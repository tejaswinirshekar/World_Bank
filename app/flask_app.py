from flask import Flask, render_template, request
import requests
import pandas as pd
import plotly.express as px

app = Flask(__name__)

CONTINENTS = [
    "East Asia & Pacific", "Europe & Central Asia", "Latin America & Caribbean",
    "Middle East & North Africa", "North America", "South Asia", "Sub-Saharan Africa"
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

@app.route("/country/<code>/graph")
def graph(code):
    indicator = request.args.get("indicator", "NY.GDP.PCAP.CD")
    url = f"http://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json&per_page=100"
    response = requests.get(url)

    if response.status_code != 200 or not response.json()[1]:
        return "Data not found", 404

    data = response.json()[1]
    df = pd.DataFrame(data)
    df = df[["date", "value"]].dropna()
    df["date"] = pd.to_datetime(df["date"])
    df.sort_values("date", inplace=True)

    fig = px.line(df, x="date", y="value", title=f"{indicator} for {code.upper()}")
    graph_html = fig.to_html(full_html=False)

    return render_template("graph.html", graph_html=graph_html, country_code=code.upper())

if __name__ == "__main__":
    app.run(debug=True, port=5000)