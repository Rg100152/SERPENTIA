<div align="center">

![SERPENTIA Header](https://capsule-render.vercel.app/api?type=wave&color=0:121110,100:EAB308&height=180&section=header&text=SERPENTIA&fontSize=64&fontColor=FAFAF9&animation=fadeIn&desc=GLOBAL%20100%20SNAKES%20ENCYCLOPEDIA&descAlignY=68&descColor=A8A29E)

![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=2800&pause=900&color=EAB308&center=true&vCenter=true&width=760&lines=Track.+Identify.+Survive.;100+Snakes.+One+Archive.;Flask+%2B+SQLite+%2B+Vanilla+JS.)

![Stars](https://img.shields.io/github/stars/Rg100152/SERPENTIA?style=for-the-badge&logo=github&color=EAB308)
![Forks](https://img.shields.io/github/forks/Rg100152/SERPENTIA?style=for-the-badge&logo=github&color=A8A29E)
![Issues](https://img.shields.io/github/issues/Rg100152/SERPENTIA?style=for-the-badge&color=DC2626)
![Last Commit](https://img.shields.io/github/last-commit/Rg100152/SERPENTIA?style=for-the-badge&color=65A30D)
![License](https://img.shields.io/github/license/Rg100152/SERPENTIA?style=for-the-badge&color=78716C)

</div>

---

## Live UI Preview

| Tactical Split-Screen Hero | Scientific Infographic View |
| :---: | :---: |
| ![Hero](https://placehold.co/640x360/121110/EAB308?text=SERPENTIA+HERO) | ![Detail](https://placehold.co/640x360/121110/DC2626?text=INFOGRAPHIC+DETAIL) |

> [!TIP]
> Run `python seed_snakes.py` first to populate all 100 species into SQLite before starting the server. The app also auto-seeds on first run if the database is missing.

---

## What Is It?

**SERPENTIA** is a full-stack, low-RAM-friendly encyclopedia of **100 real snake species** from Asia, Africa, the Americas, Australia and Europe. Every record carries taxonomy, venom profile, danger rating, anatomy (head shape, pupil, heat pits), length scale, habitat, colour morphs and a Wikimedia Commons image.

> [!WARNING]
> Educational reference only. This project is **not** a medical or field-safety authority. For any snakebite, seek emergency medical care immediately.

---

## Key Features

- **Tactical field-guide UI** — volcanic charcoal (`#121110`), desert amber (`#EAB308`), crimson (`#DC2626`), sharp 4px edges; deliberately different from the FishWorld ocean-glass aesthetic.
- **Split-screen hero** — giant translucent `SERPENT` typography behind an overlapping high-contrast specimen, with `‹ PREV / NEXT ›` slider driven by JSON.
- **Instant directory** — live search plus venom and region filter pills; client-side render first, API sync right after.
- **Scientific infographic detail** — danger banner, length ruler, anatomy callouts and a colour-morph swatch grid.
- **Local admin** — add or update records through a form (no authentication; keep it on localhost).
- **Zero heavy dependencies** — Flask + SQLite + vanilla JS, comfortable on a 4 GB machine.

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

---

## Quick Start

```bash
git clone https://github.com/Rg100152/SERPENTIA.git
cd SERPENTIA

python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python seed_snakes.py             # 100 species -> database/snakes.db
python app.py                     # http://127.0.0.1:5000
```

<details>
<summary><b>Click to View Full Project Folder Structure</b></summary>

```text
SERPENTIA/
├── app.py                  # Flask app factory, blueprints, stats context
├── seed_snakes.py          # 100-species dataset + idempotent SQLite seeder
├── db.py                   # Shared SQLite helpers
├── requirements.txt
├── README.md
├── .gitignore
├── database/
│   └── snakes.db           # Generated (git-ignored)
├── routes/
│   ├── __init__.py
│   ├── web_routes.py       # /, /snakes, /snake/<id>, /admin, redirects
│   └── api_routes.py       # /api/snakes, /api/snakes/<id>, /api/featured, /api/stats
├── templates/
│   ├── base.html           # Left rail + top utility bar + footer
│   ├── index.html          # Split-screen hero + slider + field notes
│   ├── directory.html      # Search, filter pills, species grid
│   ├── snake_detail.html   # Infographic profile
│   ├── admin.html          # Add / edit records
│   └── 404.html
└── static/
    ├── css/
    │   ├── variables.css   # Obsidian / Amber / Crimson tokens
    │   ├── style.css       # Shell, rail, cards, filters, admin
    │   ├── hero.css        # Split hero, ghost type, HUD, slider
    │   └── infographic.css # Ruler, anatomy callouts, morph grid
    ├── js/
    │   ├── app.js          # Image fallback utilities
    │   ├── heroSlider.js   # Featured specimen slider
    │   └── filterEngine.js # Instant search + API filter sync
    └── assets/
        └── logo.svg        # Hexagonal scale / fang emblem
```

</details>

---

## Routes & API

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| GET | `/` | Split-screen hero + featured specimens |
| GET | `/snakes?q=&venom=&continent=&sort=` | Filterable species directory |
| GET | `/snake/<id>` | Full infographic profile |
| GET | `/venom-guide`, `/regions` | Shortcuts into the directory |
| GET/POST | `/admin?edit=<id>` | Add or update a snake record |
| GET | `/api/snakes?q=&venom=&continent=&habitat=` | JSON list (used by the filter engine) |
| GET | `/api/snakes/<id>` | JSON single record |
| GET | `/api/featured` | JSON slider data |
| GET | `/api/stats` | JSON counts (total, venomous, regions, families) |

Example:

```bash
curl "http://127.0.0.1:5000/api/snakes?venom=Venomous&continent=Asia"
```

---

## Database Schema

`snakes` table fields: `id`, `common_name`, `scientific_name`, `family`, `continent`, `country`, `habitat`, `length_cm`, `venom_status`, `venom_type`, `danger_level`, `head_shape`, `pupil_shape`, `color_morphs`, `image_url`, `description`, `created_at`.

`seed_snakes.py` is idempotent: re-running it updates existing species by scientific name instead of duplicating rows.

---

<div align="center">

![SERPENTIA Footer](https://capsule-render.vercel.app/api?type=wave&color=0:EAB308,100:121110&height=120&section=footer&text=TRACK.%20IDENTIFY.%20SURVIVE.&fontSize=28&fontColor=FAFAF9)

Built with Flask, SQLite and vanilla JavaScript · `Rg100152/SERPENTIA`

</div>
