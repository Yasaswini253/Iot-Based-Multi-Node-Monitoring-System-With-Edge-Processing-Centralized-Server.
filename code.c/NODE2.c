#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ================= WIFI =================
const char* ssid = "Yashu@123";
const char* password = "123456789";
const char* mqtt_server = "10.111.130.164";

const char* mqtt_user = "iot_user";
const char* mqtt_pass = "iot_pass";

WiFiClient espClient;
PubSubClient client(espClient);

// ================= PINS =================
#define DHTPIN 4
#define DHTTYPE DHT11

#define FLAME_PIN 27
#define PIR_PIN 14
#define IR_PIN 26
#define MQ135_PIN 34

#define BUZZER 25
#define LED_PIN 33

DHT dht(DHTPIN, DHTTYPE);

// ================= STATES =================
int buzzer_mode = 0;
int led_mode = 0;

unsigned long last_cmd_time = 0;

// ================= CALLBACK =================
void callback(char* topic, byte* payload, unsigned int length) {

  String msg = "";
  for (int i = 0; i < length; i++) msg += (char)payload[i];

  StaticJsonDocument<100> doc;
  DeserializationError error = deserializeJson(doc, msg);

  if (!error) {
    buzzer_mode = doc["buzzer_mode"];
    led_mode = doc["led_mode"];

    // Update last command time
    last_cmd_time = millis();
  }
}

// ================= WIFI =================
void setup_wifi() {
  Serial.print("Connecting WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// ================= MQTT =================
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting MQTT...");

    if (client.connect("Node2", mqtt_user, mqtt_pass)) {
      Serial.println("CONNECTED");
      client.subscribe("home/node2/cmd");
    } else {
      Serial.print("FAILED, rc=");
      Serial.print(client.state());
      Serial.println(" → retrying");
      delay(3000);
    }
  }
}

// ================= SETUP =================
void setup() {
  Serial.begin(115200);

  pinMode(FLAME_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(IR_PIN, INPUT);

  pinMode(BUZZER, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  dht.begin();

  setup_wifi();

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

// ================= LOOP =================
void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }

  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  // ================= SENSOR READ =================
  float temp = dht.readTemperature();
  int flame = digitalRead(FLAME_PIN);
  int pir = digitalRead(PIR_PIN);
  int vessel = !digitalRead(IR_PIN);
  int gas = map(analogRead(MQ135_PIN), 0, 4095, 0, 5000);

  // ================= JSON =================
  StaticJsonDocument<200> doc;
  doc["temp"] = temp;
  doc["flame"] = flame;
  doc["pir"] = pir;
  doc["vessel"] = vessel;
  doc["gas"] = gas;

  char buffer[200];
  serializeJson(doc, buffer);

  // ================= DEBUG =================
  Serial.println("\n--- NODE2 DATA ---");
  Serial.println(buffer);

  // ================= PUBLISH =================
  client.publish("home/node2/data", buffer);

  // ================= FAILSAFE =================
  // If no command from edge for 5 sec → turn OFF everything
  if (millis() - last_cmd_time > 5000) {
    buzzer_mode = 0;
    led_mode = 0;
  }

  // ================= ACTUATOR CONTROL =================
  digitalWrite(BUZZER, buzzer_mode == 1);
  digitalWrite(LED_PIN, led_mode == 1);

  delay(2000);
}



