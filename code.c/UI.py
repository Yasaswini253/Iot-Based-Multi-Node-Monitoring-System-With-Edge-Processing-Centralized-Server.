import streamlit as st
import requests
import pandas as pd
import time

API = "http://3.106.54.200:5001/data"

st.set_page_config(layout="wide")

# ================= MEMORY =================
if "gas_history" not in st.session_state:
    st.session_state.gas_history = []

if "door_history" not in st.session_state:
    st.session_state.door_history = []

if "room1_count" not in st.session_state:
    st.session_state.room1_count = 0
    st.session_state.room2_count = 0

# ================= FETCH =================
def get_data():
    try:
        res = requests.get(API)
        return res.json()
    except:
        return None

data = get_data()

st.title("🏠 Smart IoT Dashboard")

if not data:
    st.error("Server not reachable")
    st.stop()

# ================= NODE1 =================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚪 Node1 - Smart Door")

    node1 = data["node1"]

    if node1:
        distance = node1.get("distance", 0)
        ir = node1.get("ir", 1)
        pir = node1.get("pir", 0)
        rfid = node1.get("rfid", "")

        st.metric("Distance (cm)", distance)

        # Status Indicators
        st.write("IR:", "🟢 CLEAR" if ir == 1 else "🔴 BLOCKED")
        st.write("PIR:", "🟢 NO MOTION" if pir == 0 else "🔴 MOTION")

        if rfid:
            st.success("✅ ACCESS GRANTED")
            door_state = 1
        else:
            st.error("❌ ACCESS DENIED")
            door_state = 0

        # Store history
        st.session_state.door_history.append(door_state)
        if len(st.session_state.door_history) > 30:
            st.session_state.door_history.pop(0)

        # Graph
        st.subheader("Door Activity")
        df = pd.DataFrame(st.session_state.door_history, columns=["Door"])
        st.line_chart(df)

    else:
        st.warning("No Node1 data")

# ================= NODE2 =================
with col2:
    st.subheader("🔥 Node2 - Gas Monitoring")

    node2 = data["node2"]

    if node2:
        gas = node2.get("gas", 0)
        temp = node2.get("temp", 0)

        st.metric("Gas", gas)
        st.metric("Temperature", temp)

        # Status Logic
        if gas > 3000:
            st.error("🔴 EMERGENCY")
        elif gas > 2000:
            st.warning("🟡 MEDIUM ALERT")
        else:
            st.success("🟢 NORMAL")

        # Store history
        st.session_state.gas_history.append(gas)
        if len(st.session_state.gas_history) > 50:
            st.session_state.gas_history.pop(0)

        # Graph
        st.subheader("Gas Trend")
        df = pd.DataFrame(st.session_state.gas_history, columns=["Gas"])
        st.line_chart(df)

    else:
        st.warning("No Node2 data")

# ================= NODE3 =================
st.subheader("🏠 Node3 - Room Access")

node3 = data["node3"]

if node3:
    r1 = node3.get("rfid1", "")
    r2 = node3.get("rfid2", "")

    col3, col4 = st.columns(2)

    with col3:
        if r1:
            st.success("Room1 ACCESS")
            st.session_state.room1_count += 1
        else:
            st.error("Room1 DENIED")

    with col4:
        if r2:
            st.success("Room2 ACCESS")
            st.session_state.room2_count += 1
        else:
            st.error("Room2 DENIED")

    # Bar Graph
    st.subheader("Room Access Count")

    df = pd.DataFrame({
        "Room": ["Room1", "Room2"],
        "Access Count": [
            st.session_state.room1_count,
            st.session_state.room2_count
        ]
    })

    st.bar_chart(df.set_index("Room"))

else:
    st.warning("No Node3 data")

# ================= AUTO REFRESH =================
time.sleep(1)
st.rerun()
