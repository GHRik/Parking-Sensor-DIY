#include <ESP8266WiFi.h>
#include "PubSubClient.h"

int trigPin = 2;
int echoPin = 4;

const char* ssid; 
const char* password;

const char* mqttServer;
int mqttPort;
const char* mqttUser;
const char* mqttPassword;
WiFiClient espClient;
PubSubClient client(espClient);


long duration = -1;
float distance = -1;

void setupWiFiConnection();
void printLocalAdress();
void setupMqttConnection();
void callback(char* topic, byte* payload, unsigned int length);
void checkMqtt();
float getDistanceFromSensor();

int flag = 1;

void setup() {
  pinMode(trigPin, OUTPUT); 
  pinMode(echoPin, INPUT); 
  //Serial.begin(115200); // Starts the serial communication
  
  setupWiFiConnection();
  
  setupMqttConnection(); 
  checkMqtt();
  
}


void loop() {

   client.loop();

  if (!client.connected()) 
  {
  reconnect();
  }

  distance = getDistanceFromSensor();
  
  //Distance to charArray, its not working in function.
  String value(distance);
  value += "\0";
  char publishValue[20];
  value.toCharArray(publishValue,20);
  
  if(flag == 1){
    client.publish("Distance", publishValue);
    }
  else if(flag == -1)
    client.publish("Distance", "-100");
  delay(1000);  
}





void setupWiFiConnection(){
  ssid = "Zakochani";
  password = "Monika2609";
  /*Serial.println();
  Serial.println();
  Serial.print("Your are connecting to;");
  Serial.println(ssid);*/
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    //Serial.print(".");
  }
}

void printLocalAdress(){
  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.print("IP address: ");
  Serial.print(WiFi.localIP());
}

 
void setupMqttConnection(){
  mqttServer = "m21.cloudmqtt.com";
  mqttPort = 12528;
  mqttUser = "NodeMcu";
  mqttPassword = "nodemcu";
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
  
}

void callback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
    message += ((char)payload[i]);
  }

    if(message == "0"){
      flag = -1;
    }
    else if(message == "1"){
      flag = 1;
    }

}

void checkMqtt(){
  while (!client.connected()) {
   // Serial.println("Connecting to MQTT: ");
 
    if(client.connect("NodeMcu2", mqttUser, mqttPassword )) {
     // Serial.println("connected");  
    }
    else{
    //  Serial.print("failed with state ");
     // Serial.print(client.state());
      delay(2000);
    }
  }
  client.subscribe("Command");
}


float getDistanceFromSensor(){
    // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculating the distance
  distance= duration*0.034/2;
  
  return distance;
}

boolean reconnect() {
  if (client.connect("ESP8266Client")) {
    // Once connected, publish an announcement...
    client.publish("Command", "Hello");
    // ... and resubscribe
    client.subscribe("Command");
  }
  return client.connected();
}

