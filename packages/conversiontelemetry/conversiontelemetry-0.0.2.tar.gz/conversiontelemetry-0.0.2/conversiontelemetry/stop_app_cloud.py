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
    this_folder = pathlib.Path(__file__).parent

    # load stop_app script check locally first
    stop_app = this_folder / "stop_app"

    if stop_app.exists():
        pass
    else:
        stop_app = this_folder.parent / "scripts" / "stop_app"

    if stop_app.exists():
        subprocess.run(
            [
                "bash", 
                str(stop_app)
            ], 
            cwd=stop_app.parent)

if __name__ == "__main__":
    main()