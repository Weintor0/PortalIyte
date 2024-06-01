from flask import Flask
from controller.userController import user_bp
from controller.userController import configure
from controller.postController import post_bp
from controller.topicController import topic_bp
from controller.commentController import comment_bp
from controller.searchController import search_bp
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask_mail import Mail

app = Flask(__name__)
CORS(app)

SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Access API'
    }
)

configure(app)
app.secret_key = "AJAJNJNJSAFNSLJFWAGNGWANPGWANG"
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(user_bp)
app.register_blueprint(post_bp)
app.register_blueprint(topic_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(search_bp)

@app.before_request
def init_threads():
    app.before_request_funcs[None].remove(init_threads)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002,debug = True)