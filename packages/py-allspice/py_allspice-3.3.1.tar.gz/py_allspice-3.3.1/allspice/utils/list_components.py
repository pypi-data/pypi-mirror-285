# cspell:ignore jsons

import configparser
import pathlib
import re
import time
from enum import Enum
from logging import Logger
from typing import Optional

from ..allspice import AllSpice
from ..apiobject import Repository
from ..exceptions import NotYetGeneratedException

SLEEP_FOR_GENERATED_JSON = 0.5
"""The amount of time to sleep between attempts to fetch generated JSON files."""

PCB_FOOTPRINT_ATTR_NAME = "PCB Footprint"

PART_REFERENCE_ATTR_NAME = "Part Reference"
"""The name of the part reference attribute in OrCAD projects."""

REPETITIONS_REGEX = re.compile(r"Repeat\(\w+,(\d+),(\d+)\)")

DESIGNATOR_COLUMN_NAME = "Designator"
"""The name of the designator attribute in Altium projects."""

# Maps a sheet name to a list of tuples, where each tuple is a child sheet and
# the number of repetitions of that child sheet in the parent sheet.
SchdocHierarchy = dict[str, list[tuple[str, int]]]
ComponentAttributes = dict[str, str | None]


class VariationKind(Enum):
    FITTED_MOD_PARAMS = 0
    NOT_FITTED = 1
    ALT_COMP = 2


def list_components(
    allspice_client: AllSpice,
    repository: Repository,
    source_file: str,
    variant: Optional[str] = None,
    ref: str = "main",
    combine_multi_part: bool = False,
) -> list[dict[str, str]]:
    """
    Get a list of all components in a schematic.

    :param client: An AllSpice client instance.
    :param repository: The repository containing the schematic.
    :param source_file: The path to the schematic file from the repo root. The
        source file must be a PrjPcb file for Altium projects and a DSN file for
        OrCAD projects. For example, if the schematic is in the folder
        "Schematics" and the file is named "example.DSN", the path would be
        "Schematics/example.DSN".
    :param variant: The variant to apply to the components. If not None, the
        components will be filtered and modified according to the variant. Only
        applies to Altium projects.
    :param ref: Optional git ref to check. This can be a commit hash, branch
        name, or tag name. Default is "main", i.e. the main branch.
    :param combine_multi_part: If True, multi-part components will be combined
        into a single component. Currently only works for Altium.
    :return: A list of all components in the schematic. Each component is a
        dictionary with the keys being the attributes of the component and the
        values being the values of the attributes. A `_name` attribute is added
        to each component to store the name of the component.
    """

    if source_file.lower().endswith(".prjpcb"):
        project_tool = "altium"
    elif source_file.lower().endswith(".dsn"):
        project_tool = "orcad"
    else:
        raise ValueError(
            "The source file must be a PrjPcb file for Altium projects or a DSN file for OrCAD "
            "projects."
        )

    match project_tool:
        case "altium":
            return list_components_for_altium(
                allspice_client,
                repository,
                source_file,
                variant=variant,
                ref=ref,
                combine_multi_part=combine_multi_part,
            )
        case "orcad":
            if variant:
                raise ValueError("Variant is not supported for OrCAD projects.")

            return list_components_for_orcad(
                allspice_client,
                repository,
                source_file,
                ref=ref,
            )


