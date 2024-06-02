from functools import wraps
from io import BytesIO
import mysql.connector
from flask import Blueprint, send_file
from flask import request, jsonify
import pdb
from datetime import datetime
import requests
from endpoints import sql_address, backend_endpoint, frontend_endpoint
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
    # image_url = "https://i.ytimg.com/vi/nooM5L1M6UM/hqdefault.jpg"
    
    # try:
    #     # Fetch the image from the URL
    #     response = requests.get(image_url)
    #     response.raise_for_status()  # Raise an error on a bad status
    # except requests.RequestException as e:
    #     return jsonify({"error": str(e)}), 404

    # # Return the image file
    # return send_file(BytesIO(response.content), mimetype='image/png')
    return f"You have successfully verified your email! You can now log in."

@user_bp.route(prefix + '/login', methods=["POST"])
@ensure_connection
def login(conn):
    with conn.cursor(dictionary=True) as cur:
        body = request.json
        cur.execute("SELECT * FROM user WHERE phone_number = %(phoneNumber)s", body)
        row = cur.fetchone()
        if(row):
            if(row["phone_number"] == body['phoneNumber'] and check_password(row["password"], body['password'])):
                if(row["verified"]):
                    return jsonify({"id": row["id"]}), 200
                else:
                    return "User is not verified. Please verify your email.", 401
            else:
                return "Phone number or password is incorrect.", 401
        else:
            return "User does not exist.", 404
    
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

@user_bp.route(prefix + '/follow', methods=["POST"])
@ensure_connection
def follow(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("INSERT INTO follow (follower_id, following_id) VALUES (%(followerId)s, %(followingId)s)", body)
        cur.execute("UPDATE user SET follower_count = follower_count + 1 WHERE id = %(followingId)s", body)
        cur.execute("UPDATE user SET following_count = following_count + 1 WHERE id = %(followerId)s", body)
        return "200"

@user_bp.route(prefix + '/unfollow', methods=["POST"])
@ensure_connection
def unfollow(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("DELETE FROM follow WHERE follower_id = %(followerId)s AND following_id = %(followingId)s", body)
        cur.execute("UPDATE user SET follower_count = follower_count - 1 WHERE id = %(followingId)s", body)
        cur.execute("UPDATE user SET following_count = following_count - 1 WHERE id = %(followerId)s", body)
        return "200"

@user_bp.route(prefix + '/followers/<user_id>', methods=["GET"])
@ensure_connection
def get_followers(conn, user_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM follow WHERE following_id = %s", [user_id])
        rows = cur.fetchall()
        response = []
        for row in rows:
            cur.execute("SELECT * FROM user WHERE id = %s", [row["follower_id"]])
            user = cur.fetchone()
            response.append({"id": user["id"], "email": user["email"], "phoneNumber": user["phone_number"], "username": user["username"], "bio": user["bio"], "profilePicture": user["profile_picture"], "createTime": user["create_date"], "postCount": user["post_count"], "followerCount": user["follower_count"], "followingCount": user["following_count"]})
        return jsonify(response), 200
    
@user_bp.route(prefix + '/following/<user_id>', methods=["GET"])
@ensure_connection
def get_following(conn, user_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM follow WHERE follower_id = %s", [user_id])
        rows = cur.fetchall()
        response = []
        for row in rows:
            cur.execute("SELECT * FROM user WHERE id = %s", [row["following_id"]])
            user = cur.fetchone()
            response.append({"id": user["id"], "email": user["email"], "phoneNumber": user["phone_number"], "username": user["username"], "bio": user["bio"], "profilePicture": user["profile_picture"], "createTime": user["create_date"], "postCount": user["post_count"], "followerCount": user["follower_count"], "followingCount": user["following_count"]})
        return jsonify(response), 200
    
@user_bp.route(prefix + '/likedPosts/<user_id>', methods=["GET"])
@ensure_connection
def get_liked_posts(conn, user_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM liked WHERE user_id = %s", [user_id])
        rows = cur.fetchall()
        response = []
        for row in rows:
            cur.execute("SELECT * FROM post WHERE id = %s", [row["post_id"]])
            post = cur.fetchone()
            response.append({"postId": post["id"], "title": post["title"], "content": post["content"], "image": post["image"], "likeCount": post["like_count"], "commentCount": post["comment_count"], "createDate": post["create_date"]})
        return jsonify(response), 200

@user_bp.route(prefix + '/comments/<user_id>', methods=["GET"])
@ensure_connection
def get_comments(conn, user_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM comment WHERE user_id = %s", [user_id])
        comments = cur.fetchall()
        comment_tree = []

        # Create a dictionary to map comment IDs to their corresponding comments
        comment_dict = {comment["id"]: comment for comment in comments}

        for comment in comments:
            if not comment["has_parent"]:
                # If comment doesn't have a parent, it's a root comment
                comment_tree.append(comment)
            else:
                # If comment has a parent, add it to its parent's 'replies' list
                parent_id = comment["parent_id"]
                parent_comment = comment_dict[parent_id]
                if "replies" not in parent_comment:
                    parent_comment["replies"] = []
                parent_comment["replies"].append(comment)

        return jsonify(comment_tree), 200
    
