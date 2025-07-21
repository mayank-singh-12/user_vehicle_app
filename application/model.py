import sqlite3
from .database import get_db, close_db
from datetime import datetime
import math


def get_user_reservations(user_id):
    db = get_db()
    query = """
        SELECT r.id as reservation_id,
               r.parking_timestamp,
               r.leaving_timestamp,
               r.vehicle_number,
               ps.id as spot_id,
               ps.status,
               pl.id as lot_id,
               pl.prime_location_name as lot_prime_location,
               pl.pin_code as lot_pin_code,
               pl.address as lot_address,
               pl.maximum_number_of_spots
        FROM reserve_parking_spot as r
        JOIN parking_spot as ps ON r.spot_id = ps.id
        JOIN parking_lot as pl ON ps.lot_id = pl.id
        WHERE r.user_id = ?
    """
    cursor = db.execute(query, (user_id,))
    fetched_data = cursor.fetchall()

    data = []

    for row in fetched_data:
        data.append(
            {
                "lot_id": row["lot_id"],
                "spot_id": row["spot_id"],
                "address": row["lot_address"],
                "prime_location": row["lot_prime_location"],
                "vehicle_number": row["vehicle_number"],
                "park_in_time": row["parking_timestamp"],
                "park_out_time": (
                    row["leaving_timestamp"] if row["leaving_timestamp"] else None
                ),
            }
        )
    return data


def get_available_parking_lots():
    db = get_db()
    query = """
    SELECT pl.id as lot_id, 
           pl.prime_location_name as lot_prime_location, 
           pl.address as lot_address, 
           pl.price as price_per_day, 
           COUNT(ps.status) as available_slots
    FROM parking_spot as ps
    JOIN parking_lot as pl ON ps.lot_id = pl.id
    WHERE status = 'A'
    GROUP BY lot_id;
    """
    cursor = db.execute(query)
    fetched_data = cursor.fetchall()

    data = []
    for row in fetched_data:
        data.append(
            {
                "lot_id": row["lot_id"],
                "lot_prime_location": row["lot_prime_location"],
                "lot_address": row["lot_address"],
                "price_per_day": row["price_per_day"],
                "available_slots": row["available_slots"],
            }
        )
    return data


def get_lot_data(lot_id):
    db = get_db()
    query = """
    SELECT ps.id as spot_id,
           COUNT(ps.status) as available_spots,
           pl.id as lot_id,
           pl.prime_location_name as lot_prime_location,
           pl.address as lot_address,
           pl.pin_code as lot_pin_code
    FROM parking_lot as pl
    JOIN parking_spot as ps ON pl.id = ps.lot_id
    WHERE ps.status='A' AND pl.id = ?
    """
    cursor = db.execute(query, (lot_id,))
    result = cursor.fetchone()
    # print(result)
    data = {
        "lot_id": result["lot_id"],
        "spot_id": result["spot_id"],
        "lot_prime_location": result["lot_prime_location"],
        "lot_address": result["lot_address"],
        "pin_code": result["lot_pin_code"],
        "available_spots": result["available_spots"],
    }
    print(data)
    return data


def is_spot_available(spot_id):
    db = get_db()
    query = """
    SELECT status FROM parking_spot as ps WHERE ps.id = ? 
    """
    cursor = db.execute(query, (spot_id,))
    data = cursor.fetchone()
    if data is None:
        return {"success": False, "error": "Row does not exist."}
    if data["status"] == "O":
        return {
            "success": False,
            "error": "Spot was just booked by another user. Please select another available spot.",
        }
    return {"success": True, "message": "Spot is available."}


def book_parking_spot(spot_id, user_id, vehicle_number):
    print("I am here.")
    db = get_db()
    try:
        spot_check = is_spot_available(spot_id)

        if spot_check["success"]:

            query = """
            UPDATE parking_spot
            SET status = 'O'
            WHERE parking_spot.id = ?
            """
            cursor = db.execute(query, (spot_id,))
            if cursor.rowcount == 0:
                return {"success": False, "error": "Unable to set status as occupied."}

            query = """
            INSERT INTO 
            reserve_parking_spot(
                "spot_id",
                "user_id",
                "vehicle_number"
            )
            VALUES(?,?,?)
            """
            cursor = db.execute(query, (spot_id, user_id, vehicle_number))
            reservation_id = cursor.lastrowid
            if not reservation_id:
                db.rollback()
                return {"success": False, "error": "Failed to insert reservation."}

            db.commit()
            return {
                "success": True,
                "reservation_id": reservation_id,
                "spot_id": spot_id,
            }

    except Exception as e:
        db.rollback()
        return {"success": False, "error": f"Booking failed: {e}"}


def spot_detail_for_release(spot_id):
    try:
        db = get_db()
        query = """
        SELECT ps.id as spot_id,
               pl.id as lot_id,
               pl.price as price_per_day,
               rs.vehicle_number as vehicle_number,
               rs.parking_timestamp as park_in_time,
               rs.leaving_timestamp as park_out_time
        FROM parking_spot as ps
        JOIN reserve_parking_spot as rs ON rs.spot_id = ps.id
        JOIN parking_lot as pl ON ps.lot_id = pl.id
        WHERE ps.id = ? AND rs.leaving_timestamp IS NULL
        """
        cursor = db.execute(query, (spot_id,))
        result = cursor.fetchone()
        if result is None:
            return {"success": False, "error": "Unable to fetch data."}

        data = {
            "spot_id": result["spot_id"],
            "lot_id": result["lot_id"],
            "price_per_day": result["price_per_day"],
            "vehicle_number": result["vehicle_number"],
            "park_in_time": result["park_in_time"],
        }
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": f"{e}"}


def commit_spot_release(spot_id):
    db = get_db()
    try:
        spot_data = spot_detail_for_release(spot_id)

        query = """
        UPDATE parking_spot
        SET status='A'
        WHERE id = ?
        """
        cursor = db.execute(query, (spot_id,))
        if cursor.rowcount == 0:
            return {"success": False, "error": "Spot not present."}

        query = """
        UPDATE reserve_parking_spot
        SET leaving_timestamp = ?
        WHERE spot_id = ? AND leaving_timestamp IS NULL 
        """
        leaving_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = db.execute(query, (leaving_time, spot_id))

        if cursor.rowcount == 0:
            return {"success": False, "error": "Unable to add leaving_timestamp"}

        db.commit()
        parking_time = spot_data["park_in_time"]
        elapsed_hours = (
            datetime.strptime(leaving_time, "%Y-%m-%d %H:%M:%S")
            - datetime.strptime(parking_time, "%Y-%m-%d %H:%M:%S")
        ).total_seconds() / 3600
        cost_per_hour = spot_data["price_per_day"]
        total_cost = round(elapsed_hours * cost_per_hour, 2)
        return {
            "success": True,
            "message": f"spot release successfully. Total Price: {total_cost}",
        }
    except Exception as e:
        return {"success": False, "error": f"{e}"}
