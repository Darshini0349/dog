"""
Project 1 (APIs): Weather Dashboard
Fetches a multi-day weather forecast for any city and prints a clean
dashboard, using the free, keyless Open-Meteo API.

REAL API: Open-Meteo (open-meteo.com) needs no API key. This code is
production-correct. If the network is unavailable (e.g. a locked-down
sandbox), it falls back to sample data so you can still see the output
format — the fallback is clearly labelled, never presented as live data.

Run: pip install requests
     python 01_weather_dashboard.py "Bengaluru"

Concepts practiced: calling a real REST API, two-step API flow (geocode
city -> fetch weather by coords), parsing nested JSON, graceful degradation
when the network fails.
"""

import sys
import requests

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 51: "Light drizzle", 61: "Rain", 63: "Moderate rain",
    65: "Heavy rain", 71: "Snow", 80: "Rain showers", 95: "Thunderstorm",
}


def geocode_city(city):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(url, params={"name": city, "count": 1}, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None
    r = results[0]
    return {"name": r["name"], "country": r.get("country", ""), "lat": r["latitude"], "lon": r["longitude"]}


def fetch_forecast(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto", "forecast_days": 5,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def sample_data():
    """Clearly-labelled offline fallback so the script always demonstrates output."""
    return {
        "location": {"name": "Bengaluru", "country": "India"},
        "current": {"temperature_2m": 27.3, "relative_humidity_2m": 65,
                    "weather_code": 2, "wind_speed_10m": 12.4},
        "daily": {
            "time": ["2026-07-02", "2026-07-03", "2026-07-04", "2026-07-05", "2026-07-06"],
            "weather_code": [2, 61, 63, 3, 1],
            "temperature_2m_max": [28, 26, 25, 27, 29],
            "temperature_2m_min": [19, 20, 20, 19, 18],
        },
    }


def print_dashboard(location, current, daily):
    print("\n" + "=" * 44)
    print(f"  WEATHER: {location['name']}, {location['country']}")
    print("=" * 44)
    print(f"  Now: {current['temperature_2m']}°C, {WEATHER_CODES.get(current['weather_code'], '?')}")
    print(f"  Humidity: {current['relative_humidity_2m']}%   Wind: {current['wind_speed_10m']} km/h")
    print("-" * 44)
    print("  5-DAY FORECAST")
    for i, day in enumerate(daily["time"]):
        code = daily["weather_code"][i]
        hi = daily["temperature_2m_max"][i]
        lo = daily["temperature_2m_min"][i]
        print(f"  {day}:  {lo:>2.0f}-{hi:>2.0f}°C   {WEATHER_CODES.get(code, '?')}")
    print("=" * 44)


def main():
    city = sys.argv[1] if len(sys.argv) > 1 else "Bengaluru"
    print(f"=== Weather Dashboard: {city} ===")

    try:
        location = geocode_city(city)
        if location is None:
            print(f"City '{city}' not found.")
            return
        data = fetch_forecast(location["lat"], location["lon"])
        print_dashboard(location, data["current"], data["daily"])
    except requests.exceptions.RequestException as e:
        print(f"\n[Network unavailable: {type(e).__name__}] Showing SAMPLE data instead.")
        s = sample_data()
        print_dashboard(s["location"], s["current"], s["daily"])


if __name__ == "__main__":
    main()