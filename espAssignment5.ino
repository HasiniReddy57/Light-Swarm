//Assignment5 - Code RED
//Author: Akshatha, Swathi, Hasini

/*
Cooperative IOT Self Organizing Example
SwitchDoc Labs, August 2015

 */
// Submission Date: 12/08/2023


#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#define PIN D5 // On Trinket or Gemma, suggest changing this to 1
#define NUMPIXELS 6 // Popular LEDPixel ring size
#define DELAYVAL 500 // Time (in milliseconds) to pause between pixels

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
u8 m_color[5][3] = { {20, 0, 0}, {0, 20, 0}, {0, 0, 20}, {20, 20, 20},{255, 105, 180} };

char ssid[] = "SETUP-2F9E";  //  your network SSID (name)
char pass[] = "coast2961banana";       // your network password
#define PHOTO_RESISTOR A0
#define SWARMSIZE 6
#define SWARMTOOOLD 30000 // 30 seconds is too old - it must be dead
int mySwarmID = 0;
// Packet Types
#define LIGHT_UPDATE_PACKET 0
#define RESET_SWARM_PACKET 1
#define DEFINE_SERVER_LOGGER_PACKET 2
#define LOG_TO_SERVER_PACKET 3
unsigned int localPort = 2910;      // local port to listen for UDP packets
boolean masterState = true;   // True if master, False if not
int swarmSensorValue[SWARMSIZE];
int swarmState[SWARMSIZE];
long swarmTimeStamp[SWARMSIZE];   // for aging
IPAddress serverAddress = IPAddress(0, 0, 0, 0); // default no IP Address
int swarmAddresses[SWARMSIZE];  // Swarm addresses
int sensorReading; // variables for light sensor
const int PACKET_SIZE = 7; // Light Update Packet
const int BUFFERSIZE = 1024;

byte packetBuffer[BUFFERSIZE]; //buffer to hold incoming and outgoing packets

// A UDP instance to let us send and receive packets over UDP
WiFiUDP udp;
IPAddress localIP;

void setup()
{
  Serial.begin(115200);
  pixels.begin(); // INITIALIZE LEDPixel strip object (REQUIRED)
  Serial.println();
  Serial.println();
  Serial.println("");
  Serial.println("--------------------------");
  Serial.println("LightSwarm");
  //Initialising LEDs
  pinMode(D2, OUTPUT);
  pinMode(D4, OUTPUT);
  digitalWrite(D2, LOW);
  delay(500);
  digitalWrite(D2, HIGH);

  digitalWrite(D4, LOW);
  delay(500);
  digitalWrite(D4, HIGH);

  randomSeed(analogRead(A0));
  //randomSeed(100);
  Serial.print("analogRead(A0)=");
  Serial.println(analogRead(A0));
  // everybody starts at 0 and changes from there
  mySwarmID = 0;

  // We start by connecting to a WiFi network
  Serial.print("LightSwarm Instance: ");
  Serial.println(mySwarmID);

  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
 

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");

  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("Starting UDP");

  udp.begin(localPort);
  Serial.print("Local port: ");
  Serial.println(udp.localPort());



  // initialize light sensor and arrays
  int i;
  for (i = 0; i < SWARMSIZE; i++)
  {

    swarmAddresses[i] = 0;
    swarmSensorValue[i] = 0;
    swarmTimeStamp[i] = -1;
  }
  swarmSensorValue[mySwarmID] = 0;
  swarmTimeStamp[mySwarmID] = 1;   // I am always in time to myself
  sensorReading = swarmSensorValue[mySwarmID];
  // swarmVersion[mySwarmID] = VERSIONNUMBER;
  swarmState[mySwarmID] = masterState;
  Serial.print("sensorReading =");
  Serial.println(sensorReading);
  // set SwarmID based on IP address 
  localIP = WiFi.localIP();
  swarmAddresses[0] =  localIP[3];
  mySwarmID = 0;
  Serial.print("MySwarmID=");
  Serial.println(mySwarmID);
}

