import pytest
import filecmp
from fhirizer import mapping, utils


@pytest.fixture
def projects():
    return utils.load_ndjson("./tests/fixtures/project/projects.ndjson")


@pytest.fixture
def cases():
    return utils.load_ndjson("./tests/fixtures/case/cases.ndjson")


@pytest.fixture
def files():
    return utils.load_ndjson("./tests/fixtures/file/files.ndjson")


def test_project_key_convert(projects):
    mapping.convert_maps(name="project", in_path="./tests/fixtures/project/projects.ndjson",
                         out_path="./tests/fixtures/project/project_key_test.ndjson", verbose=True)

    assert filecmp.cmp("./tests/fixtures/project/project_key_test.ndjson", "./tests/fixtures/project/project_key.ndjson", shallow=False)
    assert projects == utils.load_ndjson("./tests/fixtures/project/projects.ndjson")


def test_case_key_convert(cases):
    mapping.convert_maps(name="case", in_path="./tests/fixtures/case/cases.ndjson",
                         out_path="./tests/fixtures/case/case_key_test.ndjson", verbose=True)

    assert filecmp.cmp("./tests/fixtures/case/case_key_test.ndjson", "./tests/fixtures/case/case_key.ndjson", shallow=False)
    assert cases == utils.load_ndjson("./tests/fixtures/case/cases.ndjson")


def test_document_reference_key_convert(files):
    mapping.convert_maps(name="file", in_path="./tests/fixtures/file/files.ndjson",
                         out_path="./tests/fixtures/file/file_key_test.ndjson", verbose=True)

    assert filecmp.cmp("./tests/fixtures/file/file_key_test.ndjson", "./tests/fixtures/file/file_key.ndjson", shallow=False)
    assert files == utils.load_ndjson("./tests/fixtures/file/files.ndjson")

