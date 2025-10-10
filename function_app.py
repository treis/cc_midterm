import azure.functions as func
import logging
import sqlite3
import json
from secret import valid_key

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Prepare connection to database
conn = sqlite3.connect(':memory:', check_same_thread=False)
cursor = conn.cursor()
valid_api_key = valid_key

# Create table if it does not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY UNIQUE,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
''')
conn.commit()

# Helper functions
def verify_authority(key: str) -> bool:
    if key == valid_api_key:
        return True
    else: 
        return False

def has_body(request: func.HttpRequest):
    try:
        request.get_json()
        return True
    except:
        return False

# Helper functions that checks if there is a json body 

def prepare_data(provided_data: list): # more specifically, a list of tuples

    master_json = {}

    for item_tuple in provided_data: 
        id = item_tuple[0]
        name = item_tuple[1]
        price = item_tuple[2]

        per_item_json = {'name': name,
                         'price': price
        }

        master_json[id] = per_item_json

    return master_json

# Helper function that prepares responses from sqllite 3 into a json response 

@app.route(route = "create_item") # CREATE an item 
def create_item (req: func.HttpRequest) -> func.HttpResponse:

    provided_key = req.headers.get('api_key') # get api key provided in request

    if verify_authority(provided_key): # check if the user is authorized based on provided request api key parameter
        pass
    else: 
        return func.HttpResponse("401: Unauthorized access.", status_code=401) # Unauthorized
    
    if not has_body(req):
        return json_response({"error": "Bad request"}, 400)
    
    req_body = req.get_json()
    name = req_body.get('name')
    price = req_body.get('price')

    if name and price:
        cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        new_id = cursor.lastrowid
        logging.info(f"CREATE request successful. Item added to database.")
        return json_response({
            "message": "Item created",
            "id": new_id,
            "name": name,
            "price": price
        }, 201)
    else:
        return json_response({"error": "Bad request"}, 400)

# UPDATE
@app.route(route="update_item")
def update_item(req: func.HttpRequest) -> func.HttpResponse:
    provided_key = req.headers.get('api_key')
    if not verify_authority(provided_key):
        return json_response({"error": "Unauthorized access"}, 401)
    
    if not has_body(req):
        return json_response({"error": "Bad request"}, 400)

    req_body = req.get_json()
    name = req_body.get('name')
    price = req_body.get('price')
    provided_id = req_body.get('id')

    if name and price and provided_id:
        try:
            cursor.execute('''
                UPDATE products
                SET name = ?, price = ?
                WHERE id = ?
            ''', (name, price, provided_id))
            conn.commit()
            return json_response({
                "message": "Item updated",
                "id": provided_id,
                "name": name,
                "price": price
            }, 200)
        except sqlite3.Error as e:
            return json_response({"error": str(e)}, 400)
    else:
        return json_response({"error": "Bad request"}, 400)

# DELETE
@app.route(route="delete_item")
def delete_item(req: func.HttpRequest) -> func.HttpResponse:
    provided_key = req.headers.get('api_key')
    if not verify_authority(provided_key):
        return json_response({"error": "Unauthorized access"}, 401)
    
    if not has_body(req):
        return json_response({"error": "Bad request"}, 400)

    req_body = req.get_json()
    provided_id = req_body.get('id')

    if provided_id:
        try:
            cursor.execute('DELETE FROM products WHERE id = ?', (provided_id,))
            conn.commit()
            # conn.close() # close connection to avert database troubles
            return func.HttpResponse(f"Successfully deleted item at id {provided_id}.", status_code=200) # Successfully submitted update
        except sqlite3.Error as e: 
            # conn.close() # close connection to avert database troubles
            return func.HttpResponse(f"400: Bad request. Error log below {e}.", status_code=400) # Terminate request with bad 400 code
            # this is meant to come up when the database identifies that there is no value to update
    else: 
        # conn.close() # close connection to avert database troubles
        return func.HttpResponse("400: Bad request.", status_code=400) # Malformed request or database error message
    
@app.route(route = "read_item") # UPDATE an item
def read_item (req: func.HttpRequest) -> func.HttpResponse:

    provided_key = req.headers.get('api_key')
    if not verify_authority(provided_key):
        return json_response({"error": "Unauthorized access"}, 401)
    
    cursor.execute("SELECT * FROM products ORDER BY id")
    unprocessed_data = cursor.fetchall()
    output = prepare_data(unprocessed_data)
    logging.info(f"Current list of items: {output}")
    return json_response({"items": output}, 200)
