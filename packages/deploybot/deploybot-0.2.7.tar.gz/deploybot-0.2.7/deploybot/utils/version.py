import os
import toml
try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

def get_version():
    with pkg_resources.open_text('deploybot', 'pyproject.toml') as f:
        pyproject_data = toml.load(f)
    return pyproject_data["tool"]["poetry"]["version"]
