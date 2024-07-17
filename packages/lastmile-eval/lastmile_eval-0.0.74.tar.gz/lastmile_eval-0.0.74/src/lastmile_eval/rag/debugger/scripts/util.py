"""
Caution: Do not import any UI dependencies in this file.
This file is used to validate the UI dependencies.
If you import any UI dependencies in this file, the validation will fail to execute.
"""

import importlib.metadata
from typing import List
from packaging.requirements import Requirement


PACKAGE_NAME = "lastmile-eval"
UI_EXTRA = "ui"


def get_dependencies(package_name: str) -> List[str]:
    """
    Get the dependencies of a package. Reads the metadata of the package to get the dependencies.
    NOTE: Skips dependencies with markers

    Args:
        package_name: The name of the package.

    Returns:
        List of dependencies of the package.

    Example:
        >>> get_dependencies("lastmile-eval")
        ['numpy', 'pandas', 'python-aiconfig >=1.1.34']

    """
    try:
        metadata = importlib.metadata.metadata(package_name)
        requires_dist = metadata.get_all("Requires-Dist", [])
        # TODO: @Ankush-lastmile handle markers
        return [
            dep.split(";")[0].strip()
            for dep in requires_dist
            if ";" not in dep
        ]
    except importlib.metadata.PackageNotFoundError:
        return []


def check_dependency(requirement: str) -> bool:
    """
    Check if the dependency is installed and if the version is correct.

    Examples:
        >>> numpy -> 1.20.0
        >>> check_dependency("numpy")
        True

        >>> numpy -> 1.20.0
        >>> check_dependency("numpy >=1.20.0")
        True
        >>> numpy -> 1.19.2
        >>> check_dependency("numpy >=1.20.0")
        False
    """

    parsed_requirement = Requirement(requirement)
    package_name = parsed_requirement.name

    try:
        installed_version = importlib.metadata.version(package_name)
        return parsed_requirement.specifier.contains(installed_version)

    except importlib.metadata.PackageNotFoundError:
        return False


def check_dependencies(dependencies: list[str]) -> bool:

    for dependency in dependencies:
        is_valid = check_dependency(dependency)
        if not is_valid:
            return False
        else:
            sub_deps = get_dependencies(dependency.split(" ")[0])
            valid = check_dependencies(sub_deps)
            if not valid:
                return False
    return True


def validate_ui_dependencies():
    missing_dependencies: list[str] = []
    try:
        metadata = importlib.metadata.metadata(PACKAGE_NAME)
        requires_dist = metadata.get_all("Requires-Dist", [])

        ui_dependencies = [
            dep.split(";")[0].strip()
            for dep in requires_dist
            if f"extra == '{UI_EXTRA}'" in dep
        ]

        for dependency in ui_dependencies:
            if not check_dependencies([dependency]):
                missing_dependencies.append((dependency))
    except ModuleNotFoundError:
        # TODO: Use logger
        print(
            "Something went wrong while validating the UI dependencies. If you run into issues,"
            "Try running the following command to install the latest dependencies (make sure to include the quotes): pip install 'lastmile-eval[ui]'"
        )
    if missing_dependencies:
        error_message = "\n".join(missing_dependencies)
        raise ModuleNotFoundError(
            f"The following UI dependencies or their subdependencies are missing or have incorrect versions:\n{error_message}\n\n"
            f"To install the correct versions, run the following command (make sure to include the quotes): "
            f'pip install "lastmile-eval[ui]"'
        )


if __name__ == "__main__":
    validate_ui_dependencies()
