int laser = 11;
int BitRate = 500;
int missatge[8] = {1,0,1,0,1,0,1,0};
int StartBit[2] = {0,1};
long NextTransmisio;
int i=0;

void SendStartBit(){
  Serial.print("Start Bits: ");

  i = 0;
  while(i<=1){
    if (millis()>NextTransmisio){
      if (StartBit[i] == 0){
        digitalWrite(laser,LOW);

      }
      else if (StartBit[i] == 1){
        digitalWrite(laser,HIGH);

      } 
      NextTransmisio = millis()+BitRate;
      Serial.print(String(StartBit[i]));
      i++;

    }
  }
  Serial.print("\n");
  return;
}

void SendMiss(){
  Serial.print("Missatge: ");
  i = 0;
  while(i<=7){
    if (millis()>NextTransmisio){
      if (missatge[i] == 0){
        digitalWrite(laser,LOW);

      }
      else if (missatge[i] == 1){
        digitalWrite(laser,HIGH);

      } 
      NextTransmisio = millis()+BitRate;
      Serial.print(missatge[i]);
      i++;
    }
  }
}

void setup(){
  Serial.begin(9600);
  pinMode(laser, OUTPUT);
  digitalWrite(laser, HIGH); //La comunicació UART té el idle state com a alt
  NextTransmisio = millis() + BitRate;

}

void loop(){

  //SendStartBit();
  SendMiss();
  //idle State
  digitalWrite(laser, HIGH);
  Serial.print("\n");
  Serial.println("-IDLE-");
  delay(5000);

}