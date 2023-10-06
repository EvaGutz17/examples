# Example requests

curl -X POST -H "Content-Type: application/json" \
 -d '{"name": "Espresso machine", "description": "Silver dual boiler machine"}' \
 http://0.0.0.0:8000/items

curl -X GET http://0.0.0.0:8000/items/1

curl -X PUT -H "Content-Type: application/json" \
 -d '{"description": "Black dual boiler machine"}' \
 http://0.0.0.0:8000/items/2

curl -X DELETE -H "Content-Type: application/json" http://0.0.0.0:8000/items/1

# Running the app

To run the app, use the following command:

    uvicorn main:app --reload
