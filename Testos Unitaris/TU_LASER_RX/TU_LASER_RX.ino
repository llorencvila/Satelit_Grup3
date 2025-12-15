/*
const int LEDPin = 13;
const int LDRPin = A0;
const int background = 0;
long nextMillis = 0;
long NextBitMillis = 0;
int interval = 1000;
int umbralDetecio = 1.25; //Es considerarà com a detecció quan els valors sobrepassin aquest tan percert del valor base
float BitRate = 100; //Temps que triga a enviar cada bit 

int rebuda(){
  int input = analogRead(LDRPin);

  int missatgeRebut[7]; //7 pq és la llargada dels caràcters ascii
  int recepcions = 0;
  int MissatgeCompletat = 0;

  while (recepcions <7){
    //Seguim escoltant el missatge
    if (input >= background*umbralDetecio){
      //S'ha detectat un pols
      long tempsRebuda = millis()
      NextBitMillis = millis()+NextBitMillis;

      if(input < background*umbralDetecio){
        //Ja no es detecta un puls
        int NumBits (tempsRebuda) / (mills()-tempsRebuda)
        

      }

    }
    Serial.println()

  }

}
*/
const int LEDPin = 13;
const int LDRPin = A0;
const int background = 0;


void setup() {
  pinMode(LEDPin, OUTPUT);
  pinMode(LDRPin, INPUT);
  nextMillis = millis() + interval;

  int sum = 0;
  int i = 0;

  while (millis()>nextMillis){ //S'està 1 seg prenent valors

    sum  = sum + analogRead(LDRPin);
    i++;
    delay(10);
  }
  background = sum/i; //Agafem com a background la mitjana dels valors de llum que es prenen durant 
  
}

void loop() {
  int input = analogRead(LDRPin);
  if (input > background*umbralDetecio) {
    digitalWrite(LEDPin, HIGH);
  }
  else {
    digitalWrite(LEDPin, LOW);
  }
}