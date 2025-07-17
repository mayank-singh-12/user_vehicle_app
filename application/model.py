import sqlite3
from .database import get_db, close_db


# def get_user_reservations(user_id):
#     db = get_db()
#     query = """SELECT r.id as reseravtion_id,
#               r.parking_timestamp,
#               ps.id as spot_id,
#               ps.status,
#               pl.prime_location_name as lot_prime_location,
#               pl.pin_code as lot_pin_code,
#               pl.address as lot_address,
#               pl.maximum_number_of_spots

#         FROM reserve_parking_spot as r
#         JOIN parking_spot as ps ON r.spot_id = ps.id
#         JOIN parking_lot as pl ON ps.lot_id = pl.id

#          WHERE r.user_id = 1 """
#     cursor = db.execute(query)
#     for row in cursor.fetchall():
#         print(
#             row
#         )


def get_user_reservations(user_id):
    db = get_db()
    # query = """
    #     SELECT r.id as reservation_id,
    #            r.parking_timestamp,
    #            ps.id as spot_id,
    #            ps.status,
    #            pl.prime_location_name as lot_prime_location,
    #            pl.pin_code as lot_pin_code,
    #            pl.address as lot_address,
    #            pl.maximum_number_of_spots
    #       FROM reserve_parking_spot as r
    #       JOIN parking_spot as ps ON r.spot_id = ps.id
    #       JOIN parking_lot as pl ON ps.lot_id = pl.id
    #      WHERE r.user_id = ?
    # """
    query = """SELECT * FROM reserve_parking_spot WHERE user_id = ?"""
    cursor = db.execute(query, (user_id,))
    rows = cursor.fetchall()

    data = []

    for row in rows:
        data.append(row["user_id"])
    return data
