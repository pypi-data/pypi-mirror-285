"""
Configuration for the test module
"""
import pytest

# Add the marks of the tests
test_marks = [
    "variable",
    "function",
    "expression",
    # Solver tests
    "opt_solver",
    # Engine tests marks
    "opt_methods"
]


def pytest_addoption(parser):
    """Create new flags for every test pack

    Args:
        parser (Parser): Pytest default
    """
    for name in test_marks:
        parser.addoption(f"--{name}",
                         action="store_true",
                         default=False,
                         help=f"run all {name} tests")


def pytest_configure(config):
    """Add new markers to tests packs

    Args:
        config (Pytest): Pytest deafault
    """
    for name in test_marks:
        config.addinivalue_line(
            "markers",
            f"{name}: mark test to run validation & behavioral test to {name}")


def pytest_collection_modifyitems(config, items):
    """Workflow for markers

    Args:
        config (Pytest): Deafault
        items (Pytest): Default
    """
    for name in test_marks:
        if config.getoption(f"--{name}"):
            skip = pytest.mark.skip(
                reason=f"test not included in '{name}' mark")
            for item in items:
                if not name in item.keywords:
                    item.add_marker(skip)
