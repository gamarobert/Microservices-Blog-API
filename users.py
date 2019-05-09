from flask import Flask
from flask import request, url_for, g, json, jsonify
from basicauth import SubBasicAuth
from passlib.hash import sha256_crypt
import userdb as dbf
import sqlite3

app = Flask(__name__)
basic_auth = SubBasicAuth(app)
basic_auth.init_app(app)

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url
    }

    resp = jsonify(message)
    resp.status_code = 404

    return resp

@app.errorhandler(409)
def db_error(error=None):
    message = {
        'status': 409,
        'message': 'Database error: ' + request.url
    }

    resp = jsonify(message)
    resp.status_code = 409

    return resp

@app.route('/')
def root():
    pass

@app.route('/auth', methods=['GET'])
@basic_auth.required
def authenticate():
    message = { 'status': 'OK' }

    resp = jsonify(message)
    resp.status_code = 200
                
    return resp


#curl --include --verbose --request POST --header 'Content-Type: application/json' --data '{"name":"name", "email":"email", "password":"password"}' http://localhost:5000/users/register_user/
@app.route('/users/register_user/' , methods=['POST'])
def register():
    
    name = request.json['name']
    email = request.json['email']
    password = request.json['password']
    username = email.split('@')
    
    # assigns text infront of '@' as username
    username = username[0]
    
    # hashing of password
    hashed_pw = sha256_crypt.encrypt(password)

    user = dbf.query_db("SELECT * FROM users WHERE username=?", [username], one=True)

    # if user doesnt exists
    if request.method == 'POST' and user is None:
        cur = dbf.get_db().cursor()
        db = dbf.get_db()
        
        cur.execute("INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)", 
                    (name, username, email, hashed_pw))

        db.commit()
        cur.close()
        
        message = {
            'message': 'User successfully created!'
        }

        resp = jsonify(message)
        resp.status_code = 201

        return resp
        
    #if user already exists
    elif user is not None: 
        return db_error()

# curl --include --verbose --request DELETE --user "username" --header 'Content-Type: application/json'  http://localhost:5000/users/delete_user/<int:uid>/
@app.route('/users/delete_user/<int:uid>/', methods=['DELETE'])
# @basic_auth.required
def delete_user(uid):

    user = dbf.query_db("SELECT * FROM users WHERE uid=?", [uid], one=True)
    real_username = user['username']


    if request.method == 'DELETE':
        cur = dbf.get_db().cursor()
        db = dbf.get_db()
        cur.execute("DELETE FROM users WHERE uid=?", [uid])

        db.commit()
        cur.close()

        message = {
            'message': 'User ' + user['username'] +' successfully deleted.'
        }

        resp = jsonify(message)
        resp.status_code = 200
        
        return resp
    
    elif user is None:
        return db_error()
    

# curl --include --verbose --header 'Content-Type: application/json' --user "username" --data '{"password": "editedpassword"}' http://localhost:5000/users/edit_password/<int:uid>/
@app.route('/users/edit_password/<int:uid>/', methods=['POST'])
# @basic_auth.required
def edit_password(uid):

    user = dbf.query_db("SELECT * FROM users WHERE uid=?", [uid], one=True)

    if user is not None:

        password = request.json['password']
        hashed_pw = sha256_crypt.encrypt(password)

        if request.method == 'POST':
            cur = dbf.get_db().cursor()
            db = dbf.get_db()

            cur.execute("UPDATE users SET password=? WHERE uid=?", 
                        (hashed_pw, uid))
            db.commit()
            cur.close()

            message = {
                'message': 'Password updated!'
            }

            resp = jsonify(message)
            resp.status_code = 201

            return resp

    elif user is None:
            return not_found()

