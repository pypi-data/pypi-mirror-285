# Telemetry

This very simple app retrieves and posts json contents to a mongodb.

## Build and Install

```bash
git clone git@github.com:bendhouseart/telemetry.git
cd telemetry
poetry install
    If you receive error regarding python version, change it in pyproject.toml and run poetry lock --no-update
poetry build
pip install dist/telemetry-0.1.0.tar.gz
```

## Setup for your environment

After installing in the previous step run the `setup-telemetry` command and follow the prompt:

```bash
(telemetry-LxPB_LWP-py3.11) setup-telemetry                                          
Enter the path to the .env file (/Users/galassiae/.telemetry.env): 
Enter the connection string to the mongodb database (127.0.0.1:27417): 
Enter the name of the mongodb user (): 
Enter the name of the database (telemetry): 
Enter the name of the collection (telemetry): 
Enable rate limiting? [y/n]: n
The .env file already exists
MONGO_DB_ADDRESS='127.0.0.1:27417'
MONGO_DB_USER='telemetry'
MONGO_DB_NAME='telemetry'
MONGO_DB_COLLECTION='telemetry'
TELEMETRY_RATE_LIMITING='False'

Override existing .env file? [y/n]: y
```

## Running this app

This app can started using the `start-telemetry` command after installation via pip:

`start-telemetry`

Or it can be run directly with:

`uvicorn telemetry:app --host 0.0.0.0 --port 80`

## Post a JSON to the database

```bash
curl -H 'Content-Type: application/json' -d '{ "what":"myjson","its":"toogood" }' -X POST 127.0.0.1:8000/telemetry/
```

Additionally there are two very simple scripts that illustrate how to post and get using this app:

```bash
bash telemetry/curl_post.sh
bash telemetry/curl_get.sh
```

## Some additional notes for interacting with the mongodb directly or starting this app

start uvicorn/run this app

`uvicorn telemetry:app --host 0.0.0.0 --port 80`

to get into monash/mongodb interface run

`mongosh`

to connect to telemetry database

first show all dbs

`show dbs`

select the telemetry db for use

`use telemetry`

and to show all items in the selected telemetry db

`db.telemetry.find()`