def list_components_for_altium(
    allspice_client: AllSpice,
    repository: Repository,
    prjpcb_file: str,
    variant: Optional[str] = None,
    ref: str = "main",
    combine_multi_part: bool = False,
) -> list[dict[str, str]]:
    """
    Get a list of all components in an Altium project.

    :param client: An AllSpice client instance.
    :param repository: The repository containing the Altium project.
    :param prjpcb_file: The path to the PrjPcb file from the repo root. For
        example, if the PrjPcb file is in the folder "Project" and the file
        is named "example.prjpcb", the path would be "Project/example.prjpcb".
    :param variant: The variant to apply to the components. If not None, the
        components will be filtered and modified according to the variant.
    :param ref: Optional git ref to check. This can be a commit hash, branch
        name, or tag name. Default is "main", i.e. the main branch.
    :param combine_multi_part: If True, multi-part components will be combined
        into a single component.
    :return: A list of all components in the Altium project. Each component is
        a dictionary with the keys being the attributes of the component and the
        values being the values of the attributes. Additionally, `_part_id`,
        `_description`, `_unique_id`, and `_kind` attributes are added to each
        component to store the Library Reference, Description, Unique ID, and
        Component Type respectively.
    """

    allspice_client.logger.info(f"Fetching {prjpcb_file=}")

    # Altium adds the Byte Order Mark to UTF-8 files, so we need to decode the
    # file content with utf-8-sig to remove it.
    prjpcb_file_contents = repository.get_raw_file(prjpcb_file, ref=ref).decode("utf-8-sig")

    prjpcb_ini = configparser.ConfigParser()
    prjpcb_ini.read_string(prjpcb_file_contents)

    if variant is not None:
        try:
            variant_details = _extract_variations(variant, prjpcb_ini)
        except ValueError:
            raise ValueError(
                f"Variant {variant} not found in PrjPcb file. "
                "Please check the name of the variant."
            )

    schdoc_files_in_proj = _extract_schdoc_list_from_prjpcb(prjpcb_ini)
    allspice_client.logger.info("Found %d SchDoc files", len(schdoc_files_in_proj))

    schdoc_jsons = {
        schdoc_file: _fetch_generated_json(
            repository,
            _resolve_prjpcb_relative_path(schdoc_file, prjpcb_file),
            ref,
        )
        for schdoc_file in schdoc_files_in_proj
    }
    schdoc_entries = {
        schdoc_file: [value for value in schdoc_json.values() if isinstance(value, dict)]
        for schdoc_file, schdoc_json in schdoc_jsons.items()
    }
    schdoc_refs = {
        schdoc_file: [entry for entry in entries if entry.get("type") == "SheetRef"]
        for schdoc_file, entries in schdoc_entries.items()
    }
    independent_sheets, hierarchy = _build_schdoc_hierarchy(schdoc_refs)

    components = []

    for independent_sheet in independent_sheets:
        components.extend(
            _extract_components(
                independent_sheet,
                schdoc_entries,
                hierarchy,
            )
        )

    if combine_multi_part:
        # Multi part components must be combined *after* we've processed
        # repetitions and before we apply variations. This is because each
        # repetition of a multi-part component is treated as a separate
        # component, and they can be present across sheets. We need to combine
        # them into a single component before applying variations, as Altium
        # variations will apply to the combined component.
        components = _combine_multi_part_components_for_altium(components)

    if variant is not None:
        components = _apply_variations(components, variant_details, allspice_client.logger)

    return components


def list_components_for_orcad(
    allspice_client: AllSpice,
    repository: Repository,
    dsn_path: str,
    ref: str = "main",
) -> list[dict[str, str]]:
    """
    Get a list of all components in an OrCAD DSN schematic.

    :param client: An AllSpice client instance.
    :param repository: The repository containing the OrCAD schematic.
    :param dsn_path: The path to the OrCAD DSN file from the repo root. For
        example, if the schematic is in the folder "Schematics" and the file
        is named "example.dsn", the path would be "Schematics/example.dsn".
    :param ref: Optional git ref to check. This can be a commit hash, branch
        name, or tag name. Default is "main", i.e. the main branch.
    :return: A list of all components in the OrCAD schematic. Each component is
        a dictionary with the keys being the attributes of the component and the
        values being the values of the attributes. A `_name` attribute is added
        to each component to store the name of the component.
    """

    allspice_client.logger.debug(
        f"Listing components in {dsn_path=} from {repository.get_full_name()} on {ref=}"
    )

    # Get the generated JSON for the schematic.
    dsn_json = _fetch_generated_json(repository, dsn_path, ref)
    pages = dsn_json["pages"]
    components = []

    for page in pages:
        for component in page["components"].values():
            component_attributes = {}
            component_attributes["_name"] = component["name"]
            for attribute in component["attributes"].values():
                component_attributes[attribute["name"]] = attribute["value"]
            components.append(component_attributes)

    return components


def _fetch_generated_json(repo: Repository, file_path: str, ref: str) -> dict:
    attempts = 0
    while attempts < 5:
        try:
            return repo.get_generated_json(file_path, ref=ref)
        except NotYetGeneratedException:
            time.sleep(SLEEP_FOR_GENERATED_JSON)

    raise TimeoutError(f"Failed to fetch JSON for {file_path} after 5 attempts.")


