"""Smart Traffic Management System Flask application."""

from datetime import datetime
from pathlib import Path
import csv
import random

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask, flash, redirect, render_template, request, url_for


BASE_DIR = Path(__file__).resolve().parent
CHART_DIR = BASE_DIR / "static" / "charts"
DATA_DIR = BASE_DIR / "data"
CONTACT_FILE = DATA_DIR / "contact_submissions.csv"

app = Flask(__name__)
app.secret_key = "smart-traffic-local-demo"


ROADS = [
    "Central Avenue",
    "Riverside Drive",
    "Tech Park Road",
    "Greenway Boulevard",
    "Metro Link",
    "Airport Expressway",
    "Harbor Street",
]


def traffic_rows():
    """Generate realistic sample traffic readings for the monitoring page."""
    now = datetime.now()
    rows = []
    for index, road in enumerate(ROADS):
        count = random.randint(95, 640)
        density = "High" if count > 460 else "Medium" if count > 250 else "Low"
        rows.append(
            {
                "road": road,
                "vehicles": count,
                "density": density,
                "signal": "Priority" if index == 2 else "Active",
                "updated": now.strftime("%I:%M:%S %p"),
            }
        )
    return rows


def dashboard_stats(rows):
    """Summarize road readings into dashboard metrics."""
    return {
        "vehicles": sum(row["vehicles"] for row in rows),
        "congested": sum(row["density"] == "High" for row in rows),
        "speed": random.randint(38, 52),
        "signals": 128,
    }


def generate_charts():
    """Create analytics charts with Matplotlib and save them for Flask."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = ["#1877f2", "#17b890", "#ffb703", "#ef476f"]

    hours = ["6 AM", "8 AM", "10 AM", "12 PM", "2 PM", "4 PM", "6 PM", "8 PM"]
    volume = [820, 1780, 1210, 1060, 1190, 1530, 1910, 980]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(hours, volume, color=colors[0], marker="o", linewidth=3)
    ax.fill_between(hours, volume, color=colors[0], alpha=0.12)
    ax.set_ylabel("Vehicles")
    ax.set_title("Hourly Traffic Volume", loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "hourly_traffic.png", dpi=150, transparent=True)
    plt.close(fig)

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    congestion = [62, 68, 59, 74, 81, 51, 43]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars = ax.bar(days, congestion, color=colors[1], edgecolor="none")
    ax.bar_label(bars, fmt="%d%%", padding=3, fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Congestion index")
    ax.set_title("Weekly Congestion Trend", loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "congestion_trends.png", dpi=150, transparent=True)
    plt.close(fig)

    labels = ["Cars", "Buses", "Two-wheelers", "Freight"]
    shares = [54, 13, 25, 8]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.pie(
        shares,
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"width": 0.48, "edgecolor": "white"},
    )
    ax.set_title("Vehicle Distribution", loc="left", weight="bold")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "vehicle_distribution.png", dpi=150, transparent=True)
    plt.close(fig)


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    rows = traffic_rows()
    return render_template("dashboard.html", stats=dashboard_stats(rows), roads=rows[:4])


@app.route("/monitoring")
def monitoring():
    query = request.args.get("q", "").strip()
    rows = traffic_rows()
    if query:
        rows = [row for row in rows if query.lower() in row["road"].lower()]
    return render_template("monitoring.html", roads=rows, query=query)


@app.route("/analytics")
def analytics():
    generate_charts()
    return render_template("analytics.html")


@app.route("/emergency")
def emergency():
    requests_data = [
        {"unit": "Ambulance AMB-204", "route": "Central Avenue → City Hospital", "eta": "4 min", "status": "Green corridor active", "type": "Medical"},
        {"unit": "Fire Unit FR-12", "route": "Harbor Street → Riverside", "eta": "7 min", "status": "Signals synchronized", "type": "Fire"},
        {"unit": "Police Unit PD-47", "route": "Metro Link → Tech Park", "eta": "9 min", "status": "Priority queued", "type": "Police"},
    ]
    return render_template("emergency.html", requests=requests_data)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please complete every field.", "error")
        else:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            new_file = not CONTACT_FILE.exists()
            with CONTACT_FILE.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                if new_file:
                    writer.writerow(["submitted_at", "name", "email", "message"])
                writer.writerow([datetime.now().isoformat(timespec="seconds"), name, email, message])
            flash("Thank you — your message has been received.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


if __name__ == "__main__":
    generate_charts()
    app.run(debug=True)
