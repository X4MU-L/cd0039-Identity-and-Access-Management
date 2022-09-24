import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    print(drinks)
    return jsonify({
        "success": True, 
        "drinks": [drink.short() for drink in drinks]
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def get_drinks_details(payload):
    drinks = Drink.query.all()
    print(drinks)
    return jsonify({
        "success": True, 
        "drinks": [drink.long() for drink in drinks]
    }), 200



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=["POST"])
@requires_auth("post:drinks")
def post_drinks(payload):
    body = request.get_json()
    if not body:
        abort(400)
    title = body.get("title", None)
    recipe = body.get("recipe", None)
    if title and recipe:
        all_drinks = Drink.query.all()
        if title in [drink.short()["title"] for drink in all_drinks]:
            print("title exist")
            abort(406)
        added_drink = Drink(title=title,recipe=json.dumps(recipe))
        try:
            added_drink.insert()
            return jsonify({
                "success": True, 
                "drinks": [added_drink.long()]
            }), 200
        except:
            abort(500)
    else:
        abort(422)



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(payload,drink_id):
    body = request.get_json()
    if not body:
        abort(400)
    title = body.get("title")
    recipe = body.get("recipe")
    
    drink_to_patch = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink_to_patch:
        if title or recipe:
            if title:
                drink_to_patch.title = title
            if recipe:
                if isinstance(recipe, dict):
                    recipe = [recipe]
                    drink_to_patch.recipe = json.dumps(recipe)
                drink_to_patch.recipe = json.dumps(recipe)
            try:
                print(drink_to_patch)
                drink_to_patch.update()
                return jsonify({
                    "success": True, 
                    "drinks": [drink_to_patch.long()]
                }), 200
            except:
                abort(500)
        else:
            abort(400)
    else:
        abort(404)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(payload,drink_id):
    if not drink_id:
        abort(400)

    drink_to_delete = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if(drink_to_delete):
        drink_to_delete.delete()
        
        return jsonify({
            "success": True,
            "delete": drink_id,
        })
    else:
        abort(404)
# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resourses not found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

@app.errorhandler(406)
def not_acceptable(error):
    return jsonify({
        "success": False,
        "error": 406,
        "message": "Not acceptable"
    }), 406


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server error"
    }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code