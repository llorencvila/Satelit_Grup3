#include <Stepper.h>

//define Input pins of the Motor
#define OUTPUT1   7                // Connected to the Blue coloured wire
#define OUTPUT2   6                // Connected to the Pink coloured wire
#define OUTPUT3   5                // Connected to the Yellow coloured wire
#define OUTPUT4   4                // Connected to the Orange coloured wire
const int EchoPin = 10;
const int TriggerPin = 11;
const int stepsPerRotation = 4779;  //com que la transmissió es produeix per engranatges hi ha una relació de de 2.3333 (al ser decimal es perd presisció)´

Stepper myStepper(stepsPerRotation, OUTPUT1, OUTPUT3, OUTPUT2, OUTPUT4); 


int VelMotor = 5; // velocitat màxima (amb la alimentacio del 5v d'arduino), si és més gran el motor es cala
int pos = 0;
int interval = 500;
int Sentit = 1;

unsigned long NextMillis;

void setup() {
  myStepper.setSpeed(VelMotor);
  Serial.begin(9600);

  pinMode(TriggerPin, OUTPUT);
  pinMode(EchoPin, INPUT);

  NextMillis = millis()+interval;
}

void loop() {
  if (pos <=0){
    Sentit = 1;
  }else if (pos >= 4779) {
    Sentit = -1;
  }
  myStepper.step(Sentit * 10);
  pos = pos + (Sentit*10);

  if (millis() >=NextMillis){
  int dist = ping(TriggerPin,EchoPin);
  NextMillis = millis()+interval;
  Serial.print("Dist: ");
  Serial.println(dist);
  Serial.print("Pos: ");
  Serial.println(pos);
      }

  delay(50);


}
int ping(int TriggerPin, int EchoPin) {
  long duration, distCm;
  
  digitalWrite(TriggerPin, LOW);  //para generar un pulso limpio ponemos a LOW 4us
  delayMicroseconds(4);
  digitalWrite(TriggerPin, HIGH);  //generamos Trigger (disparo) de 10us
  delayMicroseconds(10);
  digitalWrite(TriggerPin, LOW);
  
  duration = pulseIn(EchoPin, HIGH);  //medimos el tiempo entre pulsos, en microsegundos
  
  distCm = duration * 10 / 292/ 2;   //convertimos a distancia, en cm
  return distCm;
}

