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

bool imu_ready = false;

unsigned long last_telem_time = 0;
unsigned long last_imu_retry_ms = 0;

const int TELEMETRY_INTERVAL = 100;           // 10Hz refresh rate
const unsigned long IMU_RETRY_INTERVAL_MS = 5000;

// ==========================================
// 3. IMU FAULT TOLERANCE
// ==========================================
bool initMpu() {
  if (mpu.begin(0x68, &Wire)) {
    mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    imu_ready = true;
    Serial.println("[INIT] MPU6050 IMU Armed and Calibrated.");
    return true;
  }

  imu_ready = false;
  Serial.println("[WARN] MPU6050 unavailable — entering degraded mode.");
  return false;
}

void attemptImuRecovery() {
  if (imu_ready) {
    return;
  }

  unsigned long now = millis();
  if (now - last_imu_retry_ms < IMU_RETRY_INTERVAL_MS) {
    return;
  }

  last_imu_retry_ms = now;
  Serial.println("[INFO] Retrying MPU6050 init...");

  if (initMpu()) {
    Serial.println("[SUCCESS] MPU6050 recovered — attitude telemetry restored.");
  }
}

void emitTelemetry(int light_val, float pitch, float roll, float yaw, float temp_c) {
  StaticJsonDocument<256> doc;
  doc["pitch"] = pitch;
  doc["roll"] = roll;
  doc["yaw"] = yaw;
  doc["light"] = light_val;
  doc["temp"] = temp_c;

  JsonObject status = doc.createNestedObject("status");
  status["led"] = led_state;
  status["solar"] = solar_state;
  status["mode"] = solar_mode;

  Serial.print("TELEM:");
  serializeJson(doc, Serial);
  Serial.println();
}

// ==========================================
// 4. SETUP
// ==========================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n[INIT] Executing Hard-Bus Reset...");

  // Bus-clearing hack for stuck I2C lines
  pinMode(D1, OUTPUT);
  for (int i = 0; i < 10; i++) {
    digitalWrite(D1, HIGH);
    delay(5);
    digitalWrite(D1, LOW);
    delay(5);
  }

  Wire.begin(D2, D1);
  Wire.setClock(100000);
  delay(2000);

  pinMode(LED_PIN, OUTPUT);
  pinMode(LDR_PIN, INPUT);
  digitalWrite(LED_PIN, LOW);

  last_imu_retry_ms = millis();
  initMpu();
}

// ==========================================
// 5. MAIN LOOP
// ==========================================
void loop() {
  // PHASE A: THE UPLINK
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.length() > 0) {
      if (cmd == "LED_ON") {
        digitalWrite(LED_PIN, HIGH);
        led_state = "ON";
      } else if (cmd == "LED_OFF") {
        digitalWrite(LED_PIN, LOW);
        led_state = "OFF";
      } else if (cmd == "DEPLOY_SOLAR") {
        solar_state = "DEPLOYED";
        solar_mode = "MANUAL";
      } else if (cmd == "RETRACT_SOLAR") {
        solar_state = "RETRACTED";
        solar_mode = "MANUAL";
      } else if (cmd == "AUTO_SOLAR") {
        solar_mode = "AUTO";
      }
    }
  }

  // PHASE B: AUTONOMOUS LOGIC
  int light_val = analogRead(LDR_PIN);
  if (solar_mode == "AUTO") {
    if (light_val > 600) {
      solar_state = "DEPLOYED";
    } else if (light_val < 400) {
      solar_state = "RETRACTED";
    }
  }

  // Periodic auto-recovery while IMU is offline
  attemptImuRecovery();

  // PHASE C: THE DOWNLINK (always 10Hz, even in degraded mode)
  if (millis() - last_telem_time > TELEMETRY_INTERVAL) {
    last_telem_time = millis();

    float real_pitch = 0.0f;
    float real_roll = 0.0f;
    float real_yaw = 0.0f;
    float real_temp = 0.0f;

    if (imu_ready) {
      sensors_event_t a, g, temp;
      mpu.getEvent(&a, &g, &temp);

      real_pitch = -(atan2(a.acceleration.x,
                            sqrt(a.acceleration.y * a.acceleration.y +
                                 a.acceleration.z * a.acceleration.z)) *
                     180.0) / PI;
      real_roll = (atan2(a.acceleration.y, a.acceleration.z) * 180.0) / PI;
      real_temp = temp.temperature;
    }

    emitTelemetry(light_val, real_pitch, real_roll, real_yaw, real_temp);
  }
}
