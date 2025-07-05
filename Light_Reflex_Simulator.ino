#include <Servo.h>

// === Pin Definitions ===
// LDR Analog Inputs
const int ldrLeftPin = A0;
const int ldrRightPin = A1;

// Servo Outputs
const int servoLeftPin = 9;
const int servoRightPin = 10;

// Lesion Pathway Control Pins (Arduino will control these as OUTPUTs to turn LEDs ON/OFF)
// HIGH = OK (LED ON), LOW = Lesion (LED OFF)
const int opticNerveLeftPin = 2;   // Optic Nerve Left Pathway LED (formerly Afferent Left)
const int opticNerveRightPin = 3;  // Optic Nerve Right Pathway LED (formerly Afferent Right)
const int ptnLeftPin = 4;        // Pretectal Nucleus Left Pathway LED
const int ptnRightPin = 5;       // Pretectal Nucleus Right Pathway LED
const int ewpLeftPin = 6;        // Edinger-Westphal Nucleus Left Pathway LED
const int ewpRightPin = 7;       // Edinger-Westphal Nucleus Right Pathway LED
const int cn3LeftPin = 8;        // 3rd Cranial Nerve Left Pathway LED
const int cn3RightPin = 11;      // 3rd Cranial Nerve Right Pathway LED // Corrected: Removed duplicate 'int'

// === Tweakable Light Intensity Thresholds (LDR values are inverse to light intensity) ===
// These will be adjusted by the GUI. Default values:
int HIGH_INTENSITY_LDR_THRESHOLD = 400; // LDR values BELOW this mean high light (pupil constricts)
int LOW_INTENSITY_LDR_THRESHOLD  = 600; // LDR values ABOVE this mean low light (pupil dilates)

// === Fixed Servo Limits for Reflex Mode ===
// Servos will operate between these angles for constriction/dilation.
const int SERVO_MIN_ANGLE = 20;  // Corresponds to fully constricted pupil
const int SERVO_MAX_ANGLE = 170; // Corresponds to fully dilated pupil

// === Servo Objects ===
Servo leftIris;
Servo rightIris;

// === Enums for better readability ===
enum LightLevel {
  NO_STIMULUS,
  LOW_LIGHT,
  AMBIENT_LIGHT,
  HIGH_LIGHT
};

// Operating mode is now fixed to REFLEX_MODE as per GUI simplification
// enum OperatingMode {
//   REFLEX_MODE,
//   MANUAL_MODE
// };
// OperatingMode currentOperatingMode = REFLEX_MODE; // Always REFLEX_MODE

// --- Serial Command Parsing (Memory Optimized) ---
const byte SERIAL_BUFFER_SIZE = 64; // Max command length + null terminator
char inputBuffer[SERIAL_BUFFER_SIZE];
byte bufferIndex = 0;
bool stringComplete = false;

void setup() {
  Serial.begin(9600);
  while (!Serial); // Wait for serial port to connect (Leonardo/Micro)

  leftIris.attach(servoLeftPin);
  rightIris.attach(servoRightPin);

  // Configure lesion control pins as OUTPUTs (explicitly for LEDs)
  pinMode(opticNerveLeftPin, OUTPUT);
  pinMode(opticNerveRightPin, OUTPUT);
  pinMode(ptnLeftPin, OUTPUT);
  pinMode(ptnRightPin, OUTPUT);
  pinMode(ewpLeftPin, OUTPUT);
  pinMode(ewpRightPin, OUTPUT);
  pinMode(cn3LeftPin, OUTPUT);
  pinMode(cn3RightPin, OUTPUT); // Corrected: cn3RightPin is now properly declared

  // Initial state of LEDs: All INTACT (LED ON, HIGH) until GUI sends commands
  // This will be set by the GUI on connection.
  digitalWrite(opticNerveLeftPin, HIGH);
  digitalWrite(opticNerveRightPin, HIGH);
  digitalWrite(ptnLeftPin, HIGH);
  digitalWrite(ptnRightPin, HIGH);
  digitalWrite(ewpLeftPin, HIGH);
  digitalWrite(ewpRightPin, HIGH);
  digitalWrite(cn3LeftPin, HIGH);
  digitalWrite(cn3RightPin, HIGH);

  // Set initial positions for both servos to their mid-range (dilated or mid-range)
  // angleToServo(0) maps to the middle of the SERVO_MIN_ANGLE and SERVO_MAX_ANGLE range
  leftIris.write(angleToServo(0));
  rightIris.write(angleToServo(0));

  Serial.println(F("Arduino Iris Reflex Simulation Ready.")); // F() macro to save PROGMEM
  Serial.println(F("Operating Mode: REFLEX_MODE (Fixed)")); // F() macro to save PROGMEM
}

