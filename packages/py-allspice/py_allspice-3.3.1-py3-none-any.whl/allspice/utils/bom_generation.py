# cspell:ignore jsons

from __future__ import annotations

from typing import Optional, Union

from ..allspice import AllSpice
from ..apiobject import Ref, Repository
from .list_components import (
    ComponentAttributes,
    list_components_for_altium,
    list_components_for_orcad,
)

QUANTITY_COLUMN_NAME = "Quantity"


ColumnsMapping = dict[str, list[str] | str]
BomEntry = dict[str, str]
Bom = list[BomEntry]


def generate_bom(
    allspice_client: AllSpice,
    repository: Repository,
    source_file: str,
    columns: ColumnsMapping,
    group_by: Optional[list[str]] = None,
    variant: Optional[str] = None,
    ref: Ref = "main",
    remove_non_bom_components: bool = True,
) -> Bom:
    """
    Generate a BOM for a project.

    :param allspice_client: The AllSpice client to use.
    :param repository: The repository to generate the BOM for.
    :param source_file: The path to the source file from the root of the
        repository. The source file must be a PrjPcb file for Altium projects
        and a DSN file for OrCAD projects. For example, if the source file is
        in the root of the repository and is named "Archimajor.PrjPcb", the
        path would be "Archimajor.PrjPcb"; if the source file is in a folder
        called "Schematics" and is named "Beagleplay.dsn", the path would be
        "Schematics/Beagleplay.dsn".
    :param columns: A mapping of the columns in the BOM to the attributes in the
        project. The attributes are tried in order, and the first one found is
        used as the value for that column.

        For example, if there should be a "Part Number" column in the BOM, and
        the value for that column can be in the "Part" or "MFN Part#" attributes
        in the project, the following mapping can be used:

                {
                    "Part Number": ["Part", "MFN Part#"]
                }

        In this case, the "Part" attribute will be checked first, and if it is
        not present, the "MFN Part#" attribute will be checked. If neither are
        present, the "Part Number" column in the BOM will be empty.

        Note that special attributes are added by this function depending on the
        project tool. For Altium projects, these are "_part_id", "_description",
        "_unique_id" and "_kind", which are the Library Reference, Description,
        Unique ID and Component Type respectively. For OrCAD projects, "_name"
        is added, which is the name of the component.
    :param group_by: A list of columns to group the BOM by. If this is provided,
        the BOM will be grouped by the values of these columns.
    :param variant: The variant of the project to generate the BOM for. If this
        is provided, the BOM will be generated for the specified variant. If
        this is not provided, or is None, the BOM will be generated for the
        default variant. Variants are not supported for OrCAD projects.
    :param ref: The ref, i.e. branch, commit or git ref from which to take the
        project files. Defaults to "main".
    :param remove_non_bom_components: If True, components of types that should
        not be included in the BOM will be removed. Defaults to True. Only
        applicable for Altium projects.
    :return: A list of BOM entries. Each entry is a dictionary where the key is
        a column name and the value is the value for that column.
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
            return generate_bom_for_altium(
                allspice_client,
                repository,
                source_file,
                columns,
                group_by,
                variant,
                ref,
                remove_non_bom_components,
            )
        case "orcad":
            if variant:
                raise ValueError("Variant is not supported for OrCAD projects.")

            return generate_bom_for_orcad(
                allspice_client,
                repository,
                source_file,
                columns,
                group_by,
                ref,
            )


def generate_bom_for_altium(
    allspice_client: AllSpice,
    repository: Repository,
    prjpcb_file: str,
    columns: ColumnsMapping,
    group_by: Optional[list[str]] = None,
    variant: Optional[str] = None,
    ref: Ref = "main",
    remove_non_bom_components: bool = True,
) -> Bom:
    """
    Generate a BOM for an Altium project.

    :param allspice_client: The AllSpice client to use.
    :param repository: The repository to generate the BOM for.
    :param prjpcb_file: The path to the PrjPcb project file from the root of the
        repository.
    :param columns: A mapping of the columns in the BOM to the attributes in the
        Altium project. The attributes are tried in order, and the first one
        found is used as the value for that column.

        For example, if there  should be a "Part Number" column in the BOM, and
        the value for that column can be in the "Part" or "MFN Part#" attributes
        in the Altium project, the following mapping can be used:

            {
                "Part Number": ["Part", "MFN Part#"]
            }

        In this case, the "Part" attribute will be checked first, and if it is
        not present, the "MFN Part#" attribute will be checked. If neither are
        present, the "Part Number" column in the BOM will be empty.

        Along with the attributes, four special attributes are added by this
        function: "_part_id", "_description", "_unique_id" and "_kind". These
        are the Library Reference, Description, Unique ID and Component Type
        respectively. You can use these like any other attribute in the columns
        mapping.
    :param group_by: A list of columns to group the BOM by. If this is provided,
        the BOM will be grouped by the values of these columns.
    :param ref: The ref, i.e. branch, commit or git ref from which to take the
        project files. Defaults to "main".
    :param variant: The variant of the project to generate the BOM for. If this
        is provided, the BOM will be generated for the specified variant. If
        this is not provided, or is None, the BOM will be generated for the
        default variant.
    :param remove_non_bom_components: If True, components of types that should
        not be included in the BOM will be removed. Defaults to True.
    :return: A list of BOM entries. Each entry is a dictionary where the key is
        a column name and the value is the value for that column.
    """

    allspice_client.logger.info(
        f"Generating BOM for {repository.get_full_name()=} on {ref=} using {columns=}"
    )

    if group_by is not None:
        for group_column in group_by:
            if group_column not in columns:
                raise ValueError(f"Group by column {group_column} not found in selected columns")

    components = list_components_for_altium(
        allspice_client,
        repository,
        prjpcb_file,
        variant=variant,
        ref=ref,
        combine_multi_part=True,
    )

    if remove_non_bom_components:
        components = _remove_non_bom_components(components)

    mapped_components = _map_attributes(components, columns)
    bom = _group_entries(mapped_components, group_by)

    return bom


def generate_bom_for_orcad(
    allspice_client: AllSpice,
    repository: Repository,
    dsn_path: str,
    columns: ColumnsMapping,
    group_by: Optional[list[str]] = None,
    ref: Ref = "main",
) -> Bom:
    """
    Generate a BOM for an OrCAD schematic.

    :param allspice_client: The AllSpice client to use.
    :param repository: The repository to generate the BOM for.
    :param dsn_path: The OrCAD DSN file. This can be a Content object returned
        by the AllSpice API, or a string containing the path to the file in the
        repo.
    :param columns: A mapping of the columns in the BOM to the attributes in the
        OrCAD schematic. The attributes are tried in order, and the first one
        found is used as the value for that column.

        For example, if there  should be a "Part Number" column in the BOM, and
        the value for that column can be in the "Part" or "MFN Part#" attributes
        in the OrCAD schematic, the following mapping can be used:

            {
                "Part Number": ["Part", "MFN Part#"]
            }

        In this case, the "Part" attribute will be checked first, and if it is
        not present, the "MFN Part#" attribute will be checked. If neither are
        present, the "Part Number" column in the BOM will be empty.
    :param group_by: A list of columns to group the BOM by. If this is provided,
        the BOM will be grouped by the values of these columns.
    :param ref: The ref, i.e. branch, commit or git ref from which to take the
        project files. Defaults to "main".
    :return: A list of BOM entries. Each entry is a dictionary where the key is
        a column name and the value is the value for that column.
    """

    allspice_client.logger.debug(
        f"Generating BOM for {repository.get_full_name()=} on {ref=} using {columns=}"
    )
    if group_by is not None:
        for group_column in group_by:
            if group_column not in columns:
                raise ValueError(f"Group by column {group_column} not found in selected columns")
    components = list_components_for_orcad(allspice_client, repository, dsn_path, ref)
    mapped_components = _map_attributes(components, columns)
    bom = _group_entries(mapped_components, group_by)

    return bom


def _get_first_matching_key_value(
    alternatives: Union[list[str], str],
    attributes: dict[str, str | None],
) -> Optional[str]:
    """
    Search for a series of alternative keys in a dictionary, and return the
    value of the first one found.
    """

    if isinstance(alternatives, str):
        alternatives = [alternatives]

    for alternative in alternatives:
        if alternative in attributes:
            return attributes[alternative]

    return None


def _map_attributes(
    components: list[ComponentAttributes],
    columns: dict[str, list[str]],
) -> list[BomEntry]:
    """
    Map the attributes of the components to the columns of the BOM using the
    columns mapping. This takes a component as we get it from the JSON and
    returns a dict that can be used as a BOM entry.
    """

    return [
        {
            key: str(_get_first_matching_key_value(value, component) or "")
            for key, value in columns.items()
        }
        for component in components
    ]


def _group_entries(
    components: list[BomEntry],
    group_by: list[str] | None = None,
) -> list[BomEntry]:
    """
    Group components based on a list of columns. The order of the columns in the
    list will determine the order of the grouping.

    :returns: A list of rows which can be used as the BOM.
    """

    # If grouping is off, we just add a quantity of 1 to each component and
    # return early.
    if group_by is None:
        for component in components:
            component[QUANTITY_COLUMN_NAME] = "1"
        return components

    grouped_components = {}
    for component in components:
        key = tuple(component[column] for column in group_by)
        if key in grouped_components:
            grouped_components[key].append(component)
        else:
            grouped_components[key] = [component]

    rows = []

    for components in grouped_components.values():
        row = {}
        for column in group_by:
            # The RHS here shouldn't fail as we've validated the group by
            # columns are all in the column selection.
            row[column] = components[0][column]
        non_group_by = set(components[0].keys()) - set(group_by)
        for column in non_group_by:
            # For each of the values in the non-group-by columns, we take the
            # unique values from all the components and join them with a comma.
            # This is better than taking the non-unique values and joining them
            # with a comma, because it means a user wouldn't have to group by
            # more columns than they want to.
            row[column] = ", ".join(
                # dict.fromkeys retains the insertion order; set doesn't.
                dict.fromkeys(str(component[column]) for component in components).keys()
            )
        row["Quantity"] = str(len(components))
        rows.append(row)

    return rows


def _remove_non_bom_components(components: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Filter out components of types that should not be included in the BOM.
    """

    return [
        component
        for component in components
        if component.get("_kind") not in {"NET_TIE_NO_BOM", "STANDARD_NO_BOM"}
    ]
