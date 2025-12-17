const int LedMirall = 11;
const int LedMissatge =10;
const int LDRPin = A0;
const float umbralDetecio = 1.25; //Es considerarà com a detecció quan els valors sobrepassin aquest tan percert del valor base


int BaudRate = 500;
int EstatMissatge = 0; //0=Idle | 1=Startbit | 2=LlegintMissatge

int UmbralIdle =2000;
int UmbralLDR = -1;
int LastIsidle = 0;
int IsIdleNow = 0;

int TempsRebuda;
int TempsRebudaStartbit;
int nextMillis = 0;
int TDetecioIdle;

int missatge[8]; 
int LlargadaMissatge = 0;

int lastInput;
int input;



void calibracio(){
  Serial.println("Entrem a calibració");
  int primer =1;
  int intents =0;

  while((UmbralLDR < 0 || UmbralLDR > 1000) && intents <3 ){ //Si el umbral és superior al valor màxim que pot agafar el sensor
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

    int background = sum/i; //Agafem com a background la mitjana dels valors de llum que es prenen durant 

    if (intents <3){
      UmbralLDR = background*umbralDetecio;
      primer = 0;
    }else{
      UmbralLDR = 800;
    }
    Serial.println("Umbral: "+ String(UmbralLDR));
  }
  }



int CanviEstat(int Vi, int Vf){ //Valor inicial i valor final
  //El Vf mai es farà servir, tot i aixo el deixo perque crec que dona claredat a l'hoara de cridar la funció
  
  if (Vi == 0){
    if (lastInput<UmbralLDR && input>UmbralLDR){ //0->1
      TempsRebuda = millis();
      digitalWrite(LedMirall,HIGH);

  
      return 1;
    }
  }else if(Vi == 1) {
    if (lastInput>UmbralLDR && input<UmbralLDR){ //1->0
       TempsRebuda = millis();
      digitalWrite(LedMirall,LOW);
      return 1;
    }
  }
}

void LlegirStartBit(){
  if (CanviEstat(1,0)){
    TempsRebudaStartbit = millis();
    Serial.println("Rebem Inici StartBit");
  }
  if (CanviEstat(0,1)){
    int deltaT = millis() - TempsRebudaStartbit;
    if (deltaT <= BaudRate) {
      BaudRate = deltaT;
      EstatMissatge = 2; //Tot Apunt per poder llegir el missatge
      Serial.println("Rebem Final StartBit");
    } else{ //Això vol dir que la hem feta grossa
      EstatMissatge = 0
    }
  }
}

void AfegirAlMissatge(int ValorAAfegir){
  missatge[LlargadaMissatge+1] = ValorAAfegir;
  
  // -----ZONA DEBUG ---
  Serial.print("Missatge: ");
  for (int i = 0; i<LlargadaMissatge; i++){
    Serial.print(missatge[i]);
  }
  Serial.print("\n");
  // -------------------

  LlargadaMissatge++;
  if (LlargadaMissatge > 8){
    EstatMissatge = 0; //Ja s'han detectat tots els valors que nescesitem
  }

}

void LlegirMissatge(){ //Aquesta funció es podria compactar més segurament
  if(CanviEstat(1,0)){  //Detectem 0's
    int NumRep = 0;
    int deltaT = millis() - TempsRebuda;

    if (deltaT >= BaudRate*(NumRep+1)){
      NumRep++;
      AfegirAlMissatge(0);
    }
  }

  if(CanviEstat(0,1)){  //Detectem 1's
    int NumRep = 0;
    int deltaT = millis() - TempsRebuda;

    if (deltaT >= BaudRate*(NumRep+1)){
      NumRep++;
      AfegirAlMissatge(1);
    }
  }
}



void setup() {
  Serial.begin(9600);
  Serial.println("Començem");
  pinMode(LedMirall, OUTPUT); //Aquest led simplement replica el que fa el laser
  pinMode(LedMissatge, OUTPUT); //S'encen quan començem a rebre un missatge
  pinMode(LDRPin, INPUT);

  nextMillis = millis() + 1000;
  calibracio();

}

void loop() {
  lastInput = input;
  input = analogRead(LDRPin);

  if (EstatMissatge == 0){
    if (CanviEstat(0,1)){
      TDetecioIdle = millis()+UmbralIdle;
    }
    if (millis() >= TDetecioIdle){
      EstatMissatge = 1;
      Serial.println("----IDLE----");
    }
  }
  if (EstatMissatge == 1){ //Toca Llegir el statBit
    LlegirStartBit();
  }
  if (EstatMissatge == 2){
    Serial.println("Llegint Missatge");
    LlegirMissatge();
  }

}
