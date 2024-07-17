import os
import toml

def get_version():
    pyproject_path = os.path.join(os.path.dirname(__file__), '../../pyproject.toml')
    pyproject_path = os.path.abspath(pyproject_path)
    if os.path.exists(pyproject_path):
        with open(pyproject_path, "r") as f:
            pyproject_data = toml.load(f)
        return pyproject_data["tool"]["poetry"]["version"]
    else:
        return "0.2.1"
