from flask import Flask, render_template, request, jsonify
import os
import pickle
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Load the LightGBM model using relative paths
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "lgb_model.pkl")

# Safely load the model
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, 'rb') as file:
        lgb_model = pickle.load(file)
else:
    lgb_model = None

# API Keys (Ideally move these to Vercel Environment Variables)
GOOGLE_CALENDAR_API_KEY = os.getenv("GOOGLE_CALENDAR_API_KEY", "AIzaSyAzAfA2xulCmEHyYS9G61NWnzcaPgnGMhQ")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "2e84974857e1d5c6f19d88f89bef1271")

# Flask app initialization
app = Flask(__name__)

# List of places and their corresponding encodings
PLACES = {
    "BTM Layout": 0, "Banashankari": 1, "Bannerghatta": 2, "Bellandur": 3,
    "Domlur": 4, "HSR Layout": 5, "Hebbal": 6, "Indiranagar": 7,
    "JP Nagar": 8, "Jayanagar": 9, "Jeevanbhima Nagar": 10, "Koramangala": 11,
    "Mahadevapura": 12, "Malleswaram": 13, "Marathahalli": 14, "R.T. Nagar": 15,
    "Rajajinagar": 16, "Rajarajeshwari Nagar": 17, "Sadashivanagar": 18,
    "Seshadripuram": 19, "Shivajinagar": 20, "Ulsoor": 21, "Vasanthnagar": 22,
    "Vijaynagar": 23, "Whitefield": 24, "Yelahanka": 25, "Yeshwantpur": 26
}

@app.route("/")
def home():
    return render_template("index.html", places=PLACES, inputs={})

def get_day_status(year, month, day):
    date = datetime(year, month, day)
    if date.weekday() == 6:  # Sunday
        return 0  # Holiday
    url = f"https://www.googleapis.com/calendar/v3/calendars/en.indian%23holiday%40group.v.calendar.google.com/events"
    params = {
        "key": GOOGLE_CALENDAR_API_KEY,
        "timeMin": date.isoformat() + "Z",
        "timeMax": (date + timedelta(days=1)).isoformat() + "Z"
    }
    try:
        response = requests.get(url, params=params)
        events = response.json().get('items', [])
        return 0 if events else 1
    except:
        return 1 # Default to working day if API fails

def get_temperature(year, month, day, city):
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(weather_url).json()
        if response.get("main"):
            return response["main"]["temp"]
    except:
        pass
    return 25.0

@app.route("/predict", methods=["POST"])
def predict():
    if lgb_model is None:
        return "Model file not found. Check path: " + MODEL_PATH, 500

    # Extract inputs
    year = int(request.form["year"])
    month = int(request.form["month"])
    day = int(request.form["date"])
    place = request.form["place"]
    hour = int(request.form["hour"])

    # Process inputs
    encoded_place = PLACES[place]
    temperature = get_temperature(year, month, day, place)
    day_status = get_day_status(year, month, day)

    if temperature < 18:
        temp_cat = 0
    elif 18 <= temperature < 27:
        temp_cat = 1
    else:
        temp_cat = 2

    # Predict
    features = [[year, month, day, hour, encoded_place, temperature, day_status, temp_cat]]
    ride_demand = lgb_model.predict(features)[0]

    # NOTE: CSV writing is removed because Vercel has a read-only filesystem.
    
    return render_template(
        "results.html",
        ride_demand=int(round(ride_demand)),
        inputs={
            "year": year, "month": month, "day": day, "hour": hour,
            "place": place, "temperature": temperature,
            "day_status": "Holiday" if day_status == 0 else "Working Day",
            "temperature_category": ["Cold", "Moderate", "Hot"][temp_cat]
        }
    )

if __name__ == "__main__":
    app.run(debug=True)
