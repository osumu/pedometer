#include <Wire.h>
#define MPU_ADDR 0x68

float yaw = 0.0;
unsigned long last_time = 0;

void setup() {
  Wire.begin();
  Serial.begin(9600);
  delay(100); 

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B); 
  Wire.write(0);  
  Wire.endTransmission(true);

  last_time = millis();
}

void loop() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B); 
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 14);

  if (Wire.available() == 14) {
    int16_t ax = Wire.read() << 8 | Wire.read();
    int16_t ay = Wire.read() << 8 | Wire.read();
    int16_t az = Wire.read() << 8 | Wire.read();

    int16_t temp_raw = Wire.read() << 8 | Wire.read(); 

    int16_t gx = Wire.read() << 8 | Wire.read();
    int16_t gy = Wire.read() << 8 | Wire.read();
    int16_t gz = Wire.read() << 8 | Wire.read();

    float denominator_pitch = sqrt((float)ay * ay + (float)az * az);
    float denominator_roll  = sqrt((float)ax * ax + (float)az * az);

    float pitch = 0.0, roll = 0.0;
    if (denominator_pitch != 0 && denominator_roll != 0) {
      pitch = atan2((float)ax, denominator_pitch) * 180.0 / PI;
      roll  = atan2((float)ay, denominator_roll) * 180.0 / PI;
    }

    unsigned long now = millis();
    float dt = (now - last_time) / 1000.0;
    last_time = now;

    float gz_dps = gz / 131.0; 
    yaw += gz_dps * dt;

    if (yaw > 180) yaw -= 360;
    if (yaw < -180) yaw += 360;

    float temperature = (temp_raw / 340.0) + 36.53;

    Serial.print(pitch, 1); Serial.print(",");
    Serial.print(roll, 1);  Serial.print(",");
    Serial.print(yaw, 1);   Serial.print(",");
    Serial.println(temperature, 1);
  } else {
    Serial.println("nan,nan,nan,nan");
  }

  delay(50); 
}

