import json
import time
import paho.mqtt.client as mqtt
import sys

# ================= LOGIN =================
print("Press @ to unlock edge console or ENTER to run normally")
if input() == "@":
    u = input("Username: ")
    p = input("Password: ")
    if u != "admin" or p != "1234":
        print("ACCESS DENIED")
        sys.exit()
    print("ACCESS GRANTED\n")

# ================= MQTT =================
#broker = "localhost"
LOCAL_BROKER = "10.111.130.164"   # ESP32 ? Pi
AWS_BROKER = "3.106.54.200"       # Pi ? AWS
mqtt_user = "iot_user"
mqtt_pass = "iot_pass"

client = mqtt.Client()
client.username_pw_set(mqtt_user, mqtt_pass)
client.connect(LOCAL_BROKER, 1883)

aws_client = mqtt.Client()
aws_client.username_pw_set(mqtt_user, mqtt_pass)   # ?? ADD THIS
aws_client.connect(AWS_BROKER, 1883)
aws_client.loop_start()

# ================= DATA =================
node1_data = None
node2_data = None
node3_data = None

# ================= NODE1 EXTRA VARIABLES (FIXED) =================
node1_last_rfid = ""
node1_rfid_time = 0
RFID_HOLD_TIME = 3   # seconds

# ================= NODE2 VARIABLES =================
gas_history = []
MAX_HISTORY = 5
previous_gas = 0

# ================= CALLBACK =================
def on_connect(client, userdata, flags, rc):
    print("Connected:", rc)
    client.subscribe("home/node1/data")
    client.subscribe("home/node2/data")
    client.subscribe("home/node3/data")

def on_message(client, userdata, msg):
    global node1_data, node2_data, node3_data
    global node1_last_rfid, node1_rfid_time

    try:
        data = json.loads(msg.payload.decode())
    except:
        return

    print("RECEIVED:", msg.topic)

    if msg.topic == "home/node1/data":
        node1_data = data

        # ? FIX RFID DELAY (store immediately)
        if data.get("rfid"):
            node1_last_rfid = data["rfid"]
            node1_rfid_time = time.time()

    elif msg.topic == "home/node2/data":
        node2_data = data
    elif msg.topic == "home/node3/data":
        node3_data = data
        handle_node3(data)
    print("FORWARDING TO AWS:", msg.topic)
    aws_client.publish(msg.topic, json.dumps(data))
# ================= NODE1 =================
def node1_logic():
    print("\nNODE1:")

    if not node1_data:
        print("No data")
        return

    d = node1_data.get("distance", 999)
    ir = node1_data.get("ir", 1)
    pir = node1_data.get("pir", 0)

    current_time = time.time()

    # ? FIX RFID HOLD (no delay now)
    if (current_time - node1_rfid_time) <= RFID_HOLD_TIME:
        rfid = node1_last_rfid
    else:
        rfid = ""

    # ---- NORMALIZATION ----
    distance_norm = max(0, (5 - d) / 5)
    ir_norm = 1 - ir
    pir_norm = pir

    presence = 0.5*distance_norm + 0.3*ir_norm + 0.2*pir_norm
    rfid_valid = (rfid == "617e7b17")

    confidence = 0.7*presence + 0.3*(1 if rfid_valid else 0)

    cmd1 = {"servo": 0, "led": 0, "buzzer": 0}

    if rfid_valid and presence > 0.3:
        state = "ACCESS GRANTED"
        cmd1["servo"] = 1
        cmd1["led"] = 1

    elif presence > 0.4:
        state = "WAITING RFID"
        cmd1["buzzer"] = 1

    else:
        state = "NO PERSON"

    print("presence:", round(presence,2))
    print("confidence:", round(confidence,2))
    print("rfid_valid:", rfid_valid)
    print("state:", state)

    client.publish("home/node1/cmd", json.dumps(cmd1))

# ================= NODE2 =================
def node2_logic():
    global previous_gas

    print("\nNODE2:")

    if not node2_data:
        print("No data")
        return

    gas = node2_data.get("gas", 0)
    flame = node2_data.get("flame", 1)
    pir = node2_data.get("pir", 0)

    gas_norm = gas / 5000
    flame_norm = 1 - flame

    gas_history.append(gas)
    if len(gas_history) > MAX_HISTORY:
        gas_history.pop(0)

    avg_gas = sum(gas_history) / len(gas_history)

    rate = gas - previous_gas
    previous_gas = gas
    rate_norm = min(rate / 1000, 1)

    risk = 0.5*gas_norm + 0.2*flame_norm + 0.2*pir + 0.1*rate_norm

    cmd2 = {"buzzer_mode": 0, "led_mode": 0}

    if risk > 0.7:
        condition = "HIGH EMERGENCY"
        cmd2["buzzer_mode"] = 1
        cmd2["led_mode"] = 1

    elif risk > 0.4:
        condition = "MEDIUM ALERT"
        cmd2["led_mode"] = 1

    elif avg_gas > 2000:
        condition = "SLOW LEAK"

    else:
        condition = "NORMAL"

    print("gas:", gas, "avg:", int(avg_gas), "rate:", rate)
    print("risk:", round(risk,2))
    print("condition:", condition)

    client.publish("home/node2/cmd", json.dumps(cmd2))

# ================= NODE3 =================
room1_time = 0
room2_time = 0

last_rfid1 = ""
last_rfid2 = ""

HOLD_TIME = 5   # seconds

def handle_node3(data):
    global room1_time, room2_time
    global last_rfid1, last_rfid2

    print("\nNODE3:")

    now = time.time()

    # ?? STORE ONLY VALID RFID (IGNORE EMPTY)
    if data.get("rfid1"):
        last_rfid1 = data["rfid1"]
        room1_time = now

    if data.get("rfid2"):
        last_rfid2 = data["rfid2"]
        room2_time = now

    ir1 = data.get("ir1", 1)
    ir2 = data.get("ir2", 1)

    cmd = {"servo1":0, "servo2":0, "led1":0, "led2":0}

    # ?? USE MEMORY (NOT CURRENT DATA)
    if last_rfid1 == "4115f455" and (now - room1_time) < HOLD_TIME:
        print("ROOM1 ACCESS")
        cmd["servo1"] = 1
        if ir1 == 0:
            cmd["led1"] = 1
    else:
        print("ROOM1 DENIED")

    if last_rfid2 == "4150ae55" and (now - room2_time) < HOLD_TIME:
        print("ROOM2 ACCESS")
        cmd["servo2"] = 1
        if ir2 == 0:
            cmd["led2"] = 1
    else:
        print("ROOM2 DENIED")

    client.publish("home/node3/cmd", json.dumps(cmd))

# ================= MAIN =================
client.on_connect = on_connect
client.on_message = on_message

client.loop_start()

try:
    while True:
        print("\n================ EDGE OUTPUT ================\n")
        node1_logic()
        node2_logic()
        #if node3_data:
         #   handle_node3(node3_data)
        print("\n============================================\n")
        time.sleep(1)   # ? reduced delay ? faster response

except KeyboardInterrupt:
    print("\nProgram stopped safely")
    client.loop_stop()
    client.disconnect()
