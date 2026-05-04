#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// ==========================================
// 1. HARDWARE PINS & OBJECTS
// ==========================================
const int LED_PIN = D5;   
const int LDR_PIN = A0;   

Adafruit_MPU6050 mpu; 

// ==========================================
// 2. GLOBAL STATE
// ==========================================
String led_state = "OFF";
String solar_state = "RETRACTED";
String solar_mode = "MANUAL";

unsigned long last_telem_time = 0; 
const int TELEMETRY_INTERVAL = 100; // 10Hz Refresh Rate

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[INIT] Executing Hard-Bus Reset...");

  // --- THE BUS CLEARING HACK ---
  // We manually toggle the pins to clear any stuck data
  pinMode(D1, OUTPUT);
  for (int i = 0; i < 10; i++) {
    digitalWrite(D1, HIGH); delay(5);
    digitalWrite(D1, LOW);  delay(5);
  }
  
  // --- PRIORITY START ---
  Wire.begin(D2, D1); 
  Wire.setClock(100000); 

  // Give the sensor a massive head start
  delay(2000); 

  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("[ERROR] MPU6050 dropped connection. Bus is hung.");
    // INSTEAD OF FREEZING: Let's try to keep going without the IMU
    // so you can at least use your LED and LDR.
  } else {
    Serial.println("[INIT] MPU6050 IMU Armed and Calibrated.");
    mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  }

  pinMode(LED_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  digitalWrite(LED_PIN, LOW); 
}

void loop() {
  // PHASE A: THE UPLINK
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); 
    
    if (cmd.length() > 0) {
      if (cmd == "LED_ON") { digitalWrite(LED_PIN, HIGH); led_state = "ON"; }
      else if (cmd == "LED_OFF") { digitalWrite(LED_PIN, LOW); led_state = "OFF"; }
      else if (cmd == "DEPLOY_SOLAR") { solar_state = "DEPLOYED"; solar_mode = "MANUAL"; }
      else if (cmd == "RETRACT_SOLAR") { solar_state = "RETRACTED"; solar_mode = "MANUAL"; }
      else if (cmd == "AUTO_SOLAR") { solar_mode = "AUTO"; }
    }
  }

  // PHASE B: AUTONOMOUS LOGIC
  int light_val = analogRead(LDR_PIN);
  if (solar_mode == "AUTO") {
    if (light_val > 600) solar_state = "DEPLOYED";
    else if (light_val < 400) solar_state = "RETRACTED";
  }

  // PHASE C: THE DOWNLINK
  if (millis() - last_telem_time > TELEMETRY_INTERVAL) {
    last_telem_time = millis();

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    float real_pitch = -(atan2(a.acceleration.x, sqrt(a.acceleration.y * a.acceleration.y + a.acceleration.z * a.acceleration.z)) * 180.0) / PI;
    float real_roll  = (atan2(a.acceleration.y, a.acceleration.z) * 180.0) / PI;

    StaticJsonDocument<256> doc;
    doc["pitch"] = real_pitch;
    doc["roll"] = real_roll;
    doc["light"] = light_val;
    
    JsonObject status = doc.createNestedObject("status");
    status["led"] = led_state;
    status["solar"] = solar_state;
    status["mode"] = solar_mode;

    Serial.print("TELEM:");
    serializeJson(doc, Serial);
    Serial.println(); 
  }
}   