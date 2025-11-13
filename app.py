from flask import Flask, render_template, request
import requests
import csv
import os

app = Flask(__name__)

API_KEY = "cur_live_1IpDQPNJIj8UwY2A0EYnE0Lmw0o0F0zpyurNqVer"  # your API key

# Function to fetch currency data
def get_currency_list():
    url = f"https://api.currencyapi.com/v3/currencies?apikey={API_KEY}"
    response = requests.get(url).json()
    data = response.get("data", {})

    country_map = {
        "INR": "India", "USD": "United States", "EUR": "European Union",
        "JPY": "Japan", "GBP": "United Kingdom", "AUD": "Australia",
        "CAD": "Canada", "CNY": "China", "AED": "United Arab Emirates",
        "CHF": "Switzerland", "SGD": "Singapore", "NZD": "New Zealand",
        "ZAR": "South Africa"
    }

    currencies = []
    for code, info in data.items():
        currencies.append({
            "code": code,
            "name": info.get("name", ""),
            "symbol": info.get("symbol", ""),
            "flag": info.get("flag", ""),
            "country": country_map.get(code, info.get("name", "")),
        })
    return currencies


@app.route("/", methods=["GET", "POST"])
def index():
    converted_amount = None
    symbol = None
    flag = None
    feedback_given = False

    currencies = get_currency_list()

    if request.method == "POST":
        if "amount" in request.form:  # conversion form
            try:
                amount = float(request.form['amount'])
                from_currency = request.form['from']
                to_currency = request.form['to']

                url = f"https://api.currencyapi.com/v3/latest?apikey={API_KEY}&currencies={to_currency}&base_currency={from_currency}"
                data = requests.get(url).json()
                rate = data["data"][to_currency]["value"]
                converted_amount = rate * amount

                for c in currencies:
                    if c["code"] == to_currency:
                        symbol = c["symbol"]
                        flag = c["flag"]
                        break

            except Exception as e:
                print("Error:", e)

        elif "rating" in request.form:  # feedback form
            rating = request.form['rating']
            comment = request.form.get('comment', '')

            file_exists = os.path.isfile("feedback.csv")
            with open("feedback.csv", mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Rating", "Comment"])
                writer.writerow([rating, comment])

            feedback_given = True

    return render_template(
        "index.html",
        currencies=currencies,
        converted_amount=converted_amount,
        symbol=symbol,
        flag=flag,
        feedback_given=feedback_given
    )


if __name__ == "__main__":
    app.run(debug=True)
