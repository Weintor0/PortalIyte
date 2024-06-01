from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime
from endpoints import sql_address, backend_endpoint
from flask_mail import Mail, Message
from bcrypt import hashpw, gensalt, checkpw
import secrets

user_bp = Blueprint('user', __name__, url_prefix="/api")
prefix = "/user"

# Connect to the MySQL database
conn = mysql.connector.connect(
    host=sql_address,
    user='portal',
    password='portal',
    database='portal_base',
    autocommit=True,
    ssl_disabled=True  # Disable SSL
)

def ensure_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            conn.ping(reconnect=True)
        except mysql.connector.Error:
            conn.reconnect()
        return func(conn, *args, **kwargs)
    return wrapper

mail = Mail()

def configure(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'portaliyte@gmail.com'
    app.config['MAIL_PASSWORD'] = 'jztu faux imoo ufhb'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'portaliyte@gmail.com'
    mail.init_app(app)

def hash_password(password):
    return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

def generate_token():
    return secrets.token_urlsafe(16)

def send_auth_email(email, verification_token):
    msg = Message('Verify Your Email', recipients=[email])
    msg.body = f"Click the link to verify your email: {backend_endpoint}/api/user/verifyEmail/{verification_token}"
    mail.send(msg)

def check_password(hashed_password, user_password):
    return checkpw(user_password.encode('utf-8'), hashed_password.encode('utf-8'))


@user_bp.route(prefix + '/verifyEmail/<token>', methods=["GET"])
@ensure_connection
def verify_email(conn, token):
    with conn.cursor() as cur:
        cur.execute("UPDATE user SET verified = 1 WHERE verification_token = %s", (token,))
        return "200"

@user_bp.route(prefix + '/login', methods=["POST"])
@ensure_connection
def login(conn):
    with conn.cursor(dictionary=True) as cur:
        body = request.json
        cur.execute("SELECT * FROM user WHERE phone_number = %(phoneNumber)s", body)
        row = cur.fetchone()
        if(row["verified"] and row["phone_number"] == body['phoneNumber'] and check_password(row["password"], body['password'])):
            return jsonify({"id": row["id"]}), 200
        return "401"
    
@user_bp.route(prefix + '/register', methods=["POST"])
@ensure_connection
def register(conn):
    with conn.cursor() as cur:
        body = request.json
        token = generate_token()
        send_auth_email(body['email'], token)
        body['password'] = hash_password(body['password'])
        body['verificationToken'] = token
        cur.execute("INSERT INTO user (email, phone_number, password, username, follower_count, following_count, post_count, verification_token) VALUES (%(email)s, %(phoneNumber)s, %(password)s, %(username)s,0,0,0,%(verificationToken)s)", body)
        user_id = cur.lastrowid
        return jsonify({"id": user_id}), 200

@user_bp.route(prefix + '/<user_id>', methods=["GET"])
@ensure_connection
def get_user(conn, user_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM user WHERE id = %s", [user_id])
        row  = cur.fetchone()
        response = {"id": row["id"], "email": row["email"], "phoneNumber": row["phone_number"], "username": row["username"], "bio": row["bio"], "profilePicture": row["profile_picture"], "createTime": row["create_date"], "postCount": row["post_count"], "followerCount": row["follower_count"], "followingCount": row["following_count"]}
        return jsonify(response), 200

@user_bp.route(prefix + '/setBio', methods=["PUT"])
@ensure_connection
def set_bio(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE user SET bio = %(bio)s WHERE id = %(userId)s", body)
        return "200"
    
@user_bp.route(prefix + '/setProfilePicture', methods=["PUT"])
@ensure_connection
def set_profile_picture(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE user SET profile_picture = %(profilePicture)s WHERE id = %(userId)s", body)
        return "200"
