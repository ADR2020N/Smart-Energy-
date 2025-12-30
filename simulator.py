# -----------------------------------
# Smart Meter Simulator (MQTT Publisher)
# -----------------------------------
import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# -----------------------------------
# MQTT Configuration
# -----------------------------------
BROKER = "localhost"
PORT = 1883
BASE_TOPIC = "energy/meters"

# -----------------------------------
# Simulation Parameters
# -----------------------------------
N_METERS = 5               # 🔁 change to 500 later
INTERVAL_SECONDS = 5       # publish every 5 seconds (test mode)

START_METER_ID = 1000000000
METER_IDS = [str(START_METER_ID + i) for i in range(N_METERS)]

# -----------------------------------
# Helper: realistic power pattern
# -----------------------------------
def realistic_power(hour):
    if 6 <= hour <= 9:
        return random.uniform(2.0, 3.5)     # morning peak
    elif 18 <= hour <= 22:
        return random.uniform(2.5, 4.0)     # evening peak
    elif 0 <= hour <= 4:
        return random.uniform(0.5, 1.2)     # night low
    else:
        return random.uniform(1.2, 2.0)

# -----------------------------------
# MQTT Client
# -----------------------------------
client = mqtt.Client()
client.connect(BROKER, PORT, 60)

print("🔌 Publishing smart meter data...")

# -----------------------------------
# Publish Loop
# -----------------------------------
while True:
    now = datetime.utcnow()
    hour = now.hour

    for meter_id in METER_IDS:
        power = realistic_power(hour)
        voltage = random.uniform(220, 240)
        current = power * 1000 / voltage
        frequency = random.uniform(49.9, 50.1)
        energy = power * (5 / 60)   # kWh for 5-minute interval

        payload = {
            "meter_id": meter_id,
            "timestamp": now.isoformat(),
            "power": round(power, 3),
            "voltage": round(voltage, 2),
            "current": round(current, 3),
            "frequency": round(frequency, 2),
            "energy": round(energy, 4)
        }

        topic = f"{BASE_TOPIC}/{meter_id}"
        client.publish(topic, json.dumps(payload))

        print(f"Published → {topic}: {payload}")

    time.sleep(INTERVAL_SECONDS)
