"""This module provides functions to install and uninstall packages in Archlinux using pacman and paru package managers.

Functions:
- install(packages: list[str]): installs packages using pacman and paru package managers.
- uninstall(packages: list[str]) -> subprocess.CompletedProcess[bytes]: uninstalls packages using pacman package manager.
- check_executable_exists(executable: str) -> bool: checks if an executable exists in the system.
"""
import subprocess


def install(packages: list[str]):
    """
    Installs the given packages using pacman and paru AUR helper.

    Args:
        packages: A list of package names to be installed.

    Returns:
        None
    """
    pacman_packages = list(filter(_check_package_exists_in_repositories, packages))
    aur_packages = list(filter(_check_package_exists_in_aur, packages))
    pacman_process = _install_pacman(pacman_packages)
    paru_process = _install_aur(aur_packages)
    return pacman_process, paru_process


def _install_pacman(packages: list[str]):
    packages_str: str = " ".join(packages)
    install = subprocess.run(
        [
            "pkexec",
            "pacman",
            "-Syu",
            packages_str,
            "--noconfirm",
            "--needed",
        ],
        capture_output=True,
    )
    return install


def _install_aur(packages: list[str]):
    packages_str: str = " ".join(packages)
    install = subprocess.run(
        [
            "paru",
            "-Syu",
            packages_str,
            "--noconfirm",
            "--needed",
        ],
        capture_output=True,
    )
    return install


def uninstall(packages: list[str]) -> subprocess.CompletedProcess[bytes]:
    packages_exists_locally = list(filter(_check_package_exists_locally, packages))
    packages_str: str = " ".join(packages_exists_locally)
    uninstall = subprocess.run(
        [
            "pkexec",
            "pacman",
            "-Rns",
            packages_str,
            "--noconfirm",
        ],
        capture_output=True,
    )
    return uninstall


def check_executable_exists(executable: str) -> bool:
    try:
        subprocess.run(["which", executable], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def _check_package_exists_locally(package: str) -> bool:
    try:
        subprocess.run(["pacman", "-Q", package], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def _check_package_exists_in_repositories(package: str) -> bool:
    try:
        subprocess.run(["paru", "-Si", package], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def _check_package_exists_in_aur(package: str) -> bool:
    if check_executable_exists("paru"):
        try:
            subprocess.run(["paru", "-Si", package], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    raise RuntimeError("Paru is not installed")
