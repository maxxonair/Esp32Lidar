/* ------------------------------------------------------------------------------------ */
/*                        [README]
 *                         
 */
/* ------------------------------------------------------------------------------------ */
#include <ESP32Servo.h>
#include "Adafruit_VL53L0X.h"
/* ------------------------------------------------------------------------------------ */
/*                        [CONSTANT DEFINES]
 *                         
 */
/* ------------------------------------------------------------------------------------ */
/* Define digital control pin to control the servo motor */
#define SERVO_CTRL_PIN (13)

#define SERIAL_BAUD_RATE (115200)

/* ------------------------------------------------------------------------------------ */
/*                        [INIT AND SETTINGS]
 *                         
 */
/* ------------------------------------------------------------------------------------ */
/*
 * Unique device identifier
 * This identifier will be added to each serial message
 */
#define DEVICE_ID 605045882

/*
 * Maximum message identifier size 
 * max uint16
 */
#define MAX_MESSAGE_ID 65535

int message_ID = -1;

// Time of flight sensor (VL53L0X)
Adafruit_VL53L0X vl53lox = Adafruit_VL53L0X();
int SHUT_VL = 12;
#define LOX1_ADDRESS 0x30

int prevMeasurement     = -1; 
int frontDistanceTime   = -1;
int prevMeasurementTime = -1;

double distance_mm = 0;

boolean enableDistFront = true;

/* Flag, if enabled print measurements */
int enablePrintMeasurements = 0;

Servo myservo;  // create servo object to control a servo

int minAngle_deg =   0;
int maxAngle_deg = 180;

// [INF] 16 servo objects can be created on the ESP32

/* Create variable to store current servo angle
 * [unit] degree*/
int currServoAngle_deg = 0;   

double trueServoeAngle = -1;

/* Delay between servo command steps 
 * [unit] milli seconds */
int stepDelay_ms = 20;

/* Angular step size magnitude between servo commands 
 * [unit] degree */
int servoStepMagn_deg = 2;

/* Variable to store the temporary step size between servo commands 
 * [unit] degree */
int servoStep_deg = -1;

/* ------------------------------------------------------------------------------------ */
/*                        [INTERNAL FUNCTIONS]
 *                         
 */
/* ------------------------------------------------------------------------------------ */
/*
 * Function: Measure front distance with laser sensor 
 * 
 * Returns: Distance to the nearest obstacle in millimeter
 */
int measFrontDistance(){
  int distance = -1;
  if(enableDistFront)
  {
      VL53L0X_RangingMeasurementData_t measure;
      vl53lox.rangingTest(&measure, false);   
       
      if (measure.RangeStatus != 4) 
      {  
        distance = measure.RangeMilliMeter;
      } 
  }
  return distance;
}

/* Function to increment the message ID index that is send 
 * via serial
 */
void incrementMessageId(){
  if ( message_ID >= MAX_MESSAGE_ID )
  {
    message_ID = 0;
  } else
  {
    message_ID = message_ID + 1;
  }
}

/* Function to compile and send current angle and distance measurements via serial 
 * Also to also print the message if enablePrintMsg is set to 1
 */
void sendSerialMsg(int enablePrintMsg) {
  /* Compose message */
  String msg = "";
  incrementMessageId();
  /*
   * Sensor: N/A
   * Measured: N/A
   * Unit: N/A
   * Frame: N/A
   * Note: Unique device ID
   */
  msg.concat(String(DEVICE_ID));
  msg.concat(",");
  /*
   * Sensor: N/A
   * Measured: N/A
   * Unit: N/A
   * Frame: N/A
   * Note: Unique message ID
   */
  msg.concat(String(message_ID));
  msg.concat(",");
  /*
   * Sensor: Servo 
   * Measured: angle
   * Unit: degree
   * Frame: N/A
   */
  msg.concat(String(trueServoeAngle));
  msg.concat(",");
  /*
   * Sensor: VL53L0X
   * Measured: distance
   * Unit: milli metre
   * Frame: N/A
   */
  msg.concat(String(distance_mm));
  msg.concat("\n");

  if ( enablePrintMsg == 1 ){
    Serial.println(msg);
  }
  /* Send serial message */
  Serial.write(msg.c_str());
}

/* ------------------------------------------------------------------------------------ */
/*                        [SETUP]
 *                         
 */
/* ------------------------------------------------------------------------------------ */
void setup() {

  Serial.begin(SERIAL_BAUD_RATE);
  delay(250);
  
	// Allow allocation of all timers
	ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
 
	myservo.setPeriodHertz(50);    // standard 50 hz servo
  
	myservo.attach(SERVO_CTRL_PIN, 1000, 2000); // attaches the servo on pin 18 to the servo object
	// using default min/max of 1000us and 2000us
	// different servos may require different min/max settings
	// for an accurate 0 to 180 sweep

  vl53lox.begin(LOX1_ADDRESS);

  /* Command servo to zero currServoAngle_degition */
  myservo.write(0);
  delay(1000);
  /* Initialize servo values for startup */
  currServoAngle_deg = 0;
  servoStep_deg = servoStepMagn_deg;
  
}
/* ------------------------------------------------------------------------------------ */
/*                        [LOOP]
 *                         
 */
/* ------------------------------------------------------------------------------------ */
void loop() {

  myservo.write(currServoAngle_deg);   
  delay(stepDelay_ms); 

  /* If max angle is reached -> switch to angle decrement */
  if ( currServoAngle_deg >= maxAngle_deg )
  {
    servoStep_deg = - servoStepMagn_deg;
  }

  /* If min angle is reached -> switch to angle increment */
  if ( currServoAngle_deg <= minAngle_deg )
  {
    servoStep_deg = servoStepMagn_deg;
  }

  /* Call distance measurement */
  distance_mm = measFrontDistance();

  /* Send measurements as serial message */
  sendSerialMsg(enablePrintMeasurements);

  /* Update servo angle for next iteration */
  currServoAngle_deg += servoStep_deg;

  /* Calculate true angle since servo output atm si not what it's supposed to be */
  trueServoeAngle = currServoAngle_deg / 2;
}