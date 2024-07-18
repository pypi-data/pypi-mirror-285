# to run this application start your virtual environment and execute
# uvicorn telemetry:app --reload
import os
import dotenv
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime

# telemetry config file location
telemetry_config = os.path.join(os.path.expanduser("~"), ".telemetry.env")

# load the environment variables from the users home dire telemetry.env file
dotenv.load_dotenv(telemetry_config, override=True)


def get_database():
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    # CONNECTION_STRING = "mongodb://127.0.0.1/telemetry"
    CONNECTION_STRING = os.environ.get("CONNECTION_STRING", "127.0.0.1:27417")

    client = MongoClient(CONNECTION_STRING)

    return client['telemetry']


db_name = get_database()
collection_name = db_name['telemetry']


class Item(BaseModel):
    timestamp: str = ''
    client_addr: str = ''
    description: str = ''
    content: dict = {}


app = FastAPI()

# set up limiters so that we don't get spammed to death, limiter can be disabled be setting 
# the environment variable TELEMETRY_RATE_LIMITING to False
limiter = Limiter(key_func=get_remote_address)
if os.environ.get("TELEMETRY_RATE_LIMITING", "") == "False" or os.environ.get("TELEMETRY_RATE_LIMITING", "") == "":
    limiter.enabled = False
if os.environ.get("TELEMETRY_RATE_LIMIT", "") == "True":
    limiter.enabled = True

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# note the route decorator must be above the limit decorator, not below it
@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    return {"message": "This is a very basic api"}


# use fastapi to accept a json via a post request
@app.post("/telemetry/")
@limiter.limit("5/minute")
async def create_item(request: Request):
    # collect the ip address of the incoming request
    # and update the item.dict with the request ip address and host name    
    data = await request.json()
    item = Item()
    item.timestamp = datetime.now().isoformat()
    item.client_addr = request.client.host
    item.content = data
    # insert the json into the mongodb collection
    collection_name.insert_one(item.dict())
    return item


@app.get("/check/")
async def check(request: Request):
    cursor = list(collection_name.find({}))
    for i, item in enumerate(cursor):
        # this is poor man's serialization b/c the bson.objectid.ObjectId is not serializable
        # with any built in methods
        item['_id'] = str(item['_id'])
        cursor[i] = item
    return cursor
