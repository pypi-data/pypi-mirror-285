import base64

import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from allspice import AllSpice
from allspice.utils import list_components
from allspice.utils.bom_generation import (
    generate_bom,
    generate_bom_for_altium,
    generate_bom_for_orcad,
)
from allspice.utils.list_components import list_components_for_altium, list_components_for_orcad
from allspice.utils.netlist_generation import generate_netlist

from .csv_snapshot_extension import CSVSnapshotExtension


@pytest.fixture(scope="session")
def port(pytestconfig):
    """Load --port command-line arg if set"""
    return pytestconfig.getoption("port")


@pytest.fixture
def instance(port, pytestconfig):
    # The None record mode is the default and is equivalent to "once"
    if pytestconfig.getoption("record_mode") in ["none", "once", None]:
        # If we're using cassettes, we don't want BOM generation to sleep
        # between requests to wait for the generated JSON to be available.
        list_components.SLEEP_FOR_GENERATED_JSON = 0

    try:
        g = AllSpice(
            f"http://localhost:{port}",
            open(".token", "r").read().strip(),
            ratelimiting=None,
        )
        print("AllSpice Hub Version: " + g.get_version())
        print("API-Token belongs to user: " + g.get_user().username)

        return g
    except Exception:
        assert False, f"AllSpice Hub could not load. Is there: \
                - an Instance running at http://localhost:{port} \
                - a Token at .token \
                    ?"


@pytest.fixture
def setup_for_generation(instance):
    repos = []

    def setup_for_generation_inner(test_name, clone_addr):
        # TODO: we should commit a smaller set of files in this repo so we don't
        #       depend on external data
        nonlocal repos

        instance.requests_post(
            "/repos/migrate",
            data={
                "clone_addr": clone_addr,
                "mirror": False,
                "repo_name": "-".join(["test", test_name]),
                "service": "git",
            },
        )

        repo = instance.get_repository(
            instance.get_user().username,
            "-".join(["test", test_name]),
        )
        repos.append(repo)
        return repo

    yield setup_for_generation_inner

    for repo in repos:
        repo.delete()


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.fixture()
def json_snapshot(snapshot):
    return snapshot.use_extension(JSONSnapshotExtension)


@pytest.fixture()
def csv_snapshot(snapshot):
    return snapshot.use_extension(CSVSnapshotExtension)