void loop() {
  serialEvent(); // Check for incoming serial data

  if (stringComplete) {
    processCommand(inputBuffer); // Pass the C-style string
    bufferIndex = 0; // Reset buffer index
    stringComplete = false;
    memset(inputBuffer, 0, SERIAL_BUFFER_SIZE); // Clear the buffer
  }

  // Common operations: Read LDR values
  int leftLDR = analogRead(ldrLeftPin);
  int rightLDR = analogRead(ldrRightPin);

  // Variables to hold calculated angles in conceptual -90 to +90 range
  int calculatedAngleLeft = 0; // Default to mid-range (0 conceptual angle)
  int calculatedAngleRight = 0; // Default to mid-range (0 conceptual angle)

  // === Read the states of all pathway control pins ===
  // A HIGH signal means the pathway is INTACT (LED ON)
  // A LOW signal means the pathway has a LESION (LED OFF)
  bool opticNerveL_OK = digitalRead(opticNerveLeftPin) == HIGH;
  bool opticNerveR_OK = digitalRead(opticNerveRightPin) == HIGH;
  bool ptnLeft_OK = digitalRead(ptnLeftPin) == HIGH;
  bool ptnRight_OK = digitalRead(ptnRightPin) == HIGH;
  bool ewpLeft_OK = digitalRead(ewpLeftPin) == HIGH;
  bool ewpRight_OK = digitalRead(ewpRightPin) == HIGH;
  bool cn3Left_OK = digitalRead(cn3LeftPin) == HIGH;
  bool cn3Right_OK = digitalRead(cn3RightPin) == HIGH; // Corrected: cn3RightPin is now properly declared

  // === Assess Optic Nerve Pathway Integrity ===
  // Both optic nerve and pretectal nucleus pathways must be intact for light stimulus to be registered
  bool leftOpticNervePathwayIntact = opticNerveL_OK && ptnLeft_OK;
  bool rightOpticNervePathwayIntact = opticNerveR_OK && ptnRight_OK;

  // === Determine the OVERALL (Global) Light Level ===
  LightLevel currentGlobalLightLevel = NO_STIMULUS;

  // Logic for determining global light level based on LDR readings and intact optic nerve pathways
  if ((leftLDR < HIGH_INTENSITY_LDR_THRESHOLD && leftOpticNervePathwayIntact) ||
      (rightLDR < HIGH_INTENSITY_LDR_THRESHOLD && rightOpticNervePathwayIntact)) {
    currentGlobalLightLevel = HIGH_LIGHT;
  } else if ((leftLDR >= HIGH_INTENSITY_LDR_THRESHOLD && leftLDR <= LOW_INTENSITY_LDR_THRESHOLD && leftOpticNervePathwayIntact) ||
             (rightLDR >= HIGH_INTENSITY_LDR_THRESHOLD && rightLDR <= LOW_INTENSITY_LDR_THRESHOLD && rightOpticNervePathwayIntact)) {
    currentGlobalLightLevel = AMBIENT_LIGHT;
  } else if ((leftLDR > LOW_INTENSITY_LDR_THRESHOLD && leftOpticNervePathwayIntact) ||
             (rightLDR > LOW_INTENSITY_LDR_THRESHOLD && rightOpticNervePathwayIntact)) {
    currentGlobalLightLevel = LOW_LIGHT;
  }

  // === Apply reflex logic to iris constriction ===
  // Left Iris Reflex
  if (ewpLeft_OK && cn3Left_OK) { // Check if left efferent pathway (EWP and CN3) is intact
    switch (currentGlobalLightLevel) {
      case HIGH_LIGHT:    calculatedAngleLeft = -90; break; // Constrict fully (maps to SERVO_MIN_ANGLE)
      case AMBIENT_LIGHT: calculatedAngleLeft = 0;   break; // Midline (maps to middle of SERVO_MIN/MAX)
      case LOW_LIGHT:     calculatedAngleLeft = 90;  break; // Dilate fully (maps to SERVO_MAX_ANGLE)
      case NO_STIMULUS:
      default:            calculatedAngleLeft = 90;  break; // No stimulus or optic nerve lesion, remains dilated
    }
  } else {
    calculatedAngleLeft = 90; // Lesion present in efferent pathway, stays dilated
  }

  // Right Iris Reflex
  if (ewpRight_OK && cn3Right_OK) { // Check if right efferent pathway (EWP and CN3) is intact
    switch (currentGlobalLightLevel) {
      case HIGH_LIGHT:    calculatedAngleRight = -90; break; // Constrict fully (maps to SERVO_MIN_ANGLE)
      case AMBIENT_LIGHT: calculatedAngleRight = 0;   break; // Midline (maps to middle of SERVO_MIN/MAX)
      case LOW_LIGHT:     calculatedAngleRight = 90;  break; // Dilate fully (maps to SERVO_MAX_ANGLE)
      case NO_STIMULUS:
      default:            calculatedAngleRight = 90;  break; // No stimulus or optic nerve lesion, remains dilated
    }
  } else {
    calculatedAngleRight = 90; // Lesion present in efferent pathway, stays dilated
  }

  // Convert conceptual angles to servo 0-180 range (which is now 20-170)
  int finalServoLeftAngle = angleToServo(calculatedAngleLeft);
  int finalServoRightAngle = angleToServo(calculatedAngleRight);

  // Apply calculated angles to servos
  leftIris.write(finalServoLeftAngle);
  rightIris.write(finalServoRightAngle);

  // === Send Consolidated Data to GUI ===
  // This helps the GUI parse data efficiently
  // Using F() macro for constant strings to store them in Flash (PROGMEM)
  // which saves precious SRAM.
  Serial.print(F("DATA|"));
  Serial.print(F("LDR_L:")); Serial.print(leftLDR);
  Serial.print(F(",LDR_R:")); Serial.print(rightLDR);
  Serial.print(F("|MODE:REFLEX")); // Mode is fixed to REFLEX
  
  // Send lesion states
  Serial.print(F("|ONL:")); Serial.print(digitalRead(opticNerveLeftPin) == HIGH ? F("1") : F("0"));
  Serial.print(F(",ONR:")); Serial.print(digitalRead(opticNerveRightPin) == HIGH ? F("1") : F("0"));
  Serial.print(F(",PTNL:")); Serial.print(digitalRead(ptnLeftPin) == HIGH ? F("1") : F("0"));
  Serial.print(F(",PTNR:")); Serial.print(digitalRead(ptnRightPin) == HIGH ? F("1") : F("0"));
  Serial.print(F(",EWPL:")); Serial.print(digitalRead(ewpLeftPin) == HIGH ? F("1") : F("0"));
  Serial.print(F(",EWPR:")); Serial.print(digitalRead(ewpRightPin) == HIGH ? F("1") : F("0"));
  Serial.print(F(",CN3L:")); Serial.print(digitalRead(cn3LeftPin) == HIGH ? F("1") : F("0"));
  Serial.print(F(",CN3R:")); Serial.print(digitalRead(cn3RightPin) == HIGH ? F("1") : F("0")); // Corrected: cn3RightPin is now properly declared

  Serial.print(F("|GLL:")); 
  // Re-calculate debugGlobalLightLevel for consistent output
  LightLevel debugGlobalLightLevel = NO_STIMULUS;
  if ((leftLDR < HIGH_INTENSITY_LDR_THRESHOLD && leftOpticNervePathwayIntact) ||
      (rightLDR < HIGH_INTENSITY_LDR_THRESHOLD && rightOpticNervePathwayIntact)) {
    debugGlobalLightLevel = HIGH_LIGHT;
  } else if ((leftLDR >= HIGH_INTENSITY_LDR_THRESHOLD && leftLDR <= LOW_INTENSITY_LDR_THRESHOLD && leftOpticNervePathwayIntact) ||
             (rightLDR >= HIGH_INTENSITY_LDR_THRESHOLD && rightLDR <= LOW_INTENSITY_LDR_THRESHOLD && rightOpticNervePathwayIntact)) {
    debugGlobalLightLevel = AMBIENT_LIGHT;
  } else if ((leftLDR > LOW_INTENSITY_LDR_THRESHOLD && leftOpticNervePathwayIntact) ||
             (rightLDR > LOW_INTENSITY_LDR_THRESHOLD && rightOpticNervePathwayIntact)) {
    debugGlobalLightLevel = LOW_LIGHT;
  }
  
  if (debugGlobalLightLevel == HIGH_LIGHT) Serial.print(F("HIGH_LIGHT"));
  else if (debugGlobalLightLevel == AMBIENT_LIGHT) Serial.print(F("AMBIENT_LIGHT"));
  else if (debugGlobalLightLevel == LOW_LIGHT) Serial.print(F("LOW_LIGHT"));
  else Serial.print(F("NO_STIMULUS"));
  
  int currentServoL = leftIris.read(); // Read current actual servo position
  int currentServoR = rightIris.read();
  
  Serial.print(F("|AngleL:")); Serial.print(calculatedAngleLeft); // Conceptual angle
  Serial.print(F(",AngleR:")); Serial.print(calculatedAngleRight); // Conceptual angle
  Serial.print(F(",ServoL:")); Serial.print(currentServoL);    // Actual servo angle
  Serial.print(F(",ServoR:")); Serial.println(currentServoR);    // Actual servo angle


  // Optional: Extensive debug print (also using F() for PROGMEM)
  Serial.print(F("DBG|"));
  Serial.print(F("LDR_L: ")); Serial.print(leftLDR);
  Serial.print(F(" | LDR_R: ")); Serial.print(rightLDR);
  Serial.print(F(" | OpticNerve_L_OK: ")); Serial.print(opticNerveL_OK ? F("OK") : F("Lesion"));
  Serial.print(F(" | OpticNerve_R_OK: ")); Serial.print(opticNerveR_OK ? F("OK") : F("Lesion"));
  Serial.print(F(" | PTN_L_OK: ")); Serial.print(ptnLeft_OK ? F("OK") : F("Lesion"));
  Serial.print(F(" | PTN_R_OK: ")); Serial.print(ptnRight_OK ? F("OK") : F("Lesion"));
  Serial.print(F(" | EWP_L_OK: ")); Serial.print(ewpLeft_OK ? F("OK") : F("Lesion"));
  Serial.print(F(" | EWP_R_OK: ")); Serial.print(ewpRight_OK ? F("OK") : F("Lesion"));
  Serial.print(F(" | CN3_L_OK: ")); Serial.print(cn3Left_OK ? F("OK") : F("Lesion"));
  Serial.print(F(" | CN3_R_OK: ")); Serial.print(cn3Right_OK ? F("OK") : F("Lesion")); // Corrected: cn3RightPin is now properly declared
  Serial.print(F(" | Global_Light_Level: "));
  if (debugGlobalLightLevel == HIGH_LIGHT) Serial.print(F("HIGH_LIGHT"));
  else if (debugGlobalLightLevel == AMBIENT_LIGHT) Serial.print(F("AMBIENT_LIGHT"));
  else if (debugGlobalLightLevel == LOW_LIGHT) Serial.print(F("LOW_LIGHT"));
  else Serial.print(F("NO_STIMULUS"));
  Serial.print(F(" | Angle_L (deg): ")); Serial.print(calculatedAngleLeft);
  Serial.print(F(" | Angle_R (deg): ")); Serial.print(calculatedAngleRight);
  Serial.print(F(" | Servo_L (20-170): ")); Serial.print(currentServoL);
  Serial.print(F(" | Servo_R (20-170): ")); Serial.println(currentServoR);


  delay(150); // Small delay to stabilize readings and avoid flickering
}

