from importlib.util import find_spec

import cargoopt_recovery


def test_package_import_and_version() -> None:
    assert find_spec("cargoopt_recovery") is not None
    assert cargoopt_recovery.__version__ == "0.1.0"
