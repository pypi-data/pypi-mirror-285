from dotenv import load_dotenv, set_key
from rich.prompt import Prompt, Confirm
from pathlib import Path

def main():
    """
    This script asks the user a series of prompts that will help to setup the telemetry fastapi app.
    Namely, the user will be asked to provide the following using the richprompt module:

    1. The connection string to the mongodb database
    2. The name of the database
    3. The name of the collection
    4. The rate limiting settings (either enabled or disabled)

    It will then load or create a .env file in the current directory and set the environment variables 
    corresponding to the user's input.
    """

    # specify a custom path to the .env file, otherwise it will place in thi users home directory
    path_to_env = Prompt.ask("Enter the path to the .env file", default=f"{Path.home() / '.telemetry.env'}")

    # port to run the app on, default is 8000
    app_port = Prompt.ask("Enter the port to run the app on", default="8000")

    # get the connection string to the mongodb database
    connection_string = Prompt.ask("Enter the connection string to the mongodb database", default="127.0.0.1:27417")

    # get then ame of the mongodb user
    mongodb_user = Prompt.ask("Enter the name of the mongodb user", default="")

    # name of the database
    database_name = Prompt.ask("Enter the name of the database", default="telemetry")

    # name of the collection
    collection_name = Prompt.ask("Enter the name of the collection", default="telemetry")

    # rate limiting settings
    rate_limiting = Confirm.ask("Enable rate limiting?")
    if rate_limiting:
        rate_limiting = "True"
    if not rate_limiting:
        rate_limiting = "False"

    # load the .env file
    if not load_dotenv(path_to_env):
        Path(path_to_env).touch()
    else:
        print("The .env file already exists")
        with open(path_to_env, "r") as f:
            print(f.read())

    override_existing_env = Confirm.ask("Override existing .env file?")

    if override_existing_env:
        set_key(path_to_env, "MONGO_DB_ADDRESS", connection_string)
        set_key(path_to_env, "MONGO_DB_USER", collection_name)
        set_key(path_to_env, "MONGO_DB_NAME", database_name)
        set_key(path_to_env, "MONGO_DB_COLLECTION", collection_name)
        set_key(path_to_env, "TELEMETRY_RATE_LIMITING", rate_limiting)
        set_key(path_to_env, "APP_PORT", app_port)

if __name__ == "__main__":
    main()