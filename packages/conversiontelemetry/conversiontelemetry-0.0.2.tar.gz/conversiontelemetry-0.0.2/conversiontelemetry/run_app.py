#! /usr/bin/env python3
import subprocess
import pathlib
    

def main():
    """
    This script starts the telemetry fastapi app with uvicorn
    """
    # this basic script starts the telemetry app with uvicorn, we've made in into a python file so that
    # there's an easy entry point from the command line after this is installed

    # this scripts parent folder is 
    script_folder = pathlib.Path(__file__).parent
    subprocess.run("uvicorn conversiontelemetry:app --reload", shell=True, cwd=script_folder)


if __name__ == "__main__":
    main()