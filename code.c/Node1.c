
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <SPI.h>
#include <MFRC522.h>

const char* ssid = "Yashu@123";
const char* password = "123456789";
const char* mqtt_server = "10.111.130.164";
const char* mqtt_user = "iot_user";
const char* mqtt_pass = "iot_pass";

WiFiClient espClient;
PubSubClient client(espClient);
Servo doorServo;
MFRC522 rfid(5, 22);

#define TRIG 33
#define ECHO 32
#define IR 26
#define PIR 27
#define LED 25
#define BUZZER 14
#define SERVO 13

// ---------- WiFi ----------
void setup_wifi() {
  Serial.print("Connecting WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.println(WiFi.localIP());
}

// ---------- MQTT ----------
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting MQTT...");
    if (client.connect("Node1", mqtt_user, mqtt_pass)) {
      Serial.println("OK");
      client.subscribe("home/node1/cmd");
    } else {
      Serial.print("Fail rc=");
      Serial.println(client.state());
      delay(3000);
    }
  }
}

// ---------- Distance ----------
long getDistance() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  long d = pulseIn(ECHO, HIGH, 30000);
  if (d == 0) return 999;
  return d * 0.034 / 2;
}

// ---------- RFID ----------
String getRFID() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return "";
  String tag = "";
  for (byte i=0;i<rfid.uid.size;i++){
    tag += String(rfid.uid.uidByte[i], HEX);
  }
  tag.toLowerCase();
  rfid.PICC_HaltA();
  return tag;
}

// ---------- Callback ----------
void callback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<100> doc;
  deserializeJson(doc, payload);

  digitalWrite(LED, doc["led"]);
  digitalWrite(BUZZER, doc["buzzer"]);
  doorServo.write(doc["servo"] ? 90 : 0);
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(IR, INPUT);
  pinMode(PIR, INPUT);
  pinMode(LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  doorServo.attach(SERVO);
  SPI.begin();
  rfid.PCD_Init();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  long distance = getDistance();
  int ir = digitalRead(IR);
  int pir = digitalRead(PIR);
  String tag = getRFID();

  StaticJsonDocument<200> doc;
  doc["distance"] = distance;
  doc["ir"] = ir;
  doc["pir"] = pir;
  doc["rfid"] = tag;

  char buffer[200];
  serializeJson(doc, buffer);

  client.publish("home/node1/data", buffer);
  Serial.println(buffer);

  delay(1000);
}
