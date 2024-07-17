import pathlib
import subprocess
import sys

INSTALLER_BINARY = "redefine_installer"


def _get_binary_name() -> str:
    if sys.platform.lower() == "win32":
        return f"{INSTALLER_BINARY}.exe"
    return INSTALLER_BINARY


def execute_from_cmd() -> int:
    try:
        redefine_installer_abs_path = (
            pathlib.Path(__file__).parent.resolve() / _get_binary_name()
        )
        if not redefine_installer_abs_path.exists():
            print("Redefine Installation Error: Redefine not running")  # noqa: T201
            return 0
    except Exception as ex:
        print(ex)  # noqa: T201
        return 0

    cmd = [redefine_installer_abs_path.as_posix()]
    cmd.extend(sys.argv[1:])

    result = subprocess.run(" ".join(cmd), shell=True, check=False)
    if (
        "session_check" in sys.argv
        or "--exit-code" in sys.argv
        or "predict" in sys.argv
    ):
        return result.returncode
    return 0
