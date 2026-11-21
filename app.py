"""SERPENTIA — Global 100 Snakes Encyclopedia (Flask entry point)."""

from __future__ import annotations

import os

from flask import Flask, render_template

from db import init_db
from routes.api_routes import api
from routes.web_routes import web


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SERPENTIA_SECRET", "serpentia-local-dev-key")
    app.config["DATABASE"] = os.environ.get(
        "SERPENTIA_DB", os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "snakes.db")
    )
    app.config["JSON_SORT_KEYS"] = False

    init_db(app.config["DATABASE"])

    app.register_blueprint(web)
    app.register_blueprint(api, url_prefix="/api")

    @app.context_processor
    def inject_site_globals():
        from db import fetch_one

        stats = fetch_one(
            """SELECT COUNT(*) AS total,
                      SUM(venom_status = 'Venomous') AS venomous,
                      SUM(venom_status = 'Non-Venomous') AS non_venomous,
                      COUNT(DISTINCT continent) AS continents,
                      COUNT(DISTINCT family) AS families
               FROM snakes"""
        ) or {}
        return {"site_stats": stats}

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
