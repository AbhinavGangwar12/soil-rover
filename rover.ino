#include <DHT.h>           
#include <SoftwareSerial.h> 

// Phase 1: Global Definitions
const int ENA = 9;  const int IN1 = 3;  const int IN2 = 4;  
const int ENB = 10; const int IN3 = 5;  const int IN4 = 6;  
#define DHTPIN 7       
#define DHTTYPE DHT11
#define MOIST_PIN A0   
SoftwareSerial BTSerial(12, 11); 
DHT dht(DHTPIN, DHTTYPE);

// --- THE SER DUNCAN POWER LIMITERS ---
// Max PWM is 255. We use 120 to throttle the 16V battery down to ~7.5V.
const int duncanMaxSpeed = 120;  
const int duncanTurnSpeed = 90;  // Slower speed for stable, controlled turns

// Phase 2: Setup (Runs once)
void setup() {
  Serial.begin(9600);   
  BTSerial.begin(9600); 
  dht.begin();          
  pinMode(ENA, OUTPUT); pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT); pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  
  // Safety: Ensure motors are fully stopped on boot
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  Serial.println("Rover System Ready. Awaiting Command.");
}

// Phase 5: The Main Loop (Runs forever)
void loop() {
  // Listen for Bluetooth Steering Commands
  if (BTSerial.available()) {
    char cmd = BTSerial.read();
    moveRover(cmd);
  }
  
  // Read and Transmit Sensor Data Every 5 Seconds
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck > 5000) {
    collectData();
    lastCheck = millis();
  }
}

// Phase 3: Movement Logic
void moveRover(char command) {
  if (command == 'F') { // Forward
    analogWrite(ENA, duncanMaxSpeed); digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    analogWrite(ENB, duncanMaxSpeed); digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    
  } else if (command == 'B') { // Backward
    analogWrite(ENA, duncanMaxSpeed); digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    analogWrite(ENB, duncanMaxSpeed); digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    
  } else if (command == 'L') { // Tank Turn Left
    analogWrite(ENA, duncanTurnSpeed); digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
    analogWrite(ENB, duncanTurnSpeed); digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
    
  } else if (command == 'R') { // Tank Turn Right
    analogWrite(ENA, duncanTurnSpeed); digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
    analogWrite(ENB, duncanTurnSpeed); digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
    
  } else if (command == 'S') { // Stop
    analogWrite(ENA, 0); digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
    analogWrite(ENB, 0); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  }
}

// Phase 4: ML Data Package
void collectData() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int m = analogRead(MOIST_PIN);
  
  // Failsafe: If the sensor wire wiggles loose, send "nan" to avoid crashing the Python ML model
  if (isnan(h) || isnan(t)) {
    String errData = "nan,nan,nan,nan";
    BTSerial.println(errData);
    Serial.println(errData);
    return;
  }
  
  float hi = dht.computeHeatIndex(t, h, false);
  
  // Package into CSV: Temp, Humidity, Moisture, HeatIndex
  String data = String(t) + "," + String(h) + "," + String(m) + "," + String(hi);
  
  BTSerial.println(data);
  Serial.println(data);
}
