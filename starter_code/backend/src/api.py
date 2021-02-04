import os
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
 initialize the datbase

'''
db_drop_and_create_all()

## ROUTES
'''

    GET / all the drinks from db


'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    
    try:
      drinks = Drink.query.all()

      return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }),200
    except:

      abort(404)

'''

    GET /drinks-detail
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):

    # Get all the drinks from db
    drinks = Drink.query.all()
    # convert Drinks to long drinks
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }), 200




'''
@TODO implement endpoint
    POST /drinks
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    # Get the body 
    body = request.get_json()
    try:
        # create new Drink
        drink = Drink()
        drink.title = body['title']
        drink.recipe = json.dumps(body['recipe'])
        # insert function
        drink.insert()

    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})

'''
    PATCH /drinks/<id>
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    # Get the body
    req = request.get_json()

    # Get the Drink with requested Id (only one)
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:

        title = req.get('title')
        recipe = req.get('recipe')

        # check if the title is the one is updated
        if title:
            drink.title = title

        # check if the recipe is the one is updated
        if recipe:
            drink.recipe = json.dumps(recipe)

        # update the drink
        drink.update()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200



'''
    DELETE /drinks/<id>
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    # Get the Drink with requested Id
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    # if no drink with given id abort
    if not drink:
        abort(404)

    try:
        # delete function
        drink.delete()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'delete': id}), 200


## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    
    }), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    } , 401)

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
    }, 405)

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }, 500)

@app.errorhandler(AuthError)
def auth_error(error):
    print(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code