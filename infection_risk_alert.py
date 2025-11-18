import os
import requests
import pandas as pd
import joblib
from scipy.stats import mode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


# ============================================================
# CLEAN PATHS (NO SPACES, MATCHES GITHUB)
# ============================================================

SCALER_PATH = "model_files/new_scaler.pkl"
PCA_PATH = "model_files/new_pca.pkl"
MODEL_PATH = "model_files/new_model.pkl"


# ============================================================
# THINGSPEAK CONFIG
# ============================================================

READ_CHANNEL_ID = os.getenv("READ_CHANNEL_ID")
READ_API_KEY = os.getenv("READ_API_KEY")
PREDICTION_WRITE_API_KEY = os.getenv("PREDICTION_WRITE_API_KEY")


# ============================================================
# EMAIL CONFIG (FROM GITHUB SECRETS)
# ============================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")   # GitHub Secret
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# ============================================================
# LOAD MODELS
# ============================================================

scaler = joblib.load(SCALER_PATH)
pca = joblib.load(PCA_PATH)
model = joblib.load(MODEL_PATH)


# ============================================================
# HELPERS
# ============================================================

def safe_float(x):
    try:
        return float(x)
    except:
        return 0.0


def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print("Email failed:", e)


# ============================================================
# BUILD EMAIL CONTENT
# ============================================================

def build_email_text(mode_risk, mode_cluster, latest):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    subject = f"Infection Risk Update – {mode_risk}"

    body = f"""
Time: {time_now}
Predicted Risk: {mode_risk}
Cluster: {mode_cluster}

Latest Sensor Readings:
Temperature: {latest['temp']}
Humidity: {latest['humidity']}
Pressure: {latest['pressure']}
PM2.5 (Dust): {latest['dust']}
CO2: {latest['co2']}
TVOC: {latest['tvoc']}

ThingSpeak Channel:
https://thingspeak.com/channels/{READ_CHANNEL_ID}
"""

    return subject, body


# ============================================================
# FETCH 20 SENSOR READINGS
# ============================================================

url = (
    f"https://api.thingspeak.com/channels/{READ_CHANNEL_ID}/feeds.json"
    f"?results=20&api_key={READ_API_KEY}"
)

resp = requests.get(url)
feeds = resp.json().get("feeds", [])

if not feeds:
    print("No data found. Exiting.")
    exit()


# Build dataframe with CORRECT ORDER:
# temp, humidity, pressure, dust, co2, tvoc

rows = []
for f in feeds:
    rows.append({
        "temp": safe_float(f.get("field1")),
        "humidity": safe_float(f.get("field2")),
        "pressure": safe_float(f.get("field3")),
        "dust": safe_float(f.get("field4")),
        "co2": safe_float(f.get("field5")),
        "tvoc": safe_float(f.get("field6"))
    })

df = pd.DataFrame(rows)


# ============================================================
# PREPROCESS + PREDICT
# ============================================================

scaled = scaler.transform(df)
pca_out = pca.transform(scaled)
predictions = model.predict(pca_out)

cluster_to_risk = {
    0: "Low Risk",
    1: "Medium Risk",
    2: "High Risk"
}

mode_cluster = int(mode(predictions, keepdims=False).mode)
mode_risk = cluster_to_risk[mode_cluster]
latest = df.iloc[-1]


# ============================================================
# SEND PREDICTION TO THINGSPEAK
# ============================================================

update_payload = {
    "api_key": PREDICTION_WRITE_API_KEY,
    "field1": latest["temp"],
    "field2": latest["humidity"],
    "field3": latest["pressure"],
    "field4": latest["dust"],
    "field5": latest["co2"],
    "field6": latest["tvoc"],
    "field7": mode_cluster,
    "field8": mode_risk
}

update_resp = requests.post(
    "https://api.thingspeak.com/update.json",
    data=update_payload
)

print("ThingSpeak response:", update_resp.text)


# ============================================================
# EMAIL ALERT (EVERY 5-MIN RUN)
# ============================================================

subject, body = build_email_text(mode_risk, mode_cluster, latest)
send_email(subject, body)

print("Finished. Risk:", mode_risk)
