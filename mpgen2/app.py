from flask import Flask, render_template, request
import os
import pickle
import requests
import csv
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# -------------------------------
# PATH FIX (works locally + cloud)
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model", "lgb_model.pkl")
CSV_FILE_PATH = os.path.join(BASE_DIR, "predictions.csv")

# -------------------------------
# LOAD MODEL
# -------------------------------
with open(MODEL_PATH, 'rb') as file:
    lgb_model = pickle.load(file)

# -------------------------------
# API KEYS (SAFE via .env)
# -------------------------------
GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# -------------------------------
# PLACES
# -------------------------------
PLACES = {
    "BTM Layout": 0, "Banashankari": 1, "Bannerghatta": 2, "Bellandur": 3,
    "Domlur": 4, "HSR Layout": 5, "Hebbal": 6, "Indiranagar": 7,
    "JP Nagar": 8, "Jayanagar": 9, "Jeevanbhima Nagar": 10,
    "Koramangala": 11, "Mahadevapura": 12, "Malleswaram": 13,
    "Marathahalli": 14, "R.T. Nagar": 15, "Rajajinagar": 16,
    "Rajarajeshwari Nagar": 17, "Sadashivanagar": 18,
    "Seshadripuram": 19, "Shivajinagar": 20, "Ulsoor": 21,
    "Vasanthnagar": 22, "Vijaynagar": 23, "Whitefield": 24,
    "Yelahanka": 25, "Yeshwantpur": 26
}

# -------------------------------
# ROUTES
# -------------------------------
@app.route("/")
def home():
    return render_template("index.html", places=PLACES, inputs={})

# -------------------------------
# FUNCTIONS
# -------------------------------
def get_day_status(year, month, day):
    date = datetime(year, month, day)

    if date.weekday() == 6:
        return 0

    url = "https://www.googleapis.com/calendar/v3/calendars/en.indian%23holiday%40group.v.calendar.google.com/events"

    params = {
        "key": GOOGLE_CALENDAR_API_KEY,
        "timeMin": date.isoformat() + "Z",
        "timeMax": (date + timedelta(days=1)).isoformat() + "Z"
    }

    try:
        response = requests.get(url, params=params).json()
        events = response.get('items', [])
        return 0 if events else 1
    except:
        return 1  # fallback

def get_temperature(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url).json()
        return response["main"]["temp"]
    except:
        return 25.0

# -------------------------------
# PREDICT ROUTE
# -------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        year = int(request.form["year"])
        month = int(request.form["month"])
        day = int(request.form["date"])
        place = request.form["place"]
        hour = int(request.form["hour"])

        encoded_place = PLACES.get(place, 0)

        temperature = get_temperature(place)
        day_status = get_day_status(year, month, day)

        # Temperature category
        if temperature < 18:
            temp_cat = 0
        elif temperature < 27:
            temp_cat = 1
        else:
            temp_cat = 2

        features = [[year, month, day, hour, encoded_place, temperature, day_status, temp_cat]]

        ride_demand = int(round(lgb_model.predict(features)[0]))

        # Save CSV safely
        file_exists = os.path.exists(CSV_FILE_PATH)

        with open(CSV_FILE_PATH, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow([
                    "Year", "Month", "Day", "Hour", "Place",
                    "Temperature", "Day Status",
                    "Temperature Category", "Ride Demand"
                ])

            writer.writerow([
                year, month, day, hour, place,
                temperature,
                "Holiday" if day_status == 0 else "Working Day",
                ["Cold", "Moderate", "Hot"][temp_cat],
                ride_demand
            ])

        return render_template(
            "results.html",
            ride_demand=ride_demand,
            inputs={
                "year": year,
                "month": month,
                "day": day,
                "hour": hour,
                "place": place,
                "temperature": temperature,
                "day_status": "Holiday" if day_status == 0 else "Working Day",
                "temperature_category": ["Cold", "Moderate", "Hot"][temp_cat]
            }
        )

    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------
# RUN APP (IMPORTANT FOR DEPLOY)
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
