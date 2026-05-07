import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).parent.parent / "pyproject.toml"

_REQUIRED_FIELDS = ["name", "version", "description", "readme", "license", "authors", "requires-python", "dependencies"]


def _project() -> dict:
    with open(PYPROJECT, "rb") as f:
        return tomllib.load(f)["project"]


def test_pyproject_exists():
    assert PYPROJECT.exists()


def test_required_fields_present():
    project = _project()
    missing = [f for f in _REQUIRED_FIELDS if f not in project]
    assert not missing, f"pyproject.toml missing fields: {missing}"


def test_fields_non_empty():
    project = _project()
    for field in _REQUIRED_FIELDS:
        val = project.get(field)
        assert val not in (None, "", [], {}), f"pyproject.toml field '{field}' is empty"


def test_python_version_constraint():
    project = _project()
    requires = project.get("requires-python", "")
    assert ">=" in requires, f"requires-python should have a >= constraint, got: {requires!r}"


def test_version_format():
    project = _project()
    version = project.get("version", "")
    parts = version.split(".")
    assert len(parts) >= 2 and all(p.isdigit() for p in parts), f"version looks malformed: {version!r}"
