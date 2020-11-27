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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

# ROUTES
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#   GET /drinks [Permissions: All]
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# [OK] TESTED GET : https://127.0.0.1:5001/drinks
# no login required for this end point (general view)


@app.route('/drinks',methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()

        drinks_list = []
        for drink in drinks:
            drinks_list.append(drink.short())
        
        return jsonify({
                'drinks': drinks_list,
                'success': True,
            }), 200
    except:
        abort(404)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#   GET /drinks-detail [Permissions: Barista & Manager]
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


# [OK] TESTES GET : https://127.0.0.1:5001/drinks-detail


@app.route('/drinks-detail',methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()

        drinks_list = []
        for drink in drinks:
            drinks_list.append(drink.long())

        return jsonify({
            'drinks': drinks_list,
            'success': True,
        }), 200
    except:
        abort(404)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#   POST /drinks [Permissions: Manager ONLY]
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


# [OK] - TESTED - see postman example below to insert


@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drink(payload):
    try:
        body = request.get_json()
        if(body is None):
            abort(404)
        drink = Drink(
                title = body.get('title'),
                recipe =json.dumps(body.get('recipe'))
                )
        drink.insert()
        
        return jsonify({
            'drinks': drink.long(),
            'success': True,
        }), 200
    except:
        abort(422)


"""
EXAMPLE POSTMAN INSERT NEW COFFEE DRINK
POST: https://127.0.0.1:5001/drinks
OPTIONS: Body > raw[x] > JSON^
{
    "title": "expresso",
    "recipe": [{
        "color": "blue",
        "name":"mr. express",
        "parts":1
        }]
}
"""


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#   PATCH /drinks/<id> [Permissions: Manager ONLY]
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
     where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


# [OK] - POST https://127.0.0.1:5001/drinks/1


@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(payload, id):
    try:
        drink = Drink.query.filter_by(id = id).one_or_none()

        if drink is None:
            abort(404)

        body = request.get_json()
        title = body.get('title')
        recipe = json.dumps(body.get('recipe'))

        # Update with new values
        if title:
            drink.title = title
        if recipe:
            drink.recipe = recipe

        drink.update()
        
        return jsonify({
            'drinks': [drink.long()],
            'success': True,
        }), 200

    except:
        abort(422)


"""
EXAMPLE POSTMAN INSERT NEW COFFEE DRINK
POST: https://127.0.0.1:5001/drinks/1
OPTIONS: Body > raw[x] > JSON^
{
    "title": "4TH edited",
    "id": 100,
    "recipe": [{
        "color": "yellow",
        "name":"name2",
        "parts":1
        }]
}
"""


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#   DELETE /drinks/<id> [Permissions: Manager ONLY]
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
     where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# [OK] TESTED - DELETE https://127.0.0.1:5001/drinks/3


@app.route('/drinks/<int:id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,id):
    try:
        drink = Drink.query.filter_by(id = id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
        
        return jsonify({
            "delete": id,
            'success': True,
        }), 200

    except:
        abort(422)

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code
