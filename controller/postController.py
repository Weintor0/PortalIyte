from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime
from controller.commentController import get_comments
from endpoints import sql_address

post_bp = Blueprint('post', __name__, url_prefix="/api")
prefix = "/post"

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

@post_bp.route(prefix, methods=['POST'])
@ensure_connection
def create_post(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("INSERT INTO post (topic_id, user_id, title, content, image, like_count, comment_count) VALUES (%(topicId)s, %(userId)s, %(title)s, %(content)s, %(image)s,0,0)", body)
        cur.execute("UPDATE user SET post_count = post_count + 1 WHERE id = %(userId)s", body)
        return "200"

@post_bp.route(prefix + "/<post_id>", methods=['GET'])
@ensure_connection
def get_post(conn, post_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM post_details WHERE post_id = %s", (post_id,))
        row = cur.fetchone()
        post = {
            "postId": row["post_id"],
            "title": row["post_title"],
            "content": row["post_content"],
            "image": row["post_image"],
            "likeCount": row["post_like_count"],
            "commentCount": row["post_comment_count"],
            "createDate": row["post_create_date"],
            "user": {
                "userId": row["user_id"],
                "username": row["user_username"],
                "profilePicture": row["user_profile_picture"]
            },
            "topic": {
                "topicId": row["topic_id"],
                "name": row["topic_name"],
                "logo": row["topic_logo"]
            },
            "comments": []
        }
        post["comments"] = get_comments(row["post_id"])
        return jsonify(post), 200

@post_bp.route(prefix, methods=['GET'])
@ensure_connection
def get_posts(conn):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM post_details;")
        rows = cur.fetchall()
        response = []
        for row in rows:
            post = {
                "postId": row["post_id"],
                "title": row["post_title"],
                "content": row["post_content"],
                "image": row["post_image"],
                "likeCount": row["post_like_count"],
                "commentCount": row["post_comment_count"],
                "createDate": row["post_create_date"],
                "user": {
                    "userId": row["user_id"],
                    "username": row["user_username"],
                    "profilePicture": row["user_profile_picture"]
                },
                "topic": {
                    "topicId": row["topic_id"],
                    "name": row["topic_name"],
                    "logo": row["topic_logo"]
                },
                "comments": []
            }
            post["comments"] = get_comments(row["post_id"])
            response.append(post)
        return jsonify(response), 200


@post_bp.route(prefix + "/topic/<topic_id>", methods=['GET'])
@ensure_connection
def get_posts_by_topic(conn, topic_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM post_details WHERE topic_id = %s", (topic_id,))
        rows = cur.fetchall()
        response = []
        for row in rows:
            post = {
                "postId": row["post_id"],
                "title": row["post_title"],
                "content": row["post_content"],
                "image": row["post_image"],
                "likeCount": row["post_like_count"],
                "commentCount": row["post_comment_count"],
                "createDate": row["post_create_date"],
                "user": {
                    "userId": row["user_id"],
                    "username": row["user_username"],
                    "profilePicture": row["user_profile_picture"]
                },
                "topic": {
                    "topicId": row["topic_id"],
                    "name": row["topic_name"],
                    "logo": row["topic_logo"]
                },
                "comments": []
            }
            post["comments"] = get_comments(row["post_id"])
            response.append(post)
        return jsonify(response), 200



@post_bp.route(prefix + "/like", methods=['PUT'])
@ensure_connection
def like_post(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE post SET like_count = like_count + 1 WHERE id = %(postId)s", body)
        cur.execute("INSERT INTO liked (post_id, user_id) VALUES (%(postId)s, %(userId)s)", body)
        return "200"
    
@post_bp.route(prefix + "/unlike", methods=['PUT'])
@ensure_connection
def unlike_post(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("UPDATE post SET like_count = like_count - 1 WHERE id = %(postId)s", body)
        cur.execute("DELETE FROM liked WHERE post_id = %(postId)s AND user_id = %(userId)s", body)
        return "200"
    
@post_bp.route(prefix + "/save", methods=['POST'])
@ensure_connection
def save_post(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("INSERT INTO saved (post_id, user_id) VALUES (%(postId)s, %(userId)s)", body)
        return "200"
    
@post_bp.route(prefix + "/unsave", methods=['POST'])
@ensure_connection
def unsave_post(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("DELETE FROM saved WHERE post_id = %(postId)s AND user_id = %(userId)s", body)
        return "200"
    
@post_bp.route(prefix + "/saved/<user_id>", methods=['GET'])
@ensure_connection
def get_saved_posts(conn, user_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM saved WHERE user_id = %s", (user_id,))
        rows = cur.fetchall()
        response = []
        for row in rows:
            cur.execute("SELECT * FROM post_details WHERE id = %s", (row["post_id"],))
            post = cur.fetchone()
            post = {
                "postId": post["post_id"],
                "title": post["post_title"],
                "content": post["post_content"],
                "image": post["post_image"],
                "likeCount": post["post_like_count"],
                "commentCount": post["post_comment_count"],
                "createDate": post["post_create_date"],
                "user": {
                    "userId": post["user_id"],
                    "username": post["user_username"],
                    "profilePicture": post["user_profile_picture"]
                },
                "topic": {
                    "topicId": post["topic_id"],
                    "name": post["topic_name"],
                    "logo": post["topic_logo"]
                },
                "comments": []
            }
            post["comments"] = get_comments(post["post_id"])
            response.append(post)
        return jsonify(response), 200
    
@post_bp.route(prefix + "/mostLiked", methods=['GET'])
@ensure_connection
def get_most_liked_posts(conn):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM post_details ORDER BY post_like_count DESC LIMIT 10;")
        rows = cur.fetchall()
        response = []
        for row in rows:
            post = {
                "postId": row["post_id"],
                "title": row["post_title"],
                "content": row["post_content"],
                "image": row["post_image"],
                "likeCount": row["post_like_count"],
                "commentCount": row["post_comment_count"],
                "createDate": row["post_create_date"],
                "user": {
                    "userId": row["user_id"],
                    "username": row["user_username"],
                    "profilePicture": row["user_profile_picture"]
                },
                "topic": {
                    "topicId": row["topic_id"],
                    "name": row["topic_name"],
                    "logo": row["topic_logo"]
                },
                "comments": []
            }
            post["comments"] = get_comments(row["post_id"])
            response.append(post)
        return jsonify(response), 200