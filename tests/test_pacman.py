import subprocess


from cli.archlinux_packages import pacman


def _mock_check_package_exists_in_repositories(package) -> bool:
    return package in ["package1", "package2"]


def _mock_check_package_exists_in_aur(package) -> bool:
    return package in ["package3", "package4"]


def _setattr_subprocess_run(monkeypatch):
    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)


def _setattr_check_package_exists_in_aur(monkeypatch):
    monkeypatch.setattr(
        "cli.archlinux_packages.pacman._check_package_exists_in_aur",
        _mock_check_package_exists_in_aur,
    )


def _setattr_check_package_exists_in_repositories(monkeypatch):
    monkeypatch.setattr(
        "cli.archlinux_packages.pacman._check_package_exists_in_repositories",
        _mock_check_package_exists_in_repositories,
    )


def _monkeypath_setattr_calls(monkeypatch):
    _setattr_check_package_exists_in_repositories(monkeypatch)
    _setattr_check_package_exists_in_aur(monkeypatch)
    _setattr_subprocess_run(monkeypatch)


def mock_subprocess_run(*args, **kwargs) -> subprocess.CompletedProcess[bytes]:
    if args[0][0] == "pkexec":
        assert args[0][1:] == [
            "pacman",
            "-Syu",
            "package1 package2",
            "--noconfirm",
            "--needed",
        ]
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=b"")
    elif args[0][0] == "paru":
        assert args[0][1:] == [
            "-Syu",
            "package3 package4",
            "--noconfirm",
            "--needed",
        ]
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=b"")
    else:
        raise ValueError(f"Unexpected command: {args[0][0]}")


def test_install_package_in_repositories_and_aur(monkeypatch):
    _monkeypath_setattr_calls(monkeypatch)

    pacman_process, paru_process = pacman.install(
        ["package1", "package2", "package3", "package4"]
    )

    assert pacman_process.returncode == 0
    assert paru_process.returncode == 0


def test_install_package_not_in_repositories_and_aur(monkeypatch):
    _monkeypath_setattr_calls(monkeypatch)

    pacman_process, paru_process = pacman.install(
        ["package1", "package2", "package3", "package4", "package5"]
    )

    assert pacman_process.returncode == 0
    assert paru_process.returncode == 0
