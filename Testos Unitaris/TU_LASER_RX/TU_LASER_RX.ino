const int LEDPin = 13;
const int LDRPin = A0;
float background = 0;
float umbralDetecio = 1.25; //Es considerarà com a detecció quan els valors sobrepassin aquest tan percert del valor base
long nextMillis = 0;
float BitRate = 300; //Temps que triga a enviar cada bit 
int input = 0;
float umbral;
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


void calibracio(){
  int sum = 0;
  int i = 0;
  int primer =1;
  while(umbral > 1024 || primer==1){ //Si el umbral és superior al valor màxim que pot agafar el sensor
    Serial.println("Prenent mitjana");
    nextMillis = millis() + 1000;
    while (millis()<nextMillis){ //S'està 1 seg prenent valors

      sum  = sum + analogRead(LDRPin);
      Serial.println(analogRead(LDRPin));
      i++;
      delay(75);
    }

    background = sum/i; //Agafem com a background la mitjana dels valors de llum que es prenen durant 
    umbral = background*umbralDetecio;
    Serial.println("Umbral: "+ String(umbral));
    primer = 0;
  }
 
}


void setup() {
  Serial.begin(9600);
  pinMode(LEDPin, OUTPUT);
  pinMode(LDRPin, INPUT);
  nextMillis = millis() + 1000;

  calibracio();

}

int startbit(){
  int llargadaPols;
  int trobat = 0;
  while(trobat != 1){
    //Serial.println(fi);
    lastInput = input;
    input = analogRead(LDRPin);

    if (lastInput>umbral && input<umbral){ //bit de recepció (1->0)
      Serial.println("Bit de recepció");
      NextTimeoutMissatge = millis() + BitRate*llargadaMissatgeBits;
      tempsRebudaLow = millis();
    }
    if (lastInput<umbral && input>umbral){ //0->1
      Serial.print("Bit down: ");
       BitRate = millis()-tempsRebudaLow-5; //El -5 final és per donar més marge d'error//En aquest pas el bitrate passa a ser el bitrate mesurat per aquest cas que serà un valor menor a l'inicial per culpa del temps de resposta del sensor
       Serial.println(BitRate);
       trobat = 1;
       break;
       Serial.println("trobat = " + String(trobat));
    }
    return 0; //No s'ha trobat un startbit       
  }
  return 1; //S'ha identificat un StartBit
  Serial.println("Sortim de la recepció");
  }


void recepcio(){
  while (recepcions <7 && (millis()<NextTimeoutMissatge)){
    lastInput = input;
    input = analogRead(LDRPin);
    
    //Detectem un traspàs del umbral de 0 -> 1
    if (lastInput<umbral && input>umbral){ //bit = 1
      tempsRebudaHigh = millis();
      if (!primer)
        num0s = (millis()-tempsRebudaLow) / BitRate;
        Serial.println("Num0s : " +String(num0s));

    }

      //Detectem un traspàs del umbral de 1 -> 0
    if (lastInput>umbral && input<umbral){ //bit = 0

      tempsRebudaLow = millis();
      if (!primer)
        num1s = (millis()-tempsRebudaHigh) / BitRate;
        Serial.print(missatge[1]);


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

void loop() {
  recepcions = 0;
  primer = true;
  lastInput = input;
  input = analogRead(LDRPin);
  Serial.println(String(umbral) + "  " + String(input));

  }
