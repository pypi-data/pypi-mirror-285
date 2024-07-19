from deltalake_tools.helpers.utils import get_version_from_pyproject

def test_get_version_from_pyproject():
    version = get_version_from_pyproject()
    assert version is not None, "Version should not be None"

