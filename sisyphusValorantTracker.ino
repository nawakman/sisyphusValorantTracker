/*******************************************************************
    A sample project for making a HTTP/HTTPS GET request on an ESP32
    and parsing it from JSON

    It will connect to the given request, parse the JSON and print the 
    body to serial monitor

    Parts:
    ESP32 Dev Board
       Aliexpress: * - https://s.click.aliexpress.com/e/_dSi824B
       Amazon: * - https://amzn.to/3gArkAY

 *  * = Affilate

    If you find what I do useful and would like to support me,
    please consider becoming a sponsor on Github
    https://github.com/sponsors/witnessmenow/


    Written by Brian Lough
    YouTube: https://www.youtube.com/brianlough
    Tindie: https://www.tindie.com/stores/brianlough/
    Twitter: https://twitter.com/witnessmenow
 *******************************************************************/


// ----------------------------
// Standard Libraries
// ----------------------------

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <ESP32Servo.h>
//#include <ArduinoJson.h>

//------- Replace the following! ------
char ssid[] = "Livebox-4A40";       // your network SSID (name)
char password[] = "KxNk9xMbs9ZcSu2qvD";  // your network key
const int servoSpeed=40;

// For Non-HTTPS requests
// WiFiClient client;

// For HTTPS requests
WiFiClientSecure client;
//WiFiClient client;
Servo servo;


// Just the base of the URL you want to connect to
#define TEST_HOST "unscintillating-angelica-gabelled.ngrok-free.dev"

void setup() {

  Serial.begin(115200);

  // Connect to the WiFI
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.println("");

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  servo.attach(13, 500, 2400); // Attach with min/max pulse widths

  //client.setCACert(server_cert);
  //OR
  client.setInsecure();

  makeHTTPRequest();
  esp_sleep_enable_timer_wakeup(10*60*1000000);//1 seconds = 1,000,000 microseconds
  esp_deep_sleep_start();
}

void loop(){//because it needs to exist apparently

}

void makeHTTPRequest() {
  const unsigned long timeout = 5000; //timeout before giving up on response
  unsigned long startTime = millis();
  // Opening connection to server (Use 80 as port if HTTP)
  if (!client.connect(TEST_HOST, 443)) //443 for https
  {
    Serial.println(F("Connection failed"));
    return;
  }

  // give the esp a breather
  yield();
  
  // Send HTTP request
  client.print(F("GET "));
  // This is the second half of a request (everything that comes after the base URL)
  client.print("/get-stats"); // %2C == ,
  client.println(F(" HTTP/1.1"));

  //Headers
  client.print(F("Host: "));
  client.println(TEST_HOST);

  client.println(F("Cache-Control: no-cache"));

  if (client.println() == 0)
  {
    Serial.println(F("Failed to send request"));
    return;
  }
  
  while (client.available() == 0) {
    if (millis() - startTime > timeout) {
      Serial.println(F("http response timeout"));
      client.stop();
      return;
    }
    delay(10);
  }

  // Check HTTP status
  char status[32] = {0};
  client.readBytesUntil('\r', status, sizeof(status));
  if (strcmp(status, "HTTP/1.1 200 OK") != 0)
  {
    Serial.print(F("Unexpected response: "));
    Serial.println(status);
    return;
  }

  // Skip HTTP headers
  char endOfHeaders[] = "\r\n\r\n";
  if (!client.find(endOfHeaders))
  {
    Serial.println(F("Invalid response"));
    return;
  }

  String response = client.readString();
  response.trim(); // Vital: removes hidden \r or \n characters
  Serial.println(response);
  servoMovements(response);
}

void servoMovements(String response){
  servo.attach(13);
  if(response=="victory"){
    servo.write(90+servoSpeed);
    delay(2000);
    servo.write(0);
  }else if (response=="defeat"){
    servo.write(90-servoSpeed);
    delay(2000);
    servo.write(0);
  }else if (response=="draw"){
    servo.write(90-servoSpeed);
    delay(500);
    servo.write(90+servoSpeed);
    delay(500);
    servo.write(90-servoSpeed);
    delay(500);
    servo.write(90+servoSpeed);
    delay(500);
    servo.write(0);
  }
  servo.detach();
}