@pytest.mark.vcr
def test_bom_generation_flat(request, instance, setup_for_generation, csv_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorDemo.git",
    )

    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        # We hard-code a ref so that this test is reproducible.
        ref="95719adde8107958bf40467ee092c45b6ddaba00",
    )

    assert len(bom) == 913

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_with_odd_line_endings(
    request, instance, setup_for_generation, csv_snapshot
):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorDemo.git",
    )

    # We hard-code a ref so that this test is reproducible.
    ref = "95719adde8107958bf40467ee092c45b6ddaba00"
    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }

    new_branch_name = "-".join(["odd-line-endings", request.node.name])
    repo.add_branch(ref, new_branch_name)
    ref = new_branch_name

    files_in_repo = repo.get_git_content(ref=ref)
    prjpcb_file = next((x for x in files_in_repo if x.path == "Archimajor.PrjPcb"), None)
    assert prjpcb_file is not None

    original_prjpcb_sha = prjpcb_file.sha
    prjpcb_content = repo.get_raw_file(prjpcb_file.path, ref=ref).decode("utf-8")
    new_prjpcb_content = prjpcb_content.replace("\r\n", "\n\r")
    new_content_econded = base64.b64encode(new_prjpcb_content.encode("utf-8")).decode("utf-8")
    repo.change_file(
        "Archimajor.PrjPcb",
        original_prjpcb_sha,
        new_content_econded,
        {"branch": ref},
    )

    # Sanity check that the file was changed.
    prjpcb_content_now = repo.get_raw_file("Archimajor.PrjPcb", ref=ref).decode("utf-8")
    assert prjpcb_content_now != prjpcb_content

    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        # Note that ref here is the branch, not a commit sha as in the previous
        # test.
        ref=ref,
    )

    assert len(bom) == 913

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_grouped(request, instance, setup_for_generation, csv_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorDemo.git",
    )

    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }

    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        group_by=["part_number", "manufacturer", "description"],
        # We hard-code a ref so that this test is reproducible.
        ref="95719adde8107958bf40467ee092c45b6ddaba00",
    )

    assert len(bom) == 108

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_with_folder_hierarchy(
    request,
    instance,
    setup_for_generation,
    csv_snapshot,
):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorInFolders.git",
    )

    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        group_by=["part_number"],
        # We hard-code a ref so that this test is reproducible.
        ref="e39ecf4de0c191559f5f23478c840ac2b6676d58",
    )

    assert len(bom) == 102
    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_with_default_variant(request, instance, setup_for_generation, csv_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorVariants.git",
    )

    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        ref="916e739f3ad9d956f4e2a293542050e1df9e6f9e",
        # For the variants tests, we don't want to remove non-BOM components
        # because some of them are enabled by the variants, and we want to
        # test that they are included when required.
        remove_non_bom_components=False,
    )

    # Since we haven't specified a variant, this should have the same result
    # as generating a flat BOM. This version of archimajor has a few parts
    # removed even before the variations, so the number of parts is different.
    assert len(bom) == 975

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_with_fitted_variant(request, instance, setup_for_generation, csv_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorVariants.git",
    )

    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        ref="916e739f3ad9d956f4e2a293542050e1df9e6f9e",
        variant="Fitted",
        remove_non_bom_components=False,
    )

    # Exactly 42 rows should be removed, as that is the number of non-param
    # variations.
    assert len(bom) == 975 - 42

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_with_grouped_variant(request, instance, setup_for_generation, csv_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorVariants.git",
    )

    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        group_by=["part_number"],
        ref="916e739f3ad9d956f4e2a293542050e1df9e6f9e",
        variant="Fitted",
        remove_non_bom_components=False,
    )

    assert len(bom) == 89

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_altium_with_non_bom_components(
    request, instance, setup_for_generation, csv_snapshot
):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorDemo.git",
    )

    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        # We hard-code a ref so that this test is reproducible.
        ref="95719adde8107958bf40467ee092c45b6ddaba00",
        remove_non_bom_components=False,
    )

    assert len(bom) == 1049

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_altium_repeated_multi_part_component(
    request, instance, setup_for_generation, csv_snapshot
):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorRepeated.git",
    )
    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        ref="1bb73a0c862e156557e05876fb268ba086e9d42d",
        remove_non_bom_components=True,
    )

    assert len(bom) == 870

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_altium_repeated_multi_part_component_variant(
    request, instance, setup_for_generation, csv_snapshot
):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorRepeatedVariant.git",
    )
    attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        attributes_mapping,
        ref="3f8ddd6b5161aebc61a3ed87b665ba0a64cc6e89",
        variant="Fitted",
        remove_non_bom_components=True,
    )

    assert len(bom) == 869

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_bom_generation_orcad(request, instance, setup_for_generation, csv_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/beagleplay.git",
    )

    attributes_mapping = {
        "Name": ["_name"],
        "Description": "Description",
        "Reference designator": ["Part Reference"],
        "Manufacturer": ["Manufacturer", "MANUFACTURER"],
        "Part Number": ["Manufacturer PN", "PN"],
    }

    bom = generate_bom_for_orcad(
        instance,
        repo,
        "Design/BEAGLEPLAYV10_221227.DSN",
        attributes_mapping,
        # We hard-code a ref so that this test is reproducible.
        ref="7a59a98ae27dc4fd9e2bd8975ff90cdb44a366ea",
    )

    assert len(bom) == 870

    assert bom == csv_snapshot


