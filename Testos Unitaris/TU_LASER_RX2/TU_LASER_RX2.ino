const int LEDPin = 6;
const int LDRPin = A0;
float background = 0;
float umbralDetecio = 1.25; //Es considerarà com a detecció quan els valors sobrepassin aquest tan percert del valor base
long nextMillis = 0;
int OgBitRate = 500;
int BitRate = OgBitRate; //Temps que triga a enviar cada bit 
int input = 0;
float umbral = -1;
int num0s;
int num1s;
int lastInput;
long tempsRebudaHigh = 0;
long tempsRebudaLow = 0;
bool primer;
int recepcions;
int NextTimeoutMissatge;
int llargadaMissatgeBits = 7;
int duradaPols;
long missatge[8];
int EsperaMax = 2000;//BitRate*llargadaMissatgeBits;


void calibracio(){
  int primer =1;
  int intents =0;

  while((umbral < 0 || umbral > 1000) && intents <3 ){ //Si el umbral és superior al valor màxim que pot agafar el sensor
    int sum = 0;
    int i = 0;
    intents++;
    Serial.println(intents);
    Serial.println("Prenent mitjana");
    nextMillis = millis() + 1000;
    while (millis()<nextMillis){ //S'està 1 seg prenent valors

      sum  = sum + analogRead(LDRPin);
      Serial.println(analogRead(LDRPin));
      i++;
      delay(75);
    }

    background = sum/i; //Agafem com a background la mitjana dels valors de llum que es prenen durant 

    if (intents <3){
      umbral = background*umbralDetecio;
      primer = 0;
    }else{
      umbral = 800;
    }
    Serial.println("Umbral: "+ String(umbral));
  }
  }
//
int isIdle(){
  int trobat = 0;
  while(trobat != 1){
    lastInput = input;
    input = analogRead(LDRPin);

    if (lastInput<umbral && input>umbral){ //0->1
      tempsRebudaHigh = millis();
      digitalWrite(LEDPin,HIGH);
    }
    if (lastInput<umbral && input>umbral){ //0->1
      digitalWrite(LEDPin,LOW);
      

    int deltat = millis() -tempsRebudaHigh;
    
    if (deltat>4500){
      Serial.println("IDLE DETECTAT");
      deltat = 0;
      trobat = 1;
    }
  }
  return 1;
}


int startbit(){ //Coprovar que bitRate <
  int llargadaPols;
  int trobat = 0;
  while(trobat != 1){
    //Serial.println(fi);
    lastInput = input;
    input = analogRead(LDRPin);

    if (lastInput>umbral && input<umbral){ //bit de recepció (1->0)
      digitalWrite(LEDPin,LOW);
      NextTimeoutMissatge = millis() + EsperaMax;
      tempsRebudaLow = millis();

    }
    if (lastInput<umbral && input>umbral){ //0->1
      digitalWrite(LEDPin,LOW);
      
      int BitRateCalc = millis()-tempsRebudaLow-5; //El -5 final és per donar més marge d'error//En aquest pas el bitrate passa a ser el bitrate mesurat per aquest cas que serà un valor menor a l'inicial per culpa del temps de resposta del sensor
      
      if (BitRateCalc < OgBitRate){
        BitRate = BitRateCalc;
        Serial.println(BitRate);
        trobat = 1;
        break;
        Serial.println("trobat = " + String(trobat));

      }else{
        Serial.println("Incorrecte: "+ String(BitRateCalc));
        return 0;
        break;
      }


    }
    return 0; //No s'ha trobat un startbit       
  }
  return 1; //S'ha identificat un StartBit
  Serial.println("Sortim de la recepció");
  }

//
void recepcio(){
  while (recepcions <7 && (millis()<EsperaMax)){
    lastInput = input;
    input = analogRead(LDRPin);
    
    //Detectem un traspàs del umbral de 0 -> 1
    if (lastInput<umbral && input>umbral){ //bit = 1
      tempsRebudaHigh = millis();
      NextTimeoutMissatge = millis() + EsperaMax;
      digitalWrite(LEDPin,HIGH);

      if (!primer)
        num0s = (millis()-tempsRebudaLow) / BitRate;
        Serial.println("Num0s : " +String(num0s));

    }

      //Detectem un traspàs del umbral de 1 -> 0
    if (lastInput>umbral && input<umbral){ //bit = 0
      tempsRebudaLow = millis();
      digitalWrite(LEDPin,LOW);
      if (!primer)
        num1s = (millis()-tempsRebudaHigh) / BitRate;
        Serial.println("Num1s : " +String(num1s));



        for (int i = 0; i<num1s; i++){
          missatge[recepcions+i] = 1;
          recepcions = recepcions +1;
    }
      primer = false;
      Serial.println(recepcions);
    }
  }
  if (millis()> NextTimeoutMissatge){
    Serial.println("TIMEOUT ERROR");
  }
  }

//
void setup() {
  Serial.begin(9600);
  pinMode(LEDPin, OUTPUT);
  pinMode(LDRPin, INPUT);
  nextMillis = millis() + 1000;
  Serial.println("funcionant: ");

  calibracio();

}

void loop() {
  recepcions = 0;
  primer = true;
  lastInput = input;
  input = analogRead(LDRPin);
  //Serial.println(startbit());
  int EstaIdle = isIdle();
  Serial.println(isIdle());

  if (lastInput<umbral && input>umbral){ //0->1
    tempsRebudaHigh = millis();
    digitalWrite(LEDPin,HIGH);
  }
  if (input>umbral){
    int deltat = millis() -tempsRebudaHigh;   

    if (deltat>4500){
      Serial.println("IDLE DETECTAT");
      startbit();
      recepcio();
      deltat = 0;
  z
  }

    Serial.println("Missatge: ");
    for (int i=0; i <7 ; i++){
      Serial.print(missatge[i]);
      }

    Serial.println();
  }

  }
