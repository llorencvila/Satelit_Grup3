const int LedIdle = 12;
const int LedMirall = 11;
const int LedMissatge = 10;

const int LDRPin = A0;
const float umbralDetecio = 1.25;  //Es considerarà com a detecció quan els valors sobrepassin aquest tan percert del valor base

int NumRep = 0;
int TempsRebudaMissHigh = 0;
int TempsRebudaMissLow = 0;

int BaudRate = 1000;
int EstatMissatge = 0;  //0=Idle | 1=Startbit | 2=LlegintMissatge

int UmbralIdle = 1500;
int UmbralLDR = -1;
int LastIsidle = 0;
int IsIdleNow = 0;

long TIniciCrono;
long TempsRebuda;
long TempsRebudaStartbit=0;
long nextMillis = 0;
long TDetecioIdle;

int missatge[8];
int LlargadaMissatge = 0;

int lastInput;
int input;



void calibracio() {
  Serial.println("Entrem a calibració");
  int primer = 1;
  int intents = 0;

  while ((UmbralLDR < 0 || UmbralLDR > 1000) && intents < 3) {  //Si el umbral és superior al valor màxim que pot agafar el sensor
    int sum = 0;
    int i = 0;
    intents++;
    Serial.println(intents);
    Serial.println("Prenent mitjana");
    nextMillis = millis() + 1000;

    while (millis() < nextMillis) {  //S'està 1 seg prenent valors
      sum = sum + analogRead(LDRPin);
      Serial.println(analogRead(LDRPin));
      i++;
      delay(75);
    }

    int background = sum / i;  //Agafem com a background la mitjana dels valors de llum que es prenen durant

    if (intents < 3) {
      UmbralLDR = background * umbralDetecio;
      
      primer = 0;
    } else {
      UmbralLDR = 800;
    }
    Serial.println("Umbral: " + String(UmbralLDR));
  }
}



int CanviEstat(int Vi, int Vf) {  //Valor inicial i valor final
  //El Vf mai es farà servir, tot i aixo el deixo perque crec que dona claredat a l'hoara de cridar la funció

  if (Vi == 0) {
    if (lastInput <= UmbralLDR && input >= UmbralLDR) {  //0->1
      TempsRebuda = millis();
      digitalWrite(LedMirall, HIGH);
      //Serial.print("1");
      return 1;
    }else{
      return 0;
    }
  }
  if (Vi == 1) {
    if (lastInput >= UmbralLDR && input <= UmbralLDR) {  //1->0
      TempsRebuda = millis();
      digitalWrite(LedMirall, LOW);
      //Serial.print("0");
      return 1;
    }else{
      return 0;
    }
  }
}

int IsIdle(){
  if (CanviEstat(0,1)){
    TDetecioIdle = millis()+UmbralIdle;
  }
  if (millis() >= TDetecioIdle){
    digitalWrite(LedIdle, HIGH);
    return 1;

  } else{
    digitalWrite(LedIdle, LOW);
    return 0;

  }
}

int LlegirStartBit() {
  int trobat = 0;
  long TimeoutFuncio = millis()+5000;

  while (!trobat){
    if (millis() > TimeoutFuncio){
      trobat = 1;
    }
    if (CanviEstat(1, 0)) {
      TempsRebudaStartbit = millis();
      //Serial.println("Rebem Inici StartBit");
    }
    if (CanviEstat(0, 1)) {
      int deltaT = millis() - TempsRebudaStartbit;
      //Serial.println("T0 = " + String(TempsRebudaStartbit) + " t0 = " +String(millis()) + " DeltaT = " +String(deltaT));
      Serial.println(deltaT);
      if (deltaT <= BaudRate) {
        BaudRate = deltaT;
        TIniciCrono = millis();
        EstatMissatge = 2;  //Tot Apunt per poder llegir el missatge
        trobat = 1;

        return 1;
      } else{
        return 0;

      }
    }
  }
}

void AfegirAlMissatge(int ValorAAfegir) {
  missatge[LlargadaMissatge + 1] = ValorAAfegir;

  // -----ZONA DEBUG ---
  /*
  Serial.print("Missatge: ");
  for (int i = 0; i<LlargadaMissatge; i++){
    Serial.print(missatge[i]);
  }
  Serial.print("\n");
  */
  // -------------------

  LlargadaMissatge++;
  if (LlargadaMissatge > 8) {
    EstatMissatge = 0;  //Ja s'han detectat tots els valors que nescesitem
  }
}

void LlegirMissatge() {    //Aquesta funció es podria compactar més segurament
  int BitComplet = 0;
  long TimeoutFuncio = millis()+5000;

  while (!BitComplet == 0 && (millis()<TimeoutFuncio)){

    digitalWrite(LedMissatge,HIGH);
    //Serial.println("dTLow");
    if (CanviEstat(1, 0)) {  //Detectem 0's
      NumRep = 0;
      TempsRebudaMissLow = millis();
      Serial.println("Afegim un = 0");
      //AfegirAlMissatge(0);
    }

    int deltaTLow = millis() - TempsRebudaMissLow;
    if (deltaTLow >= BaudRate * (NumRep)) {
      NumRep++;
      AfegirAlMissatge(0);

      //Serial.println("Cero Extra");
    }
    

    if (CanviEstat(0, 1)) {  //Detectem 1's
      NumRep = 0;
      TempsRebudaMissHigh = millis();
      Serial.println("Afegim un = 1");
      AfegirAlMissatge(1);
    }
    int deltaTHigh = millis() - TempsRebudaMissHigh;
    if (deltaTHigh >= (BaudRate * (NumRep + 1))) {
      NumRep++;
      AfegirAlMissatge(1);
    }
  }
}

void LlegirMissatge2(){
  if (millis() >= (TIniciCrono-(BaudRate/2)+BaudRate)){
    TIniciCrono = millis();

    if (input > UmbralLDR){
      Serial.println("1");
    }else{
      Serial.println("0");
    }
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println("Començem");
  pinMode(LedMirall, OUTPUT);    //Aquest led simplement replica el que fa el laser
  pinMode(LedMissatge, OUTPUT);  //S'encen quan començem a rebre un missatge
  pinMode(LDRPin, INPUT);

  nextMillis = millis() + 1000;
  calibracio();
}

void loop() {
  lastInput = input;
  input = analogRead(LDRPin);
  //Serial.println(String(UmbralLDR) + "  " + String(input) + "  " + String(lastInput));
  //Serial.println(CanviEstat(0, 1));
  //CanviEstat(1, 0);

  //LlegirStartBit();
  //Serial.println(BaudRate);
  Serial.println(EstatMissatge);
  if (EstatMissatge != 0 || EstatMissatge !=1){
    digitalWrite(LedIdle,LOW);
  }
  if (EstatMissatge == 0 ){
    if (IsIdle()){
      Serial.println("idle");
      if (LlegirStartBit())


      EstatMissatge = 1;
      digitalWrite(LedIdle,HIGH);
    } else{
      digitalWrite(LedIdle,LOW);
    }
  } if (EstatMissatge == 1){
    digitalWrite(LedIdle,LOW);
    LlegirStartBit();
    //Serial.println(BaudRate);

  } if (EstatMissatge == 2) {
    Serial.print("llegint missatge");
    LlegirMissatge();
  }

  /*
  }
  if (EstatMissatge == 1){ //Toca Llegir el statBit
    LlegirStartBit();
  }
  if (EstatMissatge == 2){
    Serial.println("Llegint Missatge");
    LlegirMissatge();
  }
*/
}
