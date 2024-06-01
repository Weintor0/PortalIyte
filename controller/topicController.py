from functools import wraps
import mysql.connector
from flask import Blueprint
from flask import request, jsonify
import pdb
from datetime import datetime


topic_bp = Blueprint('topic', __name__, url_prefix="/api")
prefix = "/topic"

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='35.194.62.103',
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

@topic_bp.route(prefix, methods=['POST'])
@ensure_connection
def create_topic(conn):
    with conn.cursor() as cur:
        body = request.json
        cur.execute("INSERT INTO topic (name, description, logo) VALUES (%(name)s, %(description)s, %(logo)s)", body)
        return "200"
    
@topic_bp.route(prefix, methods=['GET'])
@ensure_connection
def get_topics(conn):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM topic")
        rows = cur.fetchall()
        response = []
        for row in rows:
            response.append({"id": row["id"], "name": row["name"], "description": row["description"], "logo": row["logo"]})
        return jsonify(response)
    
@topic_bp.route(prefix + "/<topic_id>", methods=['GET'])
@ensure_connection
def get_topic(conn, topic_id):
    with conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
        row = cur.fetchone()
        return jsonify({"id": row["id"], "name": row["name"], "description": row["description"], "logo": row["logo"]})