def _extract_schdoc_list_from_prjpcb(prjpcb_ini: configparser.ConfigParser) -> set[str]:
    """
    Get a list of SchDoc files from a PrjPcb file.
    """

    return {
        section["DocumentPath"]
        for (_, section) in prjpcb_ini.items()
        if "DocumentPath" in section and section["DocumentPath"].endswith(".SchDoc")
    }


def _resolve_prjpcb_relative_path(schdoc_path: str, prjpcb_path: str) -> str:
    """
    Convert a relative path to the SchDoc file to an absolute path from the git
    root based on the path to the PrjPcb file.
    """

    # The paths in the PrjPcb file are Windows paths, and ASH will store the
    # paths as Posix paths. We need to resolve the SchDoc path relative to the
    # PrjPcb path (which is a Posix Path, since it is from ASH), and then
    # convert the result into a posix path as a string for use in ASH.
    schdoc = pathlib.PureWindowsPath(schdoc_path)
    prjpcb = pathlib.PurePosixPath(prjpcb_path)
    return (prjpcb.parent / schdoc).as_posix()


def _build_schdoc_hierarchy(
    sheets_to_refs: dict[str, list[dict]],
) -> tuple[set[str], SchdocHierarchy]:
    """
    Build a hierarchy of sheets from a mapping of sheet names to the references
    of their children.

    The output of this function is a tuple of two values:

    1. A set of "independent" sheets, which can be taken to be roots of the
    hierarchy.

    2. A mapping of each sheet that has children to a list of tuples, where each
    tuple is a child sheet and the number of repetitions of that child sheet in
    the parent sheet. If a sheet has no children and is not a child of any other
    sheet, it will be mapped to an empty list.
    """

    hierarchy = {}

    # We start by assuming all sheets are independent.
    independent_sheets = set(sheets_to_refs.keys())
    # This is what we'll use to compare with the sheet names in repetitions.
    sheet_names_downcased = {sheet.lower(): sheet for sheet in independent_sheets}

    for parent_sheet, refs in sheets_to_refs.items():
        if not refs or len(refs) == 0:
            continue

        repetitions = _extract_repetitions(refs)
        for child_sheet, count in repetitions.items():
            child_path = _resolve_child_relative_path(child_sheet, parent_sheet)
            child_name = sheet_names_downcased[child_path.lower()]
            if parent_sheet in hierarchy:
                hierarchy[parent_sheet].append((child_name, count))
            else:
                hierarchy[parent_sheet] = [(child_name, count)]
            independent_sheets.discard(child_name)

    return (independent_sheets, hierarchy)


def _resolve_child_relative_path(child_path: str, parent_path: str) -> str:
    """
    Converts a relative path in a sheet ref to a relative path from the prjpcb
    file.
    """

    child = pathlib.PureWindowsPath(child_path)
    parent = pathlib.PureWindowsPath(parent_path)

    return str(parent.parent / child)


def _extract_repetitions(sheet_refs: list[dict]) -> dict[str, int]:
    """
    Takes a list of sheet references and returns a dictionary of each child
    sheet to the number of repetitions of that sheet in the parent sheet.
    """

    repetitions = {}
    for sheet_ref in sheet_refs:
        sheet_name = (sheet_ref.get("sheet_name", {}) or {}).get("name", "") or ""
        try:
            sheet_file_name = sheet_ref["filename"]
        except Exception:
            raise ValueError(f"Could not find sheet filename in {sheet_ref=}")
        if sheet_file_name is None:
            raise ValueError(
                "Sheet filename is null in for a sheet. Please check sheet references in this "
                "project for an empty file path."
            )
        if match := REPETITIONS_REGEX.search(sheet_name):
            count = int(match.group(2)) - int(match.group(1)) + 1
            if sheet_file_name in repetitions:
                repetitions[sheet_file_name] += count
            else:
                repetitions[sheet_file_name] = count
        else:
            if sheet_file_name in repetitions:
                repetitions[sheet_file_name] += 1
            else:
                repetitions[sheet_file_name] = 1
    return repetitions


def _component_attributes(component: dict) -> ComponentAttributes:
    """
    Extract the attributes of a component into a dict.

    This also adds two properties of the component that are not attributes into
    the dict.
    """

    attributes = {}

    for key, value in component["attributes"].items():
        attributes[key] = value["text"]

    # The designator attribute has a `value` key which contains the unchanged
    # designator from the schematic file. This is useful when combining multi-
    # part components.
    attributes["_logical_designator"] = component["attributes"][DESIGNATOR_COLUMN_NAME]["value"]

    if "part_id" in component:
        attributes["_part_id"] = component["part_id"]
    if "description" in component:
        attributes["_description"] = component["description"]
    if "unique_id" in component:
        attributes["_unique_id"] = component["unique_id"]
    if "kind" in component:
        attributes["_kind"] = component["kind"]
    if "part_count" in component:
        attributes["_part_count"] = component["part_count"]
        attributes["_current_part_id"] = component["current_part_id"]

    return attributes


def _letters_for_repetition(rep: int) -> str:
    """
    Generate the letter suffix for a repetition number. If the repetition is
    more than 26, the suffix will be a combination of letters.
    """

    first = ord("A")
    suffix = ""

    while rep > 0:
        u = (rep - 1) % 26
        letter = chr(u + first)
        suffix = letter + suffix
        rep = (rep - u) // 26

    return suffix


def _append_designator_letters(
    component_attributes: ComponentAttributes,
    repetitions: int,
) -> list[ComponentAttributes]:
    """
    Append a letter to the designator of each component in a list of components
    based on the number of repetitions of each component in the parent sheet.
    """

    if repetitions == 1:
        return [component_attributes]

    try:
        designator = component_attributes[DESIGNATOR_COLUMN_NAME]
        logical_designator = component_attributes["_logical_designator"]
    except KeyError:
        raise ValueError(f"Designator not found in {component_attributes=}")

    if designator is None:
        return [component_attributes] * repetitions

    return [
        {
            **component_attributes,
            DESIGNATOR_COLUMN_NAME: f"{designator}{_letters_for_repetition(i)}",
            # The designator value should also get the page ordinal, because
            # each time the page is repeated we're dealing with a different
            # component.
            "_logical_designator": f"{logical_designator}{_letters_for_repetition(i)}",
        }
        for i in range(1, repetitions + 1)
    ]


def _extract_components(
    sheet_name: str,
    sheets_to_entries: dict[str, list[dict]],
    hierarchy: SchdocHierarchy,
) -> list[ComponentAttributes]:
    components = []
    if sheet_name not in sheets_to_entries:
        return components

    for entry in sheets_to_entries[sheet_name]:
        if entry["type"] != "Component":
            continue

        component = _component_attributes(entry)
        components.append(component)

    if sheet_name not in hierarchy:
        return components

    for child_sheet, count in hierarchy[sheet_name]:
        child_components = _extract_components(child_sheet, sheets_to_entries, hierarchy)
        if count > 1:
            for component in child_components:
                components.extend(_append_designator_letters(component, count))
        else:
            components.extend(child_components)

    return components


