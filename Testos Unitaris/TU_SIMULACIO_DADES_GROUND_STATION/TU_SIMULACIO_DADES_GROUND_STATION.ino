int h,t, pos, dist;

void setup() {
  Serial.begin(9600);
  //Serial.println("Random Ground Station");

  
}

void loop() {
    h = random(0, 100);
    t = random(10,30);
    pos = random(0,360);
    dist = random(0,400),
    Serial.print(h);
    Serial.print(":");
    Serial.print(t);
    Serial.print(":");
    Serial.print(pos);
    Serial.print(":");
    Serial.println(dist);
    delay(500);
    //TELEMETRIA
}