@pytest.mark.vcr
def test_generate_bom(request, instance, setup_for_generation, csv_snapshot):
    # Test the one-stop API which should automatically figure out the project
    # type and call the appropriate function.
    repo = setup_for_generation(
        request.node.name + "altium",
        "https://hub.allspice.io/AllSpiceTests/ArchimajorDemo.git",
    )

    altium_attributes_mapping = {
        "description": ["PART DESCRIPTION"],
        "designator": ["Designator"],
        "manufacturer": ["Manufacturer", "MANUFACTURER"],
        "part_number": ["PART", "MANUFACTURER #"],
    }
    bom = generate_bom(
        instance,
        repo,
        "Archimajor.PrjPcb",
        altium_attributes_mapping,
        ref="95719adde8107958bf40467ee092c45b6ddaba00",
    )
    assert len(bom) == 913
    assert bom == csv_snapshot
    repo = setup_for_generation(
        request.node.name + "orcad",
        "https://hub.allspice.io/AllSpiceTests/beagleplay.git",
    )
    orcad_attributes_mapping = {
        "Name": ["_name"],
        "Description": "Description",
        "Reference designator": ["Part Reference"],
        "Manufacturer": ["Manufacturer", "MANUFACTURER"],
        "Part Number": ["Manufacturer PN", "PN"],
    }
    bom = generate_bom(
        instance,
        repo,
        "Design/BEAGLEPLAYV10_221227.DSN",
        orcad_attributes_mapping,
        ref="7a59a98ae27dc4fd9e2bd8975ff90cdb44a366ea",
    )
    assert len(bom) == 870
    assert bom == csv_snapshot


@pytest.mark.vcr
def test_orcad_components_list(request, instance, setup_for_generation, json_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/beagleplay.git",
    )

    components = list_components_for_orcad(
        instance,
        repo,
        "Design/BEAGLEPLAYV10_221227.DSN",
        # We hard-code a ref so that this test is reproducible.
        ref="7a59a98ae27dc4fd9e2bd8975ff90cdb44a366ea",
    )

    assert len(components) == 870
    assert components == json_snapshot


@pytest.mark.vcr
def test_altium_components_list(request, instance, setup_for_generation, json_snapshot):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorDemo.git",
    )

    components = list_components_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        # We hard-code a ref so that this test is reproducible.
        ref="95719adde8107958bf40467ee092c45b6ddaba00",
    )

    assert len(components) == 1061
    assert components == json_snapshot


@pytest.mark.vcr
def test_altium_components_list_with_folder_hierarchy(
    request,
    instance,
    setup_for_generation,
    json_snapshot,
):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorInFolders.git",
    )

    components = list_components_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        # We hard-code a ref so that this test is reproducible.
        ref="e39ecf4de0c191559f5f23478c840ac2b6676d58",
    )

    assert len(components) == 1049
    assert components == json_snapshot


@pytest.mark.vcr
def test_altium_components_list_with_fitted_variant(
    request,
    instance,
    setup_for_generation,
    json_snapshot,
):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorVariants.git",
    )

    components = list_components_for_altium(
        instance,
        repo,
        "Archimajor.PrjPcb",
        # We hard-code a ref so that this test is reproducible.
        ref="916e739f3ad9d956f4e2a293542050e1df9e6f9e",
        variant="Fitted",
    )

    assert len(components) == 945
    assert components == json_snapshot


@pytest.mark.vcr
def test_netlist_generation(request, instance, setup_for_generation):
    repo = setup_for_generation(
        request.node.name,
        "https://hub.allspice.io/AllSpiceTests/ArchimajorDemo.git",
    )

    netlist = generate_netlist(
        instance,
        repo,
        "Archimajor.PcbDoc",
        # We hard-code a ref so that this test is reproducible.
        ref="95719adde8107958bf40467ee092c45b6ddaba00",
    )
    assert len(netlist) == 682

    nets = list(netlist.keys())

    nets.sort()

    with open("tests/data/archimajor_netlist_expected.net", "r") as f:
        for net in nets:
            assert (net + "\n") == f.readline()
            pins_on_net = sorted(netlist[net])
            assert (" " + " ".join(pins_on_net) + "\n") == f.readline()