// === Helper function to convert conceptual angle (-90 to +90) into servo signal (20-170) ===
int angleToServo(int angle) {
  // Map -90 (constricted) to SERVO_MIN_ANGLE (20)
  // Map +90 (dilated) to SERVO_MAX_ANGLE (170)
  return map(angle, -90, 90, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE);
}

// === Serial Event Handler (for C-style string) ===
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    // If the buffer is not full and it's not a newline, add character
    if (inChar != '\n' && bufferIndex < SERIAL_BUFFER_SIZE - 1) {
      inputBuffer[bufferIndex++] = inChar;
    } else if (inChar == '\n') {
      inputBuffer[bufferIndex] = '\0'; // Null-terminate the string
      stringComplete = true;
    }
  }
}

// === Command Processing Function (for C-style string) ===
void processCommand(char* command) {
  // Use C-string functions (strstr, sscanf, atoi)
  // strstr returns a pointer to the first occurrence of the substring, or NULL if not found.

  // SET_LDR_THRESH command
  if (strstr(command, "SET_LDR_THRESH:") == command) {
    int high, low;
    // sscanf is powerful for parsing formatted strings
    if (sscanf(command, "SET_LDR_THRESH:%d,%d", &high, &low) == 2) {
      HIGH_INTENSITY_LDR_THRESHOLD = high;
      LOW_INTENSITY_LDR_THRESHOLD = low;
      Serial.print(F("LDR Thresholds set: High="));
      Serial.print(HIGH_INTENSITY_LDR_THRESHOLD);
      Serial.print(F(", Low="));
      Serial.println(LOW_INTENSITY_LDR_THRESHOLD);
    } else {
      Serial.println(F("Error: Invalid SET_LDR_THRESH format. Use SET_LDR_THRESH:<high>,<low>"));
    }
  }
  // SET_PIN_STATE command (for lesion switches)
  else if (strstr(command, "SET_PIN_STATE:") == command) {
    int pinNum, state;
    if (sscanf(command, "SET_PIN_STATE:%d,%d", &pinNum, &state) == 2) {
      // Check if the pin number is one of the defined lesion control pins
      if (pinNum == opticNerveLeftPin || pinNum == opticNerveRightPin || // Updated pin names
          pinNum == ptnLeftPin || pinNum == ptnRightPin ||
          pinNum == ewpLeftPin || pinNum == ewpRightPin ||
          pinNum == cn3LeftPin || pinNum == cn3RightPin) { // Corrected: cn3RightPin is now properly declared
        digitalWrite(pinNum, (state == 1) ? HIGH : LOW); // 1 (HIGH) = INTACT (LED ON), 0 (LOW) = LESION (LED OFF)
        Serial.print(F("Pin "));
        Serial.print(pinNum);
        Serial.print(F(" set to "));
        Serial.println(state == 1 ? F("HIGH (INTACT, LED ON)") : F("LOW (LESION, LED OFF)"));
      } else {
        Serial.print(F("Error: Invalid pin number for lesion control: "));
        Serial.println(pinNum);
      }
    } else {
      Serial.println(F("Error: Invalid SET_PIN_STATE format. Use SET_PIN_STATE:<pin>,<state>"));
    }
  }
  // All other commands are now considered unknown as manual mode is removed
  else {
    Serial.print(F("Unknown command: "));
    Serial.println(command);
  }
}
