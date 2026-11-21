"""Server-rendered pages: home, directory, infographic detail and admin."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import fetch_all, fetch_one, get_db

web = Blueprint("web", __name__)

ORDERS = {
    "name": "common_name ASC",
    "danger": "danger_level DESC, common_name ASC",
    "length": "length_cm DESC, common_name ASC",
}

FEATURED_IDS = (1, 5, 29, 35, 50, 82)  # King Cobra, Malabar Pit Viper, Black Mamba, Gaboon Viper, Anaconda, Inland Taipan

MORPH_COLORS = {
    "green": "#4D7C0F", "emerald": "#059669", "olive": "#65A30D",
    "yellow": "#EAB308", "golden": "#CA8A04", "gold": "#D97706",
    "black": "#18181B", "dark": "#27272A", "grey": "#71717A", "gray": "#71717A",
    "silver": "#A8A29E", "white": "#E7E5E4", "cream": "#FEF3C7", "pale": "#D6D3D1",
    "brown": "#78350F", "tan": "#A16207", "copper": "#B45309", "bronze": "#92700E",
    "red": "#B91C1C", "crimson": "#DC2626", "pink": "#DB2777", "purple": "#7E22CE",
    "blue": "#1D4ED8", "violet": "#6D28D9", "orange": "#EA580C", "rufous": "#9A3412",
    "sand": "#D2B48C", "yellow-green": "#84CC16", "blue-grey": "#64748B",
    "blue-black": "#1E293B", "white-banded": "#E7E5E4", "yellow-banded": "#FACC15",
    "black-banded": "#18181B", "bicoloured": "#EAB308", "iridescent": "#0D9488",
    "chequered": "#57534E", "chain": "#A8A29E", "hourglass": "#92400E",
    "diamonds": "#A16207", "triangles": "#78716C", "striped": "#65A30D",
    "spotted": "#A16207", "banded": "#B91C1C", "light": "#D6D3D1",
}


def morph_swatch(name: str) -> str:
    lowered = name.lower()
    for token, color in MORPH_COLORS.items():
        if token in lowered:
            return color
    return "#A8A29E"


@web.route("/")
def index():
    placeholders = ",".join("?" for _ in FEATURED_IDS)
    featured = fetch_all(
        f"SELECT * FROM snakes WHERE id IN ({placeholders})",
        FEATURED_IDS,
    )
    # Preserve the curated order in Python (SQLite has no FIELD() function).
    by_id = {s["id"]: s for s in featured}
    featured = [by_id[i] for i in FEATURED_IDS if i in by_id]

    venomous = fetch_all("SELECT * FROM snakes WHERE venom_status = 'Venomous' ORDER BY danger_level DESC LIMIT 4")
    giants = fetch_all("SELECT * FROM snakes WHERE venom_status = 'Non-Venomous' ORDER BY length_cm DESC LIMIT 4")
    return render_template("index.html", featured=featured, venomous=venomous, giants=giants)


@web.route("/snakes")
def directory():
    venom = request.args.get("venom", "All")
    continent = request.args.get("continent", "All")
    q = request.args.get("q", "").strip()
    order = ORDERS.get(request.args.get("sort", "name"), ORDERS["name"])

    where, params = [], []
    if venom in {"Venomous", "Non-Venomous", "Mildly Venomous"}:
        where.append("venom_status = ?")
        params.append(venom)
    if continent in {"Asia", "Africa", "Americas", "Australia", "Europe"}:
        where.append("continent = ?")
        params.append(continent)
    if q:
        where.append("(common_name LIKE ? OR scientific_name LIKE ? OR family LIKE ? OR country LIKE ? OR habitat LIKE ?)")
        params.extend([f"%{q}%"] * 5)

    sql = "SELECT * FROM snakes"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += f" ORDER BY {order}"

    snakes = fetch_all(sql, tuple(params))
    continents = [r["continent"] for r in fetch_all("SELECT DISTINCT continent FROM snakes ORDER BY continent")]
    return render_template(
        "directory.html", snakes=snakes, continents=continents,
        active_venom=venom, active_continent=continent, query=q, active_sort=request.args.get("sort", "name")
    )


@web.route("/snake/<int:snake_id>")
def snake_detail(snake_id: int):
    snake = fetch_one("SELECT * FROM snakes WHERE id = ?", (snake_id,))
    if snake is None:
        return render_template("404.html"), 404
    morphs = [
        {"name": m.strip(), "color": morph_swatch(m)}
        for m in (snake["color_morphs"] or "").split(",") if m.strip()
    ]
    related = fetch_all(
        "SELECT id, common_name, scientific_name, image_url, danger_level FROM snakes "
        "WHERE family = ? AND id != ? ORDER BY danger_level DESC LIMIT 4",
        (snake["family"], snake_id),
    )
    return render_template("snake_detail.html", snake=snake, morphs=morphs, related=related)


@web.route("/venom-guide")
def venom_guide():
    return redirect(url_for("web.directory", venom="Venomous"))


@web.route("/regions")
def regions():
    return redirect(url_for("web.directory") + "#region-filter")


@web.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        form = request.form
        common = form.get("common_name", "").strip()
        scientific = form.get("scientific_name", "").strip()
        if not common or not scientific:
            flash("Common name and scientific name are required.", "error")
            return redirect(url_for("web.admin"))

        try:
            length_cm = max(0, int(form.get("length_cm") or 0))
            danger = min(5, max(1, int(form.get("danger_level") or 1)))
        except ValueError:
            flash("Length and danger level must be numbers.", "error")
            return redirect(url_for("web.admin"))

        values = (
            common, scientific, form.get("family", "").strip(),
            form.get("continent", "Asia").strip(), form.get("country", "").strip(),
            form.get("habitat", "").strip(), length_cm,
            form.get("venom_status", "Non-Venomous"), form.get("venom_type", "None"),
            danger, form.get("head_shape", "").strip(), form.get("pupil_shape", "").strip(),
            form.get("color_morphs", "").strip(), form.get("image_url", "").strip(),
            form.get("description", "").strip(),
        )

        conn = get_db()
        try:
            existing = conn.execute(
                "SELECT id FROM snakes WHERE scientific_name = ?", (scientific,)
            ).fetchone()
            if existing:
                conn.execute(
                    """UPDATE snakes SET common_name=?, family=?, continent=?, country=?,
                       habitat=?, length_cm=?, venom_status=?, venom_type=?, danger_level=?,
                       head_shape=?, pupil_shape=?, color_morphs=?, image_url=?, description=?
                       WHERE scientific_name=?""",
                    (values[0],) + values[2:] + (scientific,),
                )
                action = "updated"
            else:
                conn.execute(
                    """INSERT INTO snakes (common_name, scientific_name, family, continent,
                       country, habitat, length_cm, venom_status, venom_type, danger_level,
                       head_shape, pupil_shape, color_morphs, image_url, description)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    values,
                )
                action = "added"
            conn.commit()
        finally:
            conn.close()
        flash(f"{common} {action} successfully.", "success")
        return redirect(url_for("web.admin"))

    snakes = fetch_all("SELECT id, common_name, scientific_name, continent, venom_status FROM snakes ORDER BY common_name")
    edit_id = request.args.get("edit", type=int)
    editing = fetch_one("SELECT * FROM snakes WHERE id = ?", (edit_id,)) if edit_id else None
    return render_template("admin.html", snakes=snakes, editing=editing)
