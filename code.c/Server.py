import json
import time
import sqlite3
from datetime import datetime
import paho.mqtt.client as mqtt
import smtplib
from email.mime.text import MIMEText
import ssl

# ================= CONFIG =================
broker = "3.106.54.200"

# Try TLS first (8883), fallback to normal (1883)
USE_TLS = False
port = 8883 if USE_TLS else 1883

mqtt_user = "iot_user"
mqtt_pass = "iot_pass"

EMAIL = "task46445@gmail.com"
PASSWORD = "vjsadialjhnopkqc"
TO_EMAIL = "kamireddyyasaswini86@gmail.com"

VALID_RFID = "617e7b17"

# ================= DATABASE =================
conn = sqlite3.connect("iot_data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    time TEXT,
    topic TEXT,
    data TEXT
)
""")
conn.commit()

# ================= MEMORY =================
node1_alert_sent = False
node2_alert_sent = False
node2_history = []

# ================= STORE DATA =================
def store(topic, data):
    cursor.execute("INSERT INTO logs VALUES (?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    topic,
                    json.dumps(data)))
    conn.commit()

# ================= EMAIL =================
def send_email(message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = "🚨 IoT Alert"
        msg["From"] = EMAIL
        msg["To"] = TO_EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()

        print("📧 Email Sent")

    except Exception as e:
        print("❌ Email Error:", e)

# ================= ALERT =================
def alert(message):
    print("🚨 ALERT:", message)
    send_email(message)

# ================= DATA VALIDATION =================
def validate_data(data):
    if not isinstance(data, dict):
        return False

    if "gas" in data and not isinstance(data["gas"], (int, float)):
        return False

    if "rfid" in data and not isinstance(data["rfid"], str):
        return False

    return True

# ================= NODE1 (RFID SECURITY) =================
def handle_node1(data):
    global node1_alert_sent

    if not validate_data(data):
        print("⚠️ Invalid Node1 data blocked")
        return

    rfid = data.get("rfid", "")

    # ❌ WRONG RFID
    if rfid != "" and rfid != VALID_RFID:
        print("❌ WRONG RFID → BUZZER ON")

        if not node1_alert_sent:
            alert("🚫 Unauthorized RFID detected at door!")
            node1_alert_sent = True

    # ✅ CORRECT RFID
    elif rfid == VALID_RFID:
        print("✅ ACCESS GRANTED")
        node1_alert_sent = False

# ================= NODE2 (GAS MONITORING) =================
def handle_node2(data):
    global node2_alert_sent, node2_history

    if not validate_data(data):
        print("⚠️ Invalid Node2 data blocked")
        return

    gas = data.get("gas", 0)

    node2_history.append(gas)
    if len(node2_history) > 5:
        node2_history.pop(0)

    avg_gas = sum(node2_history) / len(node2_history)

    # 🔥 EMERGENCY
    if gas > 3000:
        print("🔥 EMERGENCY GAS LEVEL!")

        if not node2_alert_sent:
            alert(f"🔥 EMERGENCY! Gas level HIGH: {gas}")
            node2_alert_sent = True

    # ⚠️ SLOW LEAK
    elif 2000 <= avg_gas <= 3000:
        print("⚠️ SLOW GAS LEAK DETECTED")

    # ✅ NORMAL
    else:
        print("✅ GAS NORMAL")
        node2_alert_sent = False

# ================= NODE3 (OPTIONAL) =================
def handle_node3(data):
    r1 = data.get("rfid1", "")
    r2 = data.get("rfid2", "")

    state = {
        "room1": "ACCESS" if r1 else "DENIED",
        "room2": "ACCESS" if r2 else "DENIED"
    }

    print("🏠 NODE3 STATE:", state)

# ================= MQTT =================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe("home/node1/data")
        client.subscribe("home/node2/data")
        client.subscribe("home/node3/data")
    else:
        print("❌ Connection Failed:", rc)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except:
        print("⚠️ Invalid JSON blocked")
        return

    topic = msg.topic
    print("\n📩 RECEIVED:", topic)

    store(topic, data)

    if topic == "home/node1/data":
        handle_node1(data)

    elif topic == "home/node2/data":
        handle_node2(data)

    elif topic == "home/node3/data":
        handle_node3(data)

# ================= MAIN =================
client = mqtt.Client()

# 🔐 MQTT AUTH
client.username_pw_set(mqtt_user, mqtt_pass)

# 🔐 TLS (optional)
if USE_TLS:
    client.tls_set(cert_reqs=ssl.CERT_NONE)

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port)

print("🚀 SECURE IOT SERVER RUNNING...")

client.loop_start()

try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("🛑 Server stopped")
