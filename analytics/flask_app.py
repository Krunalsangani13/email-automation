from flask import Flask, request, redirect,send_file
import pandas as pd
import csv
import os
from datetime import datetime

app = Flask(__name__)

os.makedirs("tracking_logs", exist_ok=True)

@app.route('/')
def home():
    return "Welcome to the Email Campaign Tracker!"

# Log open
@app.route('/open')
def open_tracker():
    email = request.args.get("email", "unknown")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log = pd.DataFrame([[email, timestamp]], columns=["Email", "Opened_At"])
    log.to_csv("tracking_logs/opens.csv", mode='a', header=not os.path.exists("tracking_logs/opens.csv"), index=False)

    # Serve a visible image instead
    return send_file("logo.png", mimetype='image/png')

    # return send_file("pixel.png", mimetype='image/png')


# Log click
@app.route('/click')
def click_tracker():
    email = request.args.get("email", "unknown")
    redirect_url = request.args.get("to", "https://google.com")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log = pd.DataFrame([[email, redirect_url, timestamp]], columns=["Email", "Clicked_URL", "Clicked_At"])
    log.to_csv("tracking_logs/clicks.csv", mode='a', header=not os.path.exists("tracking_logs/clicks.csv"), index=False)
    
    return redirect(redirect_url)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