def _combine_multi_part_components_for_altium(
    components: list[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Combine multi-part Altium components into a single component.

    Altium multi-part components can be distinguished by the `_part_count` and
    `_current_part_id` attributes being present, which respectively store the
    total number of parts and the current part number. If that is the case, the
    `_logical_designator` attribute ties together the different parts of the
    component.
    """

    combined_components = []
    multi_part_components_by_designator = {}

    for component in components:
        if "_part_count" in component and "_current_part_id" in component:
            designator = component["_logical_designator"]
            multi_part_components_by_designator.setdefault(designator, []).append(component)
        else:
            combined_components.append(component)

    for designator, multi_part_components in multi_part_components_by_designator.items():
        combined_component = multi_part_components[0].copy()
        combined_component[DESIGNATOR_COLUMN_NAME] = designator
        # The combined component shouldn't have the current part id, as it is
        # not any of the parts.
        del combined_component["_current_part_id"]
        combined_components.append(combined_component)

    return combined_components


def _extract_variations(
    variant: str,
    prjpcb_ini: configparser.ConfigParser,
) -> configparser.SectionProxy:
    """
    Extract the details of a variant from a PrjPcb file.
    """

    available_variants = set()

    for section in prjpcb_ini.sections():
        if section.startswith("ProjectVariant"):
            if prjpcb_ini[section].get("Description") == variant:
                return prjpcb_ini[section]
            else:
                available_variants.add(prjpcb_ini[section].get("Description"))
    raise ValueError(
        f"Variant {variant} not found in PrjPcb file.\n"
        f"Available variants: {', '.join(available_variants)}"
    )


def _apply_variations(
    components: list[dict[str, str | None]],
    variant_details: configparser.SectionProxy,
    logger: Logger,
) -> list[dict[str, str | None]]:
    """
    Apply the variations of a specific variant to the components. This should be
    done before the components are mapped to columns or grouped.

    :param components: The components to apply the variations to.
    :param variant_details: The section of the config file dealing with a
        specific variant.

    :returns: The components with the variations applied.
    """

    # Each item in the list is a pairing of (unique_id, designator), as both are
    # required to identify a component.
    components_to_remove: list[tuple[str, str]] = []
    # When patching components, the ParamVariation doesn't have the unique ID,
    # only a designator. However, ParamVariations follow the Variation entry, so
    # if we note down the last unique id we saw for a designator when going
    # through the variations, we can use that unique id when handling a param
    # variation. This dict holds that information.
    patch_component_unique_id: dict[str, str] = {}
    # The keys are the same as above, and the values are a key-value of the
    # parameter to patch and the value to patch it to.
    components_to_patch: dict[tuple[str, str], tuple[str, str]] = {}

    for key, value in variant_details.items():
        # Note that this is in lowercase, as configparser stores all keys in
        # lowercase.
        if re.match(r"variation[\d+]", key):
            variation_details = dict(details.split("=", 1) for details in value.split("|"))
            try:
                designator = variation_details["Designator"]
                # The unique ID field is a "path" separated by backslashes, and
                # the the unique id we want is the last entry in that path.
                unique_id = variation_details["UniqueId"].split("\\")[-1]
                kind = variation_details["Kind"]
            except KeyError:
                logger.warn(
                    "Designator, UniqueId, or Kind not found in details of variation "
                    f"{variation_details}; skipping this variation."
                )
                continue
            try:
                kind = VariationKind(int(variation_details["Kind"]))
            except ValueError:
                logger.warn(
                    f"Kind {variation_details['Kind']} of variation {variation_details} must be "
                    "either 0, 1 or 2; skipping this variation."
                )
                continue

            if kind == VariationKind.NOT_FITTED:
                components_to_remove.append((unique_id, designator))
            else:
                patch_component_unique_id[designator] = unique_id
        elif re.match(r"paramvariation[\d]+", key):
            variation_id = key.split("paramvariation")[-1]
            designator = variant_details[f"ParamDesignator{variation_id}"]
            variation_details = dict(details.split("=", 1) for details in value.split("|"))
            try:
                unique_id = patch_component_unique_id[designator]
            except KeyError:
                # This can happen sometimes - Altium allows param variations
                # even when the component is not fitted, so we just log and
                # ignore.
                logger.warn(
                    f"ParamVariation{variation_id} found for component {designator} either before "
                    "the corresponding Variation or for a component that is not fitted.\n"
                    "Ignoring this ParamVariation."
                )
                continue

            try:
                parameter_patch = (
                    variation_details["ParameterName"],
                    variation_details["VariantValue"],
                )
            except KeyError:
                logger.warn(
                    f"ParameterName or VariantValue not found in ParamVariation{variation_id} "
                    "details."
                )
                continue

            if (unique_id, designator) in components_to_patch:
                components_to_patch[(unique_id, designator)].append(parameter_patch)
            else:
                components_to_patch[(unique_id, designator)] = [parameter_patch]

    final_components = []

    for component in components:
        identifying_pair = (component["_unique_id"], component[DESIGNATOR_COLUMN_NAME])
        if identifying_pair in components_to_remove:
            continue

        if identifying_pair in components_to_patch:
            new_component = component.copy()
            for parameter, value in components_to_patch[identifying_pair]:
                new_component[parameter] = value
            final_components.append(new_component)
        else:
            final_components.append(component)

    return final_components
