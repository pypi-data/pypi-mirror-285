#! /usr/bin/env python3
import subprocess
import pathlib


# get the path to the home users folder
home = pathlib.Path.home()

def main(workers=1, worker_class="uvicorn.workers.UvicornWorker", bind="0.0.0.0:80", PID_FILE="PID_FILE"):
    """
    This script starts the telemetry fastapi app with uvicorn
    """
    # this basic script starts the telemetry app with gunicorn running uvicorn.
    # there's an easy entry point from the command line after this is installed

    # this scripts parent folder is 
    script_folder = pathlib.Path(__file__).parent
    subprocess.Popen(
        [
            "gunicorn", 
            "conversiontelemetry:app", 
            f"--workers {workers}",
            f"--worker-class {worker_class}",
            f"--bind {bind}",
            f"--pid {PID_FILE}"
        ],
        cwd=script_folder,
        stdin=subprocess.DEVNULL,
        stdout=open(home / "gunicorn.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True)

if __name__ == "__main__":
    main()