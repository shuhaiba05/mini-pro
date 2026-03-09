from flask import Flask, render_template, request
import random

# 🔥 Import AI functions
from detection_ai import start_ai_detection, get_bus_data

app = Flask(__name__)

# Bus Data (UNCHANGED)
buses = {
    1: {
        "name": "KSRTC City Express",
        "route": "Calicut → Kozhikode Beach",
        "total_seats": 40,
        "passengers": 0
    },
    2: {
        "name": "Metro Fast Passenger",
        "route": "Calicut → Medical College",
        "total_seats": 35,
        "passengers": 0
    },
    3: {
        "name": "Town Circular",
        "route": "Calicut → Mavoor Road",
        "total_seats": 30,
        "passengers": 0
    }
}

# Home Page (UNCHANGED)
@app.route("/")
def home():
    return render_template("index.html")


# Search Results Page (UNCHANGED)
@app.route("/search", methods=["POST"])
def search():
    source = request.form.get("source")
    destination = request.form.get("destination")

    bus_list = []

    for bus_id, bus in buses.items():
        arrival_time = random.randint(1, 10)

        bus_list.append({
            "id": bus_id,
            "name": bus["name"],
            "route": bus["route"],
            "arrival": f"Arriving in {arrival_time} mins"
        })

    return render_template(
        "bus_list.html",
        source=source,
        destination=destination,
        buses=bus_list
    )


# Bus Detail Page (UNCHANGED)
@app.route("/bus/<int:bus_id>")
def bus_detail(bus_id):
    bus = buses.get(bus_id)
    if not bus:
        return "Bus Not Found", 404

    return render_template(
        "bus_detail.html",
        bus_id=bus_id,
        bus=bus
    )


# 🔥 AI-Based Real-Time API (UPDATED)
@app.route("/api/bus/<int:bus_id>")
def bus_api(bus_id):
    try:
        # Get live data from AI module
        data = get_bus_data(bus_id)
        return data
    except:
        return {"error": "Bus not found"}, 404


# 🔥 Start AI detection when app starts
if __name__ == "__main__":
    start_ai_detection()
    app.run(debug=True)