from flask import Flask, render_template, request
import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

CONTINENTS = [
    "East Asia & Pacific", "Europe & Central Asia", "Latin America & Caribbean",
    "Middle East & North Africa", "North America", "South Asia", "Sub-Saharan Africa"
]

INDICATORS = [
    ("NY.GDP.PCAP.CD", "GDP per Capita (current US$)"),
    ("SP.POP.TOTL", "Total Population"),
    ("SL.UEM.TOTL.ZS", "Unemployment (% of labor force)"),
    ("SP.DYN.LE00.IN", "Life Expectancy at Birth (years)")
]

@app.route("/")
def index():
    return render_template("index.html", continents=CONTINENTS)

@app.route("/countries")
def countries():
    continent = request.args.get("continent")
    url = "http://api.worldbank.org/v2/country?format=json&per_page=500"
    response = requests.get(url)

    if response.status_code != 200:
        return "Failed to fetch countries", 500

    countries = response.json()[1]
    if continent:
        countries = [c for c in countries if c["region"]["value"] == continent]

    filtered = [
        {"id": c["id"], "name": c["name"], "region": c["region"]["value"]}
        for c in countries if c["region"]["value"] != "Aggregates"
    ]
    return render_template("index.html", continents=CONTINENTS, countries=filtered, selected=continent)

@app.route("/country/<code>")
def country_detail(code):
    url = f"http://api.worldbank.org/v2/country/{code}?format=json"
    response = requests.get(url)

    if response.status_code != 200 or not response.json()[1]:
        return "Country not found", 404

    data = response.json()[1][0]
    return render_template("country.html", country=data)

@app.route("/country/<country_id>/graph")
def country_graphs(country_id):
    graphs = []

    for code, label in INDICATORS:
        url = f"http://api.worldbank.org/v2/country/{country_id.lower()}/indicator/{code}?format=json&per_page=100"
        response = requests.get(url)

        if response.status_code != 200:
            continue

        data = response.json()
        if len(data) < 2 or not data[1]:
            continue

        df = pd.DataFrame(data[1])
        df = df[["date", "value"]].dropna()
        if df.empty:
            continue

        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)

        fig = px.line(df, x="date", y="value", title=f"{label} for {country_id.upper()}")
        graph_html = pio.to_html(fig, full_html=False)
        graphs.append((label, graph_html))

    if not graphs:
        return f"<h3>No indicator data found for country {country_id.upper()}</h3>"

    return render_template("graphs_multi.html", country_code=country_id.upper(), graphs=graphs)

if __name__ == "__main__":
    app.run(debug=True, port=5000)