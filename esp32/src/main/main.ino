#include <WiFi.h>
#include <Arduino_LSM6DSOX.h>
#include <PulseSensorPlayground.h>

// constants
const char* ssid = "esp_test";
const char* password = "pctq3111";
const int pulse_threshold = 400;
const int movement_threshold = 9999;


// wire setup 
// avoid using pins 6-11 since it affects memory
// avoid using 0, 2, 15 since it affects boot
const int pulse_wire = A1; // wire that pulse sensor is connected to, change to actual pin later
const int led = 38; // on board RGB led (led on gpio pin 38)

// globals
volatile float x, y, z; // current position variables
PulseSensorPlayground pulse_sensor;

void setup() {
    Serial.begin(115200);
    delay(1000);

    // init code for pulse sensor
    pulse_sensor.analogInput(pulse_wire);
    pulse_sensor.blinkOnPulse(led);
    pulse_sensor.setThreshold(pulse_threshold);

    if (!pulse_sensor.begin()) {
        Serial.println("error while initializing pulse sensor");
    }

    // sets up gpio pins for i2c communication
    Wire.begin(SDA, SCL);

    /*// init code for accelerometer
    // TODO: look at interrupts so that the lsm6ds0x can wake up esp32 when needed
    if (!IMU.begin()) {
        Serial.println("error while initializing lsm6ds0x");
        while (1);
    }
    */
    WiFi.mode(WIFI_STA); // sets esp to station mode so it can connect to internet
    WiFi.begin(ssid, password); // starts up wifi
    Serial.println("\nConnecting"); 

    while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        delay(100);
    }

    Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
}

void loop() {

    /*// test for accelerometer hookup
    if (IMU.accelerationAvailable()) {
        IMU.readAcceleration(x, y, z);
        Serial.print("X: "); Serial.print(x);
        Serial.print(", Y: "); Serial.print(y);
        Serial.print(", Z: "); Serial.println(z);
    }
    */
    if(pulse_sensor.sawStartOfBeat()) {
        int BPM = pulse_sensor.getBeatsPerMinute(); 

        Serial.print("BPM: ");
        Serial.println(BPM);
    }

    delay(20);
}