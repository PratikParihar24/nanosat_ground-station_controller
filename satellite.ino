#include <ArduinoJson.h>
#include <Wire.h>

// ==========================================
// 1. HARDWARE PINS
// ==========================================
const int LED_PIN = D5;   
const int LDR_PIN = A0;   

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
  
  // 1. Setup Basic Hardware
  pinMode(LED_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  digitalWrite(LED_PIN, LOW); 

  delay(1000); 
  Serial.println("\n[INIT] Booting...");

  // 2. Start I2C EXACTLY like the Radar script
  Wire.begin(D2, D1); 

  // 3. Wake up the MPU6050 directly (Bypassing Adafruit entirely)
  Wire.beginTransmission(0x68);
  Wire.write(0x6B); // Power Management Register
  Wire.write(0);    // 0 = Wake Up Command
  byte error = Wire.endTransmission();

  if (error != 0) {
    Serial.println("[ERROR] MPU6050 dropped connection. Check wires.");
    while (1) { delay(10); } 
  }
  
  Serial.println("[INIT] Hardline Telemetry System Online.");
  Serial.println("[INIT] MPU6050 Armed via Raw I2C Protocol.");
}

void loop() {
  // ==========================================
  // PHASE A: THE UPLINK (Read Python Commands)
  // ==========================================
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

  // ==========================================
  // PHASE B: AUTONOMOUS LOGIC (LDR)
  // ==========================================
  int light_val = analogRead(LDR_PIN);
  if (solar_mode == "AUTO") {
    if (light_val > 600) solar_state = "DEPLOYED";
    else if (light_val < 400) solar_state = "RETRACTED";
  }

  // ==========================================
  // PHASE C: THE DOWNLINK (Raw Physics Math)
  // ==========================================
  if (millis() - last_telem_time > TELEMETRY_INTERVAL) {
    last_telem_time = millis();

    // 1. Request Raw Accelerometer Data from the I2C Bus
    Wire.beginTransmission(0x68);
    Wire.write(0x3B); // Start reading at the X-Axis register
    Wire.endTransmission(false);
    Wire.requestFrom((uint8_t)0x68, (size_t)6, (bool)true); 

    // 2. Read the 6 bytes of physics data
    int16_t AcX = Wire.read() << 8 | Wire.read();
    int16_t AcY = Wire.read() << 8 | Wire.read();
    int16_t AcZ = Wire.read() << 8 | Wire.read();

    // 3. Convert raw gravity forces to Degrees
    float ax = AcX, ay = AcY, az = AcZ;
    float real_pitch = -(atan2(ax, sqrt(ay * ay + az * az)) * 180.0) / PI;
    float real_roll  = (atan2(ay, az) * 180.0) / PI;

    // 4. Build JSON
    StaticJsonDocument<256> doc;
    doc["pitch"] = real_pitch;
    doc["roll"] = real_roll;
    doc["light"] = light_val;
    
    JsonObject status = doc.createNestedObject("status");
    status["led"] = led_state;
    status["solar"] = solar_state;
    status["mode"] = solar_mode;

    // 5. Fire the umbilical cord
    Serial.print("TELEM:");
    serializeJson(doc, Serial);
    Serial.println(); 
  }
}