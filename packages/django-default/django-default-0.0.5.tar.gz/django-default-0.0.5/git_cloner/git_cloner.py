import os
import shutil
import subprocess
import tempfile
import time

import colorama
from alive_progress import alive_bar
from colorama import Fore, Style

colorama.init()


def make_files_writable(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            os.chmod(filepath, 0o777)
        for name in dirs:
            os.chmod(os.path.join(root, name), 0o777)


def alive_progress_bar(duration, stages):
    total_steps = 100
    print(Fore.LIGHTMAGENTA_EX + "\nOperation started:\n" + Style.RESET_ALL)
    for stage in stages:
        print(Fore.LIGHTYELLOW_EX + f"{stage}" + Style.RESET_ALL)
        with alive_bar(total_steps, title=stage) as bar:
            for i in range(total_steps):
                time.sleep(duration / total_steps)
                bar()
        print("\n")
    print(Fore.LIGHTGREEN_EX + "Operation completed successfully!" + Style.RESET_ALL)


def clone_repo():
    repo_url = "https://github.com/JahongirHakimjonov/DjangoDefault.git"
    stages = [
        "Installing Django Default structure...",
        "Building Django Default structure...",
        "Finishing progress...",
    ]
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            print(Fore.LIGHTCYAN_EX + "\nOperation started:\n" + Style.RESET_ALL)
            alive_progress_bar(5, [stages[0]])
            subprocess.run(
                ["git", "clone", repo_url, tmp_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            git_dir_path = os.path.join(tmp_dir, ".git")
            if os.path.exists(git_dir_path):
                make_files_writable(git_dir_path)
                shutil.rmtree(git_dir_path)

            for item in os.listdir(tmp_dir):
                s_path = os.path.join(tmp_dir, item)
                d_path = os.path.join(os.getcwd(), item)

                if os.path.isdir(s_path) and os.path.exists(d_path):
                    make_files_writable(d_path)
                    shutil.rmtree(d_path)
                elif os.path.exists(d_path):
                    os.remove(d_path)

                shutil.move(s_path, d_path)

            alive_progress_bar(2, [stages[1], stages[2]])

            print(
                Fore.LIGHTGREEN_EX
                + "Django Structure successfully built !!!"
                + Style.RESET_ALL
            )
    except subprocess.CalledProcessError as e:
        print(
            Fore.LIGHTRED_EX
            + f"An error occurred while cloning the repository: {e}"
            + Style.RESET_ALL
        )
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"An error occurred: {e}" + Style.RESET_ALL)

    directory = "envs"
    source_file_name = ".env.example"
    target_file_name = ".env"

    source_file_path = os.path.join(directory, source_file_name)
    target_file_path = os.path.join(directory, target_file_name)

    if os.path.exists(source_file_path):
        os.rename(source_file_path, target_file_path)
    else:
        pass


if __name__ == "__main__":
    clone_repo()
