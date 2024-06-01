from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime
from controller.commentController import get_comments
from sql_address import sql_address

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
        cur.execute("INSERT INTO post (topic_id, user_id, title, content, image) VALUES (%(topicId)s, %(userId)s, %(title)s, %(content)s, %(image)s)", body)
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
        return jsonify(post)

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
        return jsonify(response)



@post_bp.route(prefix + "/like/<post_id>", methods=['PUT'])
@ensure_connection
def like_post(conn, post_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE post SET like_count = like_count + 1 WHERE id = %s", (post_id,))
        return "200"
    
@post_bp.route(prefix + "/unlike/<post_id>", methods=['PUT'])
@ensure_connection
def unlike_post(conn, post_id):
    with conn.cursor() as cur:
        cur.execute("UPDATE post SET like_count = like_count - 1 WHERE id = %s", (post_id,))
        return "200"