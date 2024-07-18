#! /usr/bin/env bash
# posts a payload to this api application at localhost port 8000 telemetry/ endpoint
curl -H 'Content-Type: application/json' -d '{ "what":"myjson","its":"toogood" }' -X POST 127.0.0.1:8000/telemetry/