#include <Arduino_LSM6DSOX.h>
#include <WiFiS3.h>
#include <ArduinoHttpClient.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

#define SECRET_SSID "esp_test"
#define SECRET_PASS "pctq3111"

char ssid[] = SECRET_SSID;
char pass[] = SECRET_PASS;

const char* serverAddress = "54.176.57.40"; // your API server IP
int serverPort = 5000;
String endpoint = "/insert-single/";

// WiFi and HTTP clients
WiFiClient wifi;
HttpClient client = HttpClient(wifi, serverAddress, serverPort);

// NTP client
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000); // UTC, update every 60s

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Start IMU
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (true);
  }

  // Connect to WiFi
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi module not found!");
    while (true);
  }

  Serial.print("Connecting to ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println("\nConnected to WiFi.");
  printWiFiStatus();

  // Start NTP client
  timeClient.begin();
  while (!timeClient.update()) {
    timeClient.forceUpdate();
  }
}

void loop() {
  float x, y, z;

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);

    // Update and format timestamp
    timeClient.update();
    String iso8601 = epochToISOString(timeClient.getEpochTime());

    Serial.print("Sending: ");
    Serial.print(x); Serial.print(", ");
    Serial.print(y); Serial.print(", ");
    Serial.print(z); Serial.print(" @ ");
    Serial.println(iso8601);

    // Create JSON body with timestamp
    String jsonData = "{";
    jsonData += "\"timestamp\": \"" + iso8601 + "\", ";
    jsonData += "\"accel_x\": " + String(x, 3) + ", ";
    jsonData += "\"accel_y\": " + String(y, 3) + ", ";
    jsonData += "\"accel_z\": " + String(z, 3);
    jsonData += "}";

    // Send POST request
    client.beginRequest();
    client.post(endpoint);
    client.sendHeader("Content-Type", "application/json");
    client.sendHeader("Content-Length", jsonData.length());
    client.beginBody();
    client.print(jsonData);
    client.endRequest();

    // Print response
    int statusCode = client.responseStatusCode();
    String response = client.responseBody();
    Serial.print("Status: ");
    Serial.println(statusCode);
    Serial.print("Response: ");
    Serial.println(response);
  }

  delay(1000); // 1 second delay
}

void printWiFiStatus() {
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  long rssi = WiFi.RSSI();
  Serial.print("Signal strength (RSSI): ");
  Serial.print(rssi);
  Serial.println(" dBm");
}

// Converts UNIX time to ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
String epochToISOString(unsigned long epoch) {
  int year, month, day, hour, minute, second;
  unsigned long rawTime = epoch;

  second = rawTime % 60;
  rawTime /= 60;
  minute = rawTime % 60;
  rawTime /= 60;
  hour = rawTime % 24;
  rawTime /= 24;

  // Convert days to date (Unix epoch = Jan 1 1970)
  unsigned long z = rawTime + 719468;
  unsigned long era = (z >= 0 ? z : z - 146096) / 146097;
  unsigned long doe = z - era * 146097;
  unsigned long yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
  year = yoe + era * 400;
  unsigned long doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
  unsigned long mp = (5 * doy + 2) / 153;
  day = doy - (153 * mp + 2) / 5 + 1;
  month = mp < 10 ? mp + 3 : mp - 9;
  if (month <= 2) year++;

  char buf[25];
  snprintf(buf, sizeof(buf), "%04d-%02d-%02dT%02d:%02d:%02dZ",
           year, month, day, hour, minute, second);
  return String(buf);
}