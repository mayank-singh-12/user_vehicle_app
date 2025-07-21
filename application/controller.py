from flask import render_template, request, redirect, url_for, flash
from application.database import get_db, close_db, init_db

from application.model import (
    get_user_reservations,
    get_available_parking_lots,
    get_lot_data,
    book_parking_spot,
    spot_detail_for_release,
    commit_spot_release,
)

user = {"id": 1}


def register_routes(app):
    @app.route("/")
    def home():
        user = {"id": 1}
        user_reservation_data = get_user_reservations(user["id"])
        available_parking_lots = get_available_parking_lots()
        return render_template(
            "index.html",
            user_reservation_data=user_reservation_data,
            available_parking_lots=available_parking_lots,
        )

    @app.route("/<int:lot_id>/spot/book", methods=["GET", "POST"])
    def book_spot(lot_id):
        if request.method == "GET":
            lot_data = get_lot_data(lot_id)
            return render_template(
                "book_spot.html", lot_data=lot_data, user_id=user["id"]
            )

        if request.method == "POST":
            data = {
                "spot_id": int(request.form.get("spot_id")),
                "user_id": int(request.form.get("user_id")),
                "vehicle_number": request.form.get("vehicle_number"),
            }
            print(data)
            booking_result = book_parking_spot(
                data["spot_id"], data["user_id"], data["vehicle_number"]
            )

            print(booking_result)

            if booking_result["success"]:
                return redirect(url_for("home"))
            else:
                return redirect(
                    url_for("book_spot", lot_id=lot_id, error=booking_result["error"])
                )

    @app.route("/<int:spot_id>/spot/release", methods=["GET", "POST"])
    def release_spot(spot_id):
        if request.method == "GET":
            result = spot_detail_for_release(spot_id)
            if result["success"]:
                spot_data = result["data"]
                return render_template("release_spot.html", spot_data=spot_data)

            return redirect(url_for("home"))

        if request.method == "POST":
            result = commit_spot_release(spot_id)
            if not result["success"]:
                print(result["error"])
                return redirect(url_for("home"))

            return redirect(url_for("home"))
