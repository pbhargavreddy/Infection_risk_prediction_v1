# Intelligent Airborne Infection Risk Prediction using IoT and Machine Learning

##

For more clear details view : https://ieeexplore.ieee.org/document/11210669
For documentation refer : https://drive.google.com/file/d/1Nj7VYo_chdG_fk18MIZhCr329dg4Rccg/view?usp=drive_link

## Overview

This project predicts the airborne infection risk of an indoor environment using real-time sensor data collected from an IoT system. Sensor readings are fetched from ThingSpeak, processed using a trained Machine Learning model, and classified into different infection risk levels. The prediction is uploaded back to ThingSpeak, and an automated email alert containing the latest sensor readings and predicted risk is sent to the user.

---

## Prerequisites

Before running this project, ensure the following requirements are met:

- A ThingSpeak channel containing environmental sensor data.
- An IoT device (such as an ESP32) configured to periodically upload sensor readings to the ThingSpeak channel.
- At least 20 sensor readings must be available in the channel before executing the prediction script.
- Trained model files (`scaler.pkl`, `pca.pkl`, and `model.pkl`) must be present in the `model_files` directory.
- Python 3.10 or later.

> **Note:** This repository does **not** include the firmware for the IoT device. You are expected to configure your own microcontroller and sensors to upload data to ThingSpeak in the required format.

---

## Expected ThingSpeak Data Format

The prediction model expects the following fields in the ThingSpeak channel:

| Field   | Sensor       |
| ------- | ------------ |
| Field 1 | Temperature  |
| Field 2 | Humidity     |
| Field 3 | Pressure     |
| Field 4 | PM2.5 (Dust) |
| Field 5 | CO₂          |
| Field 6 | TVOC         |

The Python application retrieves the latest 20 entries from these fields, preprocesses the data, predicts the infection risk, uploads the prediction to another ThingSpeak channel, and sends an email notification.

## Features

- Fetches live sensor data from ThingSpeak
- Uses a trained Machine Learning pipeline for prediction
  - StandardScaler
  - PCA
  - K-Means Clustering

- Predicts infection risk as:
  - Low Risk
  - Medium Risk
  - High Risk

- Uploads predictions to a separate ThingSpeak channel
- Sends automated email notifications with:
  - Predicted risk
  - Latest sensor values
  - Timestamp (converted to IST)
  - ThingSpeak dashboard link

---

## Machine Learning Pipeline

Sensor Data

↓

Data Preprocessing

- StandardScaler

↓

Dimensionality Reduction

- Principal Component Analysis (PCA)

↓

Prediction

- K-Means Clustering

↓

Risk Mapping

- Cluster → Infection Risk Level

---

## Sensors Used

| Sensor Parameter | Description                      |
| ---------------- | -------------------------------- |
| Temperature      | Ambient temperature              |
| Humidity         | Relative humidity                |
| Pressure         | Atmospheric pressure             |
| PM2.5            | Dust concentration               |
| CO₂              | Carbon dioxide concentration     |
| TVOC             | Total Volatile Organic Compounds |

---

## Project Structure

```
.
├── model_files/
│   ├── scaler.pkl
│   ├── pca.pkl
│   └── model.pkl
│
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

## Environment Variables

Create a `.env` file with the following variables:

```env
READ_CHANNEL_ID=YOUR_CHANNEL_ID
READ_API_KEY=YOUR_READ_API_KEY
PREDICTION_WRITE_API_KEY=YOUR_WRITE_API_KEY

EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=receiver_email@gmail.com
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/pbhargavreddy/Infection_risk_prediction_v1.git
```

Move into the project

```bash
cd project-name
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
python main.py
```

---

## Dependencies

- Python 3.10+
- pandas
- requests
- scipy
- scikit-learn
- joblib

---

## Workflow

1. Fetch the latest 20 sensor readings from ThingSpeak.
2. Convert sensor values into a DataFrame.
3. Scale the data using the trained StandardScaler.
4. Apply PCA transformation.
5. Predict infection risk using the trained K-Means model.
6. Determine the majority predicted cluster.
7. Map the cluster to an infection risk level.
8. Upload the prediction back to ThingSpeak.
9. Send an email notification containing:
   - Predicted risk
   - Latest sensor readings
   - Timestamp (IST)
   - ThingSpeak channel link

---

## Sample Email Notification

```
Predicted Risk: Medium Risk

Latest Sensor Readings:

Temperature : 28.4 °C
Humidity    : 63 %
Pressure    : 1008 hPa
PM2.5       : 32
CO₂         : 480 ppm
TVOC        : 65 ppb

Timestamp:
29-06-2026 10:45:12 AM IST

ThingSpeak:
https://thingspeak.com/channels/CHANNEL_ID
```

---

## Technologies Used

- Python
- Machine Learning
- Scikit-learn
- K-Means Clustering
- PCA
- StandardScaler
- ThingSpeak API
- SMTP (Email Alerts)
- IoT Sensors

---

## Future Improvements

- Live dashboard for visualization
- SMS/Telegram notifications
- Real-time streaming using MQTT
- Deep learning-based prediction models
- Edge deployment on Raspberry Pi/ESP32
- Historical trend analysis and reporting

---

## License

This project is intended for academic and educational purposes.
