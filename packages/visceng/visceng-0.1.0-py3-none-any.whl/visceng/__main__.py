"""
ViscEng Jumpstart CLI tool. This tool is used to create a new ViscEng project easily.
"""

import argparse
import shutil
import os
from sys import exit


def main() -> int:
    """
    Main function for the ViscEng Jumpstart CLI tool.
    """
    parser = argparse.ArgumentParser(description="ViscEng Jumpstart")
    parser.add_argument("project_name", type=str, help="Name of the project")
    parser.add_argument(
        "--no-engine-bundle",
        "-n",
        action="store_true",
        help="Do not include the engine's source with the project, reference the module instead",
    )
    parser.add_argument(
        "--no-git-init",
        "-g",
        action="store_true",
        help="Do not initialize a git repository",
    )
    parser.add_argument(
        "--no-venv-init",
        "-v",
        action="store_true",
        help="Do not initialize a virtual environment",
    )
    args = parser.parse_args()
    module_path = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.join(os.getcwd(), args.project_name)
    # os.makedirs(project_path, exist_ok=True)
    try:
        os.removedirs(project_path)
    except OSError:
        pass
    shutil.copytree(os.path.join(module_path, "template"), project_path)
    if not args.no_engine_bundle:
        shutil.copytree(
            os.path.join(module_path), os.path.join(project_path, "visceng")
        )
    if not args.no_git_init:
        orig_dir = os.getcwd()
        os.chdir(project_path)
        os.system("git init")
        with open(os.path.join(project_path, ".gitignore"), "w") as f:
            f.write("env\n*__pycache__/\n*.pyc\n*.pyo\n*.pyd\n*.pyw\n*.pyz\nlogs/")
        os.system("git add .")
        os.system("git commit -m 'Initial commit'")
        os.chdir(orig_dir)
    if not args.no_venv_init:
        orig_dir = os.getcwd()
        os.chdir(project_path)
        os.system("python -m venv env")
        os.chdir(orig_dir)
    return 0


if __name__ == "__main__":
    exit(main())
