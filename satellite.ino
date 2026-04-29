#include <ArduinoJson.h>

// ==========================================
// 1. HARDWARE PIN MAPPING
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
  
  pinMode(LED_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  digitalWrite(LED_PIN, LOW); // Ensure LED is off at boot

  // Allow a moment for the serial port to stabilize
  delay(500); 
  Serial.println("\n[INIT] Hardline Telemetry System Online. Awaiting Python Backend.");
}

void loop() {
  // ==========================================
  // PHASE A: THE UPLINK (Process Serial Commands)
  // ==========================================
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // Clean invisible characters
    
    if (cmd.length() > 0) {
      if (cmd == "LED_ON") { digitalWrite(LED_PIN, HIGH); led_state = "ON"; }
      else if (cmd == "LED_OFF") { digitalWrite(LED_PIN, LOW); led_state = "OFF"; }
      else if (cmd == "DEPLOY_SOLAR") { solar_state = "DEPLOYED"; solar_mode = "MANUAL"; }
      else if (cmd == "RETRACT_SOLAR") { solar_state = "RETRACTED"; solar_mode = "MANUAL"; }
      else if (cmd == "AUTO_SOLAR") { solar_mode = "AUTO"; }
    }
  }

  // ==========================================
  // PHASE B: AUTONOMOUS LOGIC
  // ==========================================
  int light_val = analogRead(LDR_PIN);
  
  if (solar_mode == "AUTO") {
    if (light_val > 600) solar_state = "DEPLOYED";
    else if (light_val < 400) solar_state = "RETRACTED";
  }

  // ==========================================
  // PHASE C: THE DOWNLINK (Send Serial Telemetry)
  // ==========================================
  if (millis() - last_telem_time > TELEMETRY_INTERVAL) {
    last_telem_time = millis();

    StaticJsonDocument<256> doc;
    doc["pitch"] = 15.0 * sin(millis() / 1000.0);
    doc["roll"] = 45.0 * cos(millis() / 2000.0);
    doc["light"] = light_val;
    
    JsonObject status = doc.createNestedObject("status");
    status["led"] = led_state;
    status["solar"] = solar_state;
    status["mode"] = solar_mode;

    // Send the telemetry payload over the hardline
    Serial.print("TELEM:");
    serializeJson(doc, Serial);
    Serial.println(); // Add the newline so Python can read it
  }
}