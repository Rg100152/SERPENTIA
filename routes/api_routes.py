"""JSON API used by the live search, filters and hero slider."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from db import fetch_all, fetch_one

api = Blueprint("api", __name__)

VALID_VENOM = {"Venomous", "Non-Venomous", "Mildly Venomous"}
VALID_CONTINENT = {"Asia", "Africa", "Americas", "Australia", "Europe"}


@api.route("/snakes")
def snakes():
    venom = request.args.get("venom", "All")
    continent = request.args.get("continent", "All")
    habitat = request.args.get("habitat", "All")
    q = request.args.get("q", "").strip()

    where, params = [], []
    if venom in VALID_VENOM:
        where.append("venom_status = ?")
        params.append(venom)
    if continent in VALID_CONTINENT:
        where.append("continent = ?")
        params.append(continent)
    if habitat and habitat != "All":
        where.append("habitat LIKE ?")
        params.append(f"%{habitat}%")
    if q:
        where.append(
            "(common_name LIKE ? OR scientific_name LIKE ? OR family LIKE ? "
            "OR country LIKE ? OR habitat LIKE ? OR color_morphs LIKE ?)"
        )
        params.extend([f"%{q}%"] * 6)

    sql = "SELECT * FROM snakes"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY common_name ASC"

    results = fetch_all(sql, tuple(params))
    return jsonify({"count": len(results), "results": results})


@api.route("/snakes/<int:snake_id>")
def snake(snake_id: int):
    record = fetch_one("SELECT * FROM snakes WHERE id = ?", (snake_id,))
    if record is None:
        return jsonify({"error": "Snake not found"}), 404
    return jsonify(record)


@api.route("/featured")
def featured():
    ids = (1, 5, 29, 35, 50, 82)
    placeholders = ",".join("?" for _ in ids)
    rows = fetch_all(f"SELECT * FROM snakes WHERE id IN ({placeholders})", ids)
    by_id = {r["id"]: r for r in rows}
    return jsonify({"results": [by_id[i] for i in ids if i in by_id]})


@api.route("/stats")
def stats():
    row = fetch_one(
        """SELECT COUNT(*) AS total,
                  SUM(venom_status = 'Venomous') AS venomous,
                  SUM(venom_status = 'Non-Venomous') AS non_venomous,
                  SUM(venom_status = 'Mildly Venomous') AS mildly_venomous,
                  COUNT(DISTINCT continent) AS continents,
                  COUNT(DISTINCT family) AS families
           FROM snakes"""
    )
    return jsonify(row or {})
