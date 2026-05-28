#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ESP32Servo.h>

// ================= WIFI =================
const char* ssid = "Yashu@123";
const char* password = "123456789";
const char* mqtt_server = "10.111.130.164";

const char* mqtt_user = "iot_user";
const char* mqtt_pass = "iot_pass";

WiFiClient espClient;
PubSubClient client(espClient);

// ================= RFID =================
#define SS1 21
#define RST1 22
#define SS2 15
#define RST2 27

MFRC522 rfid1(SS1, RST1);
MFRC522 rfid2(SS2, RST2);

// ================= IR =================
#define IR1 34
#define IR2 35

// ================= LED =================
#define LED1 26
#define LED2 25
#define LED3 33

// ================= SERVO =================
#define SERVO1_PIN 14
#define SERVO2_PIN 13

Servo servo1;
Servo servo2;

// ================= STATES =================
bool room1_active = false;
bool room2_active = false;

unsigned long room1_timer = 0;
unsigned long room2_timer = 0;

// ================= RFID READ =================
String readRFID(MFRC522 &rfid)
{
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial())
    return "";

  String tag = "";
  for (byte i = 0; i < rfid.uid.size; i++)
  {
    if (rfid.uid.uidByte[i] < 0x10) tag += "0";
    tag += String(rfid.uid.uidByte[i], HEX);
  }

  tag.toLowerCase();
  rfid.PICC_HaltA();
  return tag;
}

// ================= CALLBACK =================
void callback(char* topic, byte* payload, unsigned int length)
{
  String msg = "";
  for (int i = 0; i < length; i++) msg += (char)payload[i];

  StaticJsonDocument<200> doc;
  deserializeJson(doc, msg);

  if (doc["servo1"] == 1)
  {
    room1_active = true;
    room1_timer = millis();
  }

  if (doc["servo2"] == 1)
  {
    room2_active = true;
    room2_timer = millis();
  }
}

// ================= WIFI =================
void setup_wifi()
{
  Serial.print("Connecting WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// ================= MQTT =================
void reconnect()
{
  while (!client.connected())
  {
    Serial.print("Connecting MQTT...");

    if (client.connect("Node3", mqtt_user, mqtt_pass))
    {
      Serial.println("CONNECTED");
      client.subscribe("home/node3/cmd");
    }
    else
    {
      Serial.print("FAILED, rc=");
      Serial.print(client.state());
      Serial.println(" retrying...");
      delay(3000);
    }
  }
}

// ================= SETUP =================
void setup()
{
  Serial.begin(115200);

  SPI.begin(18, 19, 23);

  pinMode(SS1, OUTPUT);
  pinMode(SS2, OUTPUT);

  digitalWrite(SS1, HIGH);
  digitalWrite(SS2, HIGH);

  rfid1.PCD_Init();
  rfid2.PCD_Init();

  pinMode(IR1, INPUT);
  pinMode(IR2, INPUT);

  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  pinMode(LED3, OUTPUT);

  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);

  servo1.write(0);
  servo2.write(0);

  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

// ================= LOOP =================
void loop()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    setup_wifi();
  }

  if (!client.connected())
  {
    reconnect();
  }

  client.loop();

  // ===== RFID SWITCHING =====
  digitalWrite(SS1, LOW);
  digitalWrite(SS2, HIGH);
  String rfidTag1 = readRFID(rfid1);
  delay(50);

  digitalWrite(SS1, HIGH);
  digitalWrite(SS2, LOW);
  String rfidTag2 = readRFID(rfid2);
  delay(50);

  int ir1 = digitalRead(IR1);
  int ir2 = digitalRead(IR2);

  // ===== DEBUG =====
  Serial.print("RFID1: "); Serial.println(rfidTag1);
  Serial.print("RFID2: "); Serial.println(rfidTag2);
  Serial.print("IR1: "); Serial.println(ir1);
  Serial.print("IR2: "); Serial.println(ir2);

  // ===== ALWAYS SEND DATA =====
  StaticJsonDocument<200> doc;
  doc["rfid1"] = rfidTag1;
  doc["rfid2"] = rfidTag2;
  doc["ir1"] = ir1;
  doc["ir2"] = ir2;

  char buffer[200];
  serializeJson(doc, buffer);

  client.publish("home/node3/data", buffer);

  // ===== ROOM1 CONTROL =====
  if (room1_active)
  {
    servo1.write(90);

    if (ir1 == 0)
      digitalWrite(LED1, HIGH);

    if (millis() - room1_timer > 5000)
    {
      room1_active = false;
      servo1.write(0);
      digitalWrite(LED1, LOW);
    }
  }

  // ===== ROOM2 CONTROL =====
  if (room2_active)
  {
    servo2.write(90);

    if (ir2 == 0)
    {
      digitalWrite(LED2, HIGH);
      digitalWrite(LED3, HIGH);
    }

    if (millis() - room2_timer > 5000)
    {
      room2_active = false;
      servo2.write(0);
      digitalWrite(LED2, LOW);
      digitalWrite(LED3, LOW);
    }
  }

  delay(1000);
}
