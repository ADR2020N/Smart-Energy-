import psycopg2
import random
from datetime import datetime, timedelta

# -----------------------------------
# Database Configuration
# -----------------------------------
DB_HOST = "localhost"
DB_PORT = 5433
DB_NAME = "smart_grid"
DB_USER = "postgres"
DB_PASSWORD = "root"   # change if needed

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
conn.autocommit = True
cur = conn.cursor()

# -----------------------------------
# Simulation Parameters
# -----------------------------------
N_METERS = 500
START_METER_ID = 1000000000
INTERVAL_MINUTES = 5
DAYS = 14

start_time = datetime.utcnow() - timedelta(days=DAYS)
end_time = datetime.utcnow()

print("⏳ Loading 2 weeks of historical data...")

insert_sql = """
INSERT INTO energy_readings
(meter_id, "timestamp", power, voltage, current, frequency, energy)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

current_time = start_time

while current_time < end_time:
    hour = current_time.hour

    for i in range(N_METERS):
        meter_id = str(START_METER_ID + i)

        # realistic power pattern
        if 6 <= hour <= 9 or 18 <= hour <= 22:
            power = random.uniform(2.5, 4.0)
        elif 0 <= hour <= 4:
            power = random.uniform(0.5, 1.2)
        else:
            power = random.uniform(1.2, 2.0)

        voltage = random.uniform(220, 240)
        current = power * 1000 / voltage
        frequency = random.uniform(49.9, 50.1)
        energy = power * (INTERVAL_MINUTES / 60)

        cur.execute(
            insert_sql,
            (
                meter_id,
                current_time,
                power,
                voltage,
                current,
                frequency,
                energy
            )
        )

    current_time += timedelta(minutes=INTERVAL_MINUTES)

cur.close()
conn.close()

print("✅ Historical data loading completed.")
