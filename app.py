from flask import Flask
from flask import render_template

from application.database import init_db, get_db, close_db

from application.controller import register_routes

app = Flask(__name__)


@app.before_request
def before_request():
    get_db()


@app.teardown_appcontext
def teardown_db(error):
    close_db(error)


register_routes(app)

if __name__ == "__main__":
    with app.app_context():
        init_db()

    app.run(host="0.0.0.0", debug=True, port=8080)
