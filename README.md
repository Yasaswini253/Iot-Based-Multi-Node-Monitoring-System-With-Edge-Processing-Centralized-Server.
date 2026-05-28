# IoT-Based Multi Node Monitoring System With Edge Processing & Centralized Server

## Overview

This project presents an IoT-based smart monitoring and automation system built using multiple ESP32 sensor nodes, a Raspberry Pi edge device, and a centralized server architecture. The system is designed to monitor different environments within a smart home setup and provide real-time sensing, processing, and control functionalities.

Each node performs dedicated monitoring tasks using integrated sensors and actuators, while the Raspberry Pi acts as the edge processing unit to collect, process, and forward data to the centralized server and user interface.



# Features

* Distributed multi-node IoT architecture
* Edge computing using Raspberry Pi
* Real-time monitoring and control
* Smart home automation
* Sensor-based safety and security
* Centralized server communication
* User monitoring interface



# Technologies Used
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ __ __
| Technology               | Purpose                |
| ------------------------ | ---------------------- |
| ESP32                    | Sensor node controller |
| Raspberry Pi             | Edge processing        |
| C / Embedded Programming | Node development       |
| Python                   | Edge, Server, UI       |
| Socket Programming       | Communication          |
| IoT Architecture         | Distributed monitoring |
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ __ __


# System Architecture

The system consists of three ESP32-based sensor nodes connected to a Raspberry Pi edge device. The Raspberry Pi processes sensor information locally and communicates with the centralized server for monitoring and control.



# Node Descriptions

## Node 1 – Entrance Security Node

This node focuses on smart security and access control at the entrance.

### Components Used

* RFID Module
* Ultrasonic Sensor
* PIR Sensor
* IR Sensor
* Servo Motor
* ESP32

### Functionalities

* RFID-based user authentication
* Human presence detection
* Object detection near the entrance
* Automatic door locking/unlocking using servo motor
* Security monitoring and access management



## Node 2 – Stove Safety Node

This node is designed for kitchen safety monitoring and hazard prevention.

### Components Used

* MQ-2 Gas Sensor
* DHT22 Temperature Sensor
* Buzzer
* Relay Module
* ESP32

### Functionalities

* Gas leakage detection
* Temperature monitoring
* Hazard alert generation using buzzer
* Automatic gas/power cutoff using relay module
* Kitchen safety management



## Node 3 – Bedroom Monitoring Node

This node performs environmental and occupancy monitoring inside the bedroom.

### Components Used

* IR Sensor
* ESP32

### Functionalities

* Occupancy detection
* Room activity monitoring
* Environmental sensing support



**# Edge Processing Unit**

## Raspberry Pi Edge Node

The Raspberry Pi acts as the edge computing device in the system.

### Responsibilities

* Collects data from all ESP32 nodes
* Performs local processing and filtering
* Reduces server communication overhead
* Transfers processed information to centralized server
* Supports real-time monitoring operations



# Centralized Server

The centralized server manages communication between nodes, stores processed data, and supports user monitoring functionalities.



# User Interface

The UI module provides monitoring and visualization of sensor data, alerts, and system status in real time.



# Working Principle

1. ESP32 sensor nodes continuously monitor their assigned environments.
2. Sensor data is transmitted to the Raspberry Pi edge device.
3. The Raspberry Pi performs local processing and filtering.
4. Processed information is sent to the centralized server.
5. The user interface displays monitoring information and alerts in real time.



# Applications

* Smart Home Automation
* Industrial Safety Monitoring
* Smart Security Systems
* Distributed IoT Networks
* Edge Computing Applications



# Future Scope

* Cloud integration
* AI-based anomaly detection
* Mobile application support
* Wireless sensor network expansion
* Secure encrypted communication




# Conclusion

This project demonstrates an efficient IoT-based distributed monitoring architecture integrating ESP32 sensor nodes, Raspberry Pi edge computing, centralized server communication, and real-time monitoring interface for smart automation and safety applications.

# Author

Yasaswini
MTech Embedded Systems
