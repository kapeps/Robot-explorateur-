int inputPin = 6;

int buttonState;
int val;

void setup() {
   pinMode(inputPin, INPUT);
   digitalWrite(inputPin, HIGH);
   
   Serial.begin(9600);
   buttonState = digitalRead(inputPin); // store initial button state (should be high)
}

void loop() {
   val = digitalRead(inputPin);
       
   if (val != buttonState) {
       if (val == LOW) {
           Serial.println("Button - low");
       } else {
           Serial.println("Button - high");
       }
   }
   
   buttonState = val;
}