void loop()
{
  int secondsCount;
  int lastSecondsCount;

  lastSecondsCount = 0;
#define LOGHOWOFTEN
//pixels.clear();
  secondsCount = millis() / 100;
  int sensorValue;
  sensorValue = analogRead(PHOTO_RESISTOR);
  //sensorValue = 567;
  Serial.print("Sensor Value "); Serial.print(sensorValue, DEC); Serial.print(" ");
  sensorReading = sensorValue;
// Calculate the blink delay based on the sensor reading.
  //int blinkDelay = map(sensorValue, 0, 1023, 0, 255); // Adjust the range and values as needed.
  //int outval = map(sensorValue, 0, 1024, 255, 0); 
  //int lightval = constrain(outval, 0,255);
  //digitalWrite(D1, HIGH); // Turn on the LED.
  //delay(blinkDelay); // Wait for the specified delay.
  // Adjust the LED brightness using PWM
  //analogWrite(D2, lightval);

  //digitalWrite(D1, LOW); // Turn off the LED.
  //delay(blinkDelay); // Wait for the same delay.
  // Adjust the LED brightness using PWM
  analogWrite(D2, map(sensorValue, 0, 1023, 0, 255));
  swarmSensorValue[mySwarmID] = sensorReading;

  // wait to see if a reply is available
  delay(300);

  int cb = udp.parsePacket();

  // pixels.clear(); // Set all pixel colors to 'off'
  // for (int i = 0; i < SWARMSIZE; i++){
  //     if (swarmSensorValue[i] > 1000){
  //       //printf("Hey, I'm in if");
  //       pixels.setPixelColor(i, pixels.Color(m_color[0][0], m_color[0][1], m_color[0][2]));
  //     }
  //     else if (swarmSensorValue[i]<=1000 && swarmSensorValue[i]>750){
  //       //printf("Hey, I'm in else if 1");
  //       pixels.setPixelColor(i, pixels.Color(m_color[1][0], m_color[1][1], m_color[1][2]));
  //     }
  //     else if (swarmSensorValue[i]<=750 && swarmSensorValue[i]>500){
  //       //printf("Hey, I'm in else if 2");
  //       pixels.setPixelColor(i, pixels.Color(m_color[2][0], m_color[2][1], m_color[2][2]));
  //     }
  //     else if (swarmSensorValue[i]<=500 && swarmSensorValue[i]>250){
  //       //printf("Hey, I'm in else if 3");
  //       pixels.setPixelColor(i, pixels.Color(m_color[3][0], m_color[3][1], m_color[3][2]));
  //     }
  //     else if (swarmSensorValue[i] <=250){
  //       //printf("Hey, I'm in else if 4");
  //       pixels.setPixelColor(i, pixels.Color(m_color[4][0], m_color[4][1], m_color[4][2]));
  //     }
  //     pixels.show(); // Send the updated pixel colors to the hardware.
  //     // delay(DELAYVAL); // Pause before next pass through loop
  //   }  
  //   // pixels.show(); // Send the updated pixel colors to the hardware.
    // delay(DELAYVAL); // Pause before next pass through loop

  if (!cb) {
    //  Serial.println("no packet yet");
    Serial.print(".");
    pixels.clear(); // Set all pixel colors to 'off'
    // printf("%d, %d\n", swarmClear[0], swarmClear[1]);
    // swarmClear[0] = 1800;
    // swarmClear[1] = 450;
    for (int i = 0; i < SWARMSIZE; i++){
      if (swarmSensorValue[i] > 1000){
        //printf("Hey, I'm in if");
        pixels.setPixelColor(i, pixels.Color(m_color[0][0], m_color[0][1], m_color[0][2]));
      }
      else if (swarmSensorValue[i]<=1000 && swarmSensorValue[i]>750){
        //printf("Hey, I'm in else if 1");
        pixels.setPixelColor(i, pixels.Color(m_color[1][0], m_color[1][1], m_color[1][2]));
      }
      else if (swarmSensorValue[i]<=750 && swarmSensorValue[i]>500){
        //printf("Hey, I'm in else if 2");
        pixels.setPixelColor(i, pixels.Color(m_color[2][0], m_color[2][1], m_color[2][2]));
      }
      else if (swarmSensorValue[i]<=500 && swarmSensorValue[i]>250){
        //printf("Hey, I'm in else if 3");
        pixels.setPixelColor(i, pixels.Color(m_color[3][0], m_color[3][1], m_color[3][2]));
      }
      else if (swarmSensorValue[i] <=250){
        //printf("Hey, I'm in else if 4");
        pixels.setPixelColor(i, pixels.Color(m_color[4][0], m_color[4][1], m_color[4][2]));
      }
      pixels.show(); // Send the updated pixel colors to the hardware.
      // delay(DELAYVAL); // Pause before next pass through loop
    }  
    // pixels.show(); // Send the updated pixel colors to the hardware.
    // delay(DELAYVAL); // Pause before next pass through loop
  }
  else {
    // We've received a packet, read the data from it
    pixels.clear(); // Set all pixel colors to 'off'
    // printf("%d, %d\n", swarmClear[0], swarmClear[1]);
    // swarmClear[0] = 1800;
    // swarmClear[1] = 450;
    for (int i = 0; i < SWARMSIZE; i++){
      if (swarmSensorValue[i] > 1000){
        //printf("Hey, I'm in if");
        pixels.setPixelColor(i, pixels.Color(m_color[0][0], m_color[0][1], m_color[0][2]));
      }
      else if (swarmSensorValue[i]<=1000 && swarmSensorValue[i]>750){
        //printf("Hey, I'm in else if 1");
        pixels.setPixelColor(i, pixels.Color(m_color[1][0], m_color[1][1], m_color[1][2]));
      }
      else if (swarmSensorValue[i]<=750 && swarmSensorValue[i]>500){
        //printf("Hey, I'm in else if 2");
        pixels.setPixelColor(i, pixels.Color(m_color[2][0], m_color[2][1], m_color[2][2]));
      }
      else if (swarmSensorValue[i]<=500 && swarmSensorValue[i]>250){
        //printf("Hey, I'm in else if 3");
        pixels.setPixelColor(i, pixels.Color(m_color[3][0], m_color[3][1], m_color[3][2]));
      }
      else if (swarmSensorValue[i] <=250){
        //printf("Hey, I'm in else if 4");
        pixels.setPixelColor(i, pixels.Color(m_color[4][0], m_color[4][1], m_color[4][2]));
      }
      pixels.show(); // Send the updated pixel colors to the hardware.
      // delay(DELAYVAL); // Pause before next pass through loop
    }  
    // // pixels.show(); // Send the updated pixel colors to the hardware.
    // // delay(DELAYVAL); // Pause before next pass through loop
    udp.read(packetBuffer, PACKET_SIZE); // read the packet into the buffer
    Serial.print("packetbuffer[1] =");
    Serial.println(packetBuffer[1]);
    if (packetBuffer[1] == LIGHT_UPDATE_PACKET)
    {
      Serial.print("LIGHT_UPDATE_PACKET received from LightSwarm #");
      Serial.println(packetBuffer[2]);
      setAndReturnMySwarmIndex(packetBuffer[2]);

      Serial.print("LS Packet Recieved from #");
      Serial.print(packetBuffer[2]);
      Serial.print(" SwarmState:");
      if (packetBuffer[3] == 0)
        Serial.print("SLAVE");
      else
        Serial.print("MASTER");
      Serial.print(" Sensor value:");
      Serial.print(packetBuffer[4] * 256 + packetBuffer[5]);
      swarmSensorValue[setAndReturnMySwarmIndex(packetBuffer[2])] = packetBuffer[4] * 256 + packetBuffer[5];
      swarmState[setAndReturnMySwarmIndex(packetBuffer[2])] = packetBuffer[3];
      swarmTimeStamp[setAndReturnMySwarmIndex(packetBuffer[2])] = millis();
      // Check to see if I am master!
      checkAndSetIfMaster();
    }
    if (packetBuffer[1] == RESET_SWARM_PACKET)
    {
      Serial.println(">>>>>>>>>RESET_SWARM_PACKETPacket Recieved");
      masterState = true;
      Serial.println("Reset Swarm:  I just BECAME Master (and everybody else!)");
      digitalWrite(D2, HIGH);
      digitalWrite(D4, LOW);
      delay(3000);

    }
  if (packetBuffer[1] ==  DEFINE_SERVER_LOGGER_PACKET)
  {
    Serial.println(">>>>>>>>>DEFINE_SERVER_LOGGER_PACKET Packet Recieved");
    serverAddress = IPAddress(packetBuffer[3], packetBuffer[4], packetBuffer[5], packetBuffer[6]);
    Serial.print("Server address received: ");
    Serial.println(serverAddress);
  }
  }
  Serial.print("MasterStatus:");
  if (masterState == true)
  {
    digitalWrite(0, LOW);
    Serial.print("MASTER");
  }
  else
  {
    digitalWrite(0, HIGH);
    Serial.print("SLAVE");
  }
  Serial.print("/Sensor Reading=");
  Serial.print(sensorReading);
  Serial.print("/KS:");
  Serial.println(serverAddress);
  
  Serial.println("--------");
  
  
  int i;
  for (i = 0; i < SWARMSIZE; i++)
  {
    Serial.print("swarmAddress[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.println(swarmAddresses[i]); 
  }
  Serial.println("--------");
  broadcastARandomUpdatePacket();
  sendLogToServer();

}

// send an LIGHT Packet request to the swarms at the given address
unsigned long sendLightUpdatePacket(IPAddress & address)
{
  // set all bytes in the buffer to 0
  memset(packetBuffer, 0, PACKET_SIZE);
  // Initialize values needed to form Light Packet
  // (see URL above for details on the packets)
  packetBuffer[0] = 0xF0;   // StartByte
  packetBuffer[1] = LIGHT_UPDATE_PACKET;     // Packet Type
  packetBuffer[2] = localIP[3];     // Sending Swarm Number
  packetBuffer[3] = masterState;  // 0 = slave, 1 = master
  packetBuffer[4] = (sensorReading & 0xFF00) >> 8; // Sensor reading High Byte
  packetBuffer[5] = (sensorReading & 0x00FF); // Sensor Reading Low Byte
  packetBuffer[6] = 0x0F;  //End Byte

  // all Light Packet fields have been given values, now
  // you can send a packet requesting coordination
  udp.beginPacketMulticast(address,  localPort, WiFi.localIP()); //
  udp.write(packetBuffer, PACKET_SIZE);
  udp.endPacket();
  return 0;
}

void broadcastARandomUpdatePacket()
{

  int sendToLightSwarm = 255;
  //int delayNum;
  Serial.print("Broadcast ToSwarm = ");
  Serial.print(sendToLightSwarm);
  Serial.print(" ");
  unsigned long startTime = millis();
  while (millis() - startTime < 100) {
    if (udp.parsePacket() > 0) {
      // Channel is not silent, exit the loop
      return;
    }
    delay(10);  // Adjust the delay as needed
    //delayNum = random(100);
    //delay(delayNum);
    //Serial.print("delay");
    //Serial.print(delayNum);
  }
  IPAddress sendSwarmAddress(192, 168, 0, sendToLightSwarm); // my Swarm Address
  sendLightUpdatePacket(sendSwarmAddress);
}

void checkAndSetIfMaster()
{

  int i;
  for (i = 0; i < SWARMSIZE; i++)
  {
#ifdef DEBUG

    Serial.print("swarmSensorValue[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.print(swarmSensorValue[i]);
    Serial.print("  swarmTimeStamp[");
    Serial.print(i);
    Serial.print("] = ");
    Serial.println(swarmTimeStamp[i]);
#endif

    Serial.print("#");
    Serial.print(i);
    Serial.print("/");
    Serial.print(swarmState[i]);
    // age data
    int howLongAgo = millis() - swarmTimeStamp[i] ;

    if (swarmTimeStamp[i] == 0)
    {
      Serial.print("TO ");
    }
    else if (swarmTimeStamp[i] == -1)
    {
      Serial.print("NP ");
    }
    else if (swarmTimeStamp[i] == 1)
    {
      Serial.print("ME ");
    }
    else if (howLongAgo > SWARMTOOOLD)
    {
      Serial.print("TO ");
      swarmTimeStamp[i] = 0;
      swarmSensorValue[i] = 0;

    }
    else
    {
      Serial.print("PR ");


    }
  }

  Serial.println();
  boolean setMaster = true;

  for (i = 0; i < SWARMSIZE; i++)
  {
    if (swarmSensorValue[mySwarmID] >= swarmSensorValue[i])
    {
      // I might be master!
      digitalWrite(D4, LOW);

    }
    else
    {
      // nope, not master
      setMaster = false;
      digitalWrite(D4, HIGH);
      break;
    }

  }
  if (setMaster == true)
  {
    if (masterState == false)
    {
      Serial.println("I just BECAME Master");
      digitalWrite(0, LOW);
    }

    masterState = true;
    delay(300);
  }
  else
  {
    if (masterState == true)
    {
      Serial.println("I just LOST Master");
      digitalWrite(0, HIGH);
    }

    masterState = false;
  }

  swarmState[mySwarmID] = masterState;

}
int setAndReturnMySwarmIndex(int incomingID)
{
 
  int i;
  for (i = 0; i< SWARMSIZE; i++)
  {
    if (swarmAddresses[i] == incomingID)
    {
       return i;
    } 
    else
    if (swarmAddresses[i] == 0)  // not in the system, so put it in
    {
    
      swarmAddresses[i] = incomingID;
      Serial.print("incomingID ");
      Serial.print(incomingID);
      Serial.print("  assigned #");
      Serial.println(i);
      return i;
    }
    
  }  
  
  // if we get here, then we have a new swarm member.   
  // Delete the oldest swarm member and add the new one in 
  // (this will probably be the one that dropped out)
  
  int oldSwarmID;
  long oldTime;
  oldTime = millis();
  for (i = 0;  i < SWARMSIZE; i++)
 {
  if (oldTime > swarmTimeStamp[i])
  {
    oldTime = swarmTimeStamp[i];
    oldSwarmID = i;
  }
  
 } 
 
 // remove the old one and put this one in....
 swarmAddresses[oldSwarmID] = incomingID;
 // the rest will be filled in by Light Packet Receive
 return 0;
  
}


// send log packet to Server if master and server address defined

void sendLogToServer()
{

  // build the string

  char myBuildString[1000];
  myBuildString[0] = '\0';

  if (masterState == true)
  {
    digitalWrite(D4, LOW);
    // now check for server address defined
    if ((serverAddress[0] == 0) && (serverAddress[1] == 0))
    {
      return;  // we are done.  not defined
    }
    else
    {
      // now send the packet as a string with the following format:
      // swarmID, MasterSlave, SoftwareVersion, sensorReading, Status | ....next Swarm ID
      // 0,1,15,3883, PR | 1,0,14,399, PR | ...
      int i;
      char swarmString[20];
      swarmString[0] = '\0';

      for (i = 0; i < SWARMSIZE; i++)
      {

        char stateString[5];
        stateString[0] = '\0';
        if (swarmTimeStamp[i] == 0)
        {
          strcat(stateString, "TO");
        }
        else if (swarmTimeStamp[i] == -1)
        {
          strcat(stateString, "NP");
        }
        else if (swarmTimeStamp[i] == 1)
        {
          strcat(stateString, "PR");
        }
        else
        {
          strcat(stateString, "PR");
        }

        sprintf(swarmString, " %i,%i,%i,%s,%i ", i, swarmState[i], swarmSensorValue[i], stateString, swarmAddresses[i]);

        strcat(myBuildString, swarmString);
        if (i < SWARMSIZE - 1)
        {

          strcat(myBuildString, "|");

        }
      }


    }

    // set all bytes in the buffer to 0
    memset(packetBuffer, 0, BUFFERSIZE);
    // Initialize values needed to form Light Packet
    // (see URL above for details on the packets)
    packetBuffer[0] = 0xF0;   // StartByte
    packetBuffer[1] = LOG_TO_SERVER_PACKET;     // Packet Type
    packetBuffer[2] = localIP[3];     // Sending Swarm Number
    packetBuffer[3] = strlen(myBuildString); // length of string in bytes
    int i;
    for (i = 0; i < strlen(myBuildString); i++)
    {
      packetBuffer[i + 4] = myBuildString[i];// first string byte
    }

    packetBuffer[i + 4] = 0x0F; //End Byte
    Serial.print("Sending Log to Sever:");
    Serial.println(myBuildString);
    int packetLength;
    packetLength = i + 5 + 1;
    Serial.print("packetLength");
    Serial.print(packetLength);
    udp.beginPacket(serverAddress,  localPort); //

    udp.write(packetBuffer, packetLength);
    udp.endPacket();

  }
}

