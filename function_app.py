import azure.functions as func
import logging
import sqlite3
from secret import valid_key

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION) # initialize application and assign to app variable

# Prepare connection to database

conn = sqlite3.connect(':memory:', check_same_thread=False) # so the database can stay in-memory and meet project requirements
cursor = conn.cursor()
valid_api_key = valid_key

# type statement into database to create table of products if it does not exist

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY UNIQUE,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
''')

conn.commit() # execute typed statement above in sqllite database

### Create cursor if it does not exist

# def get_connection():
#    conn = sqlite3.connect('example.db')
#    cursor = conn.cursor()
#    return conn, cursor

# Helper function that gets a connection to do operations in CRUD routes

def verify_authority(key: str): 
    if key == valid_api_key: 
        return True
    else: 
        return False

# Helper function that terminates requests 

def has_body(request: func.HttpRequest):
    try: # Check if valid json in body. Else, return with False.
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
    
    if has_body(req): # check if the function has a body
        pass
    else: 
        return func.HttpResponse("400: Bad request.", status_code=400) # Terminate request with bad 400 code
    
    # conn, cursor = get_connection() # get connection to database as well as cursor operator

    req_body = req.get_json() # get request body as json
    name = req_body.get('name')
    price = req_body.get('price')

    # get the name and price from the request

    if name and price: # check if name and price are present within body
        cursor.execute("""INSERT INTO products (name, price) VALUES (?, ?)""", (name, price)) # type insert to prepare write
        conn.commit() # commit write
        new_id = cursor.lastrowid
        # conn.close() # close connection to avert database troubles
        logging.info(f"CREATE request successful. Item added to database.")
        return func.HttpResponse(f"201: CREATE request successful. Item {name} with price of {price} added to database. Item ID of the item you just created is {new_id}.", status_code=201)
    else:
        # conn.close() # close connection even after failure
        return func.HttpResponse("400: Bad request.", status_code=400) # Malformed request or database error message
    
@app.route(route = "update_item") # UPDATE an item
def update_item (req: func.HttpRequest) -> func.HttpResponse:

    provided_key = req.headers.get('api_key')

    if verify_authority(provided_key):
        pass
    else: 
        return func.HttpResponse("401: Unauthorized access.", status_code=401) # Unauthorized

    if has_body(req): # check if the function has a body
        pass
    else: 
        return func.HttpResponse("400: Bad request.", status_code=400) # Terminate request with bad 400 code
    
    # conn, cursor = get_connection() # get connection to database as well as cursor operator

    req_body = req.get_json() # get request body as json
    name = req_body.get('name')
    price = req_body.get('price')
    provided_id = req_body.get('id')

    if name and price and provided_id: # check if all three required json values are provided
        try: 
            cursor.execute('''
            UPDATE products
            SET name = ?,
                price = ?
            WHERE id = ?
            ''', (name, price, provided_id))
            conn.commit()
            # conn.close() # close connection to avert database troubles
            return func.HttpResponse(f"200: Successfully added {name} with price {price} at id {provided_id}.", status_code=200) # Successfully submitted update
        except sqlite3.Error as e: 
            # conn.close() # close connection to avert database troubles
            return func.HttpResponse(f"400: Bad request. Error log below {e}.", status_code=400) # Terminate request with bad 400 code
            # this is meant to come up when the database identifies that there is no value to update
    
    else: 
        # conn.close() # close connection to avert database troubles
        return func.HttpResponse("400: Bad request.", status_code=400) # Malformed request or database error message
    
@app.route(route = "delete_item") # UPDATE an item
def delete_item (req: func.HttpRequest) -> func.HttpResponse:

    provided_key = req.headers.get('api_key')

    if verify_authority(provided_key):
        pass
    else: 
        return func.HttpResponse("401: Unauthorized access.", status_code=401) # Unauthorized

    if has_body(req): # check if the function has a body
        pass
    else: 
        return func.HttpResponse("400: Bad request.", status_code=400) # Terminate request with bad 400 code
    
    # conn, cursor = get_connection() # get connection to database as well as cursor operator

    req_body = req.get_json() # get request body as json
    provided_id = req_body.get('id')

    if provided_id: # check if all three required json values are provided
        try: 
            cursor.execute('''
            DELETE FROM products
            WHERE id = ?
            ''', (provided_id,))
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

    if verify_authority(provided_key):
        pass
    else: 
        return func.HttpResponse("401: Unauthorized access.", status_code=401) # Unauthorized

    if has_body(req): # check if the function has a body
        pass
    else: 
        return func.HttpResponse("400: Bad request.", status_code=400) # Terminate request with bad 400 code
    
    # conn, cursor = get_connection() # get connection to database as well as cursor operator

    cursor.execute("SELECT * FROM products ORDER BY id") # type select request
    unprocessed_data = cursor.fetchall() # execute on select request and return as output
    
    # construct empty dictionary to add data to 

    output = prepare_data(unprocessed_data)

    # conn.close() # close connection to avert database troubles
    logging.info(f"Current list of items: {output}")
    return func.HttpResponse(f"200: Current list of items: {output}", status_code=201)