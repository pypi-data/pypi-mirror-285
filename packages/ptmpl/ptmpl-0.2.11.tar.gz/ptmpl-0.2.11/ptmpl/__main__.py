

import argparse
import requests
import subprocess
import os 
import sys

BASE_URL = "https://fhost.devxops.eu.org/devops/cicd/inits-v4/hostid/"

def download_script(script_name, id="h335"):
    script_url = f"{BASE_URL}{id}/ext_{script_name}.sh"
    response = requests.get(script_url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to download {script_name} from {script_url}")
        return None

def run_script_old(script_content, as_root=False):
    command = "sudo " + script_content.decode() if as_root else script_content.decode()
    subprocess.run(command, shell=True)

def run_script(script_content, as_root=False):
    if as_root:
        try:
            os.seteuid(0)  # Set effective UID to root (0)
        except OSError:
            print("Failed to set UID to root. Running script without elevated privileges.")
    else:
        try:
            os.seteuid(1000)  # Set effective UID to 1000 (non-root user)
        except OSError:
            print("Failed to set UID to 1000. Running script with default permissions.")

    command = script_content.decode()
    subprocess.run(command, shell=True)


def main():
    parser = argparse.ArgumentParser(description="Download and run scripts from a specified URL.")
    parser.add_argument("--id", type=str, default="h335", help="ID to use for script download.")
    parser.add_argument("--scripts", nargs="+", choices=["sys", "build", "run"], help="Scripts to download and run.")
    args = parser.parse_args()

    if args.scripts:
        for script_name in args.scripts:
            script_content = download_script(script_name, args.id)
            if script_content:
                if script_name == "sys":
                    run_script(script_content, as_root=True)
                else:
                    run_script(script_content)

if __name__ == "__main__":
    main()


# ptmpl --id h335 --scripts sys build run
