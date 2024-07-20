import toml

def get_version_from_pyproject():
    with open("pyproject.toml", "r") as file:
        pyproject_data = toml.load(file)
    version = pyproject_data.get("project", {}).get("version", None)
    return version

