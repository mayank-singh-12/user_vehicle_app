from flask import render_template
from application.database import get_db, close_db, init_db

from application.model import get_user_reservations


def register_routes(app):
    @app.route("/")
    def home():
        user_reservation_data = get_user_reservations(1)
        return render_template("index.html",user_reservation_data=user_reservation_data)
