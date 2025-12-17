const int LedMirall = 11;
const int LedMissatge =10;
const int LDRPin = A0;
const float umbralDetecio = 1.25; //Es considerarà com a detecció quan els valors sobrepassin aquest tan percert del valor base


int BaudRate = 500;
int EstatMissatge = 0; //0=Idle | 1=Startbit | 2=LlegintMissatge

int UmbralIdle =2500;
int UmbralLDR = -1;
int LastIsidle = 0;
int IsIdleNow = 0;

int TempsRebuda;
int TempsRebudaStartbit;
int nextMillis = 0;

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



int CanviEstat(int Vi, int Vf, int TempsRebuda){ //Valor inicial i valor final
  //El Vf mai es farà servir, tot i aixo el deixo perque crec que dona claredat a l'hoara de cridar la funció
  
  if (Vi == 0){
    if (lastInput<UmbralLDR && input>UmbralLDR){ //0->1
      digitalWrite(LedMirall,HIGH);
      if (TempsRebuda){
        TempsRebuda = millis();
      }
      return 1;
    }
  }else if(Vi == 1) {
    if (lastInput>UmbralLDR && input<UmbralLDR){ //1->0
      digitalWrite(LedMirall,LOW);
      if (TempsRebuda){
        TempsRebuda = millis();
      }
      return 1;
    }
  }
}

int IsIdle(){
  CanviEstat(0,1,1);
  if ((millis()-TempsRebuda)>UmbralIdle){
    digitalWrite(LedMissatge,LOW);
    return 1;
  }
}

int IsStartBit(){
  LastIsidle = IsIdleNow;
  IsIdleNow = IsIdle();

  if (LastIsidle == 1 && CanviEstat(1,0) == 1){ //1->0  //Si abans estava en idle i ara hi hi ha un canvi a low
    TempsRebudaStartbit = millis();
    digitalWrite(LedMissatge,HIGH);
    EstatMissatge = 1;
    return 1;
  } else{
    return 0;
  }
}

void LlegirStartBit(){
      if (CanviEstat(0,1)){
        int deltaT = millis() - TempsRebudaStartbit;
        if (deltaT <= BaudRate){
          BaudRate = deltaT;
          EstatMissatge = 2;

        }else{ //En cas contrari vol dir que la hem feta grossa
          EstatMissatge = 0; //Encara no se ben be que fer amb aquesta variable
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
    EstatMissatge = 1; //Ja s'han detectat tots els valors que nescesitem
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
  Serial.println(IsStartBit());
  lastInput = input;
  input = analogRead(LDRPin);

  if (IsStartBit() == 1){
    //Començem la lectura
    LlegirStartBit();
  }
  if (EstatMissatge == 3){
    //És hora de llegir
    LlegirMissatge();
  }


}
