#include <ArduinoJson.h>
#include <DallasTemperature.h>
#include <EEPROM.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <WiFi.h>
#include "wifi_config.h"  // Local credentials; this file is excluded from Git.

const char *ssid = WIFI_SSID;
const char *password = WIFI_PASSWORD;
const char *serverUrl = AQUAVISION_SERVER_URL;

#define PH_PIN 1
#define TURBIDITY_PIN 2
#define DS18B20_PIN 4
#define VALVE_A_PIN 5
#define VALVE_B_PIN 6
#define EEPROM_ADDR_TARGET_PH 0

#define PH_SLOPE -5.70
#define PH_OFFSET 21.34

float targetPH = 7.0;
const float pH_TOLERANCE = 0.1;
const unsigned long VALVE_OPEN_MS = 5000;
const unsigned long STABILISE_MS = 25000;

OneWire oneWire(DS18B20_PIN);
DallasTemperature sensors(&oneWire);
WiFiClient client;
HTTPClient http;

void connectWiFi();
void readSensors(float &pH, float &temp, int &turbidity);
void sendToServer(float pH, float temp, int turbidity, float target);
void controlpH(float currentPH);
void saveTargetPH(float value);
float loadTargetPH();

void setup() {
  Serial.begin(115200);
  Serial.println("\n[BOOT] AquaVision starting...");

  EEPROM.begin(512);
  targetPH = loadTargetPH();
  Serial.print("[EEPROM] Target pH: ");
  Serial.println(targetPH);

  sensors.begin();
  analogReadResolution(12);
  analogSetPinAttenuation(PH_PIN, ADC_11db);
  analogSetPinAttenuation(TURBIDITY_PIN, ADC_11db);

  pinMode(VALVE_A_PIN, OUTPUT);
  pinMode(VALVE_B_PIN, OUTPUT);
  digitalWrite(VALVE_A_PIN, LOW);
  digitalWrite(VALVE_B_PIN, LOW);

  connectWiFi();
}

void loop() {
  static unsigned long lastRead = 0;
  static unsigned long lastSend = 0;
  static unsigned long lastControl = 0;
  static unsigned long lastWifiRetry = 0;
  unsigned long now = millis();

  if (WiFi.status() != WL_CONNECTED && (now - lastWifiRetry >= 30000)) {
    lastWifiRetry = now;
    connectWiFi();
  }

  if (now - lastRead >= 2000) {
    lastRead = now;
    float pH, temp;
    int turbidity;
    readSensors(pH, temp, turbidity);

    Serial.print("[SENSORS] pH:");
    Serial.print(pH, 2);
    Serial.print("  Temp:");
    Serial.print(temp, 1);
    Serial.print("C  Turbidity:");
    Serial.print(turbidity);
    Serial.print("%  Target:");
    Serial.println(targetPH, 1);

    if (now - lastSend >= 10000 && WiFi.status() == WL_CONNECTED) {
      lastSend = now;
      sendToServer(pH, temp, turbidity, targetPH);
    }

    if (now - lastControl >= 60000) {
      lastControl = now;
      controlpH(pH);
    }
  }

  delay(100);
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED)
    return;
  Serial.print("[WiFi] Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected! IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[WiFi] Failed. Will retry in 30s.");
  }
}

void readSensors(float &pH, float &temp, int &turbidity) {
  sensors.requestTemperatures();
  temp = sensors.getTempCByIndex(0);
  if (temp == DEVICE_DISCONNECTED_C) {
    temp = -999;
    Serial.println("[WARN] DS18B20 disconnected!");
  }

  long phSum = 0;
  for (int i = 0; i < 10; i++) {
    phSum += analogRead(PH_PIN);
    delay(10);
  }
  float phVoltage = (phSum / 10.0 / 4095.0) * 3.3 * 1.5;
  pH = PH_SLOPE * phVoltage + PH_OFFSET;
  pH = constrain(pH, 0.0, 14.0);

  long turbSum = 0;
  for (int i = 0; i < 10; i++) {
    turbSum += analogRead(TURBIDITY_PIN);
    delay(5);
  }
  turbidity = map((int)(turbSum / 10), 500, 3500, 0, 100);
  turbidity = constrain(turbidity, 0, 100);
}

void sendToServer(float pH, float temp, int turbidity, float target) {
  if (WiFi.status() != WL_CONNECTED)
    return;

  StaticJsonDocument<256> doc;
  doc["ph"] = pH;
  doc["temperature"] = temp;
  doc["turbidity"] = turbidity;
  doc["target_ph"] = target;

  String jsonStr;
  serializeJson(doc, jsonStr);

  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "application/json");
  int httpCode = http.POST(jsonStr);

  if (httpCode > 0) {
    String response = http.getString();
    Serial.print("[HTTP] Sent OK. Code: ");
    Serial.println(httpCode);
    StaticJsonDocument<64> respDoc;
    if (!deserializeJson(respDoc, response) &&
        respDoc.containsKey("target_pH")) {
      float newTarget = respDoc["target_pH"];
      if (newTarget >= 4.0 && newTarget <= 10.0 &&
          abs(newTarget - targetPH) > 0.01) {
        targetPH = newTarget;
        saveTargetPH(targetPH);
        Serial.print("[SERVER] New target pH: ");
        Serial.println(targetPH, 2);
      }
    }
  } else {
    Serial.print("[HTTP] Failed. Error: ");
    Serial.println(httpCode);
  }
  http.end();
}

void controlpH(float currentPH) {
  if (currentPH < 0.5 || currentPH > 13.5) {
    Serial.println("[CONTROL] Bad reading, skipping.");
    return;
  }
  if (currentPH < targetPH - pH_TOLERANCE) {
    Serial.println("[CONTROL] pH low -> Valve A open (alkaline)");
    digitalWrite(VALVE_A_PIN, HIGH);
    delay(VALVE_OPEN_MS);
    digitalWrite(VALVE_A_PIN, LOW);
    Serial.println("[CONTROL] Valve A closed. Stabilising...");
    delay(STABILISE_MS);
  } else if (currentPH > targetPH + pH_TOLERANCE) {
    Serial.println("[CONTROL] pH high -> Valve B open (acidic)");
    digitalWrite(VALVE_B_PIN, HIGH);
    delay(VALVE_OPEN_MS);
    digitalWrite(VALVE_B_PIN, LOW);
    Serial.println("[CONTROL] Valve B closed. Stabilising...");
    delay(STABILISE_MS);
  } else {
    Serial.println("[CONTROL] pH in range. No action.");
  }
}

void saveTargetPH(float value) {
  EEPROM.put(EEPROM_ADDR_TARGET_PH, value);
  EEPROM.commit();
  Serial.print("[EEPROM] Saved: ");
  Serial.println(value, 2);
}

float loadTargetPH() {
  float val;
  EEPROM.get(EEPROM_ADDR_TARGET_PH, val);
  if (isnan(val) || val < 4.0 || val > 10.0) {
    val = 7.0;
    saveTargetPH(val);
  }
  return val;
}