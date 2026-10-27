// Receive "state,front_sensor,red,green,blue" from local_usb_dashboard.py.
// The older two-number serial bridge remains supported.
int thymioState = -1;
int frontSensor = 0;
int topRed = 0;
int topGreen = 0;
int topBlue = 0;
unsigned long lastMessageMs = 0;

char line[48];
size_t lineLength = 0;

void acceptLine() {
  line[lineLength] = '\0';
  int state, front, red, green, blue;
  int fields = sscanf(line, "%d,%d,%d,%d,%d", &state, &front, &red, &green, &blue);
  if ((fields == 2 || fields == 5) &&
      state >= -1 && state <= 6 && front >= 0 && front <= 10000 &&
      (fields == 2 || (red >= 0 && red <= 32 && green >= 0 && green <= 32 &&
                       blue >= 0 && blue <= 32))) {
    thymioState = state;
    frontSensor = front;
    if (fields == 5) {
      topRed = red;
      topGreen = green;
      topBlue = blue;
    }
    lastMessageMs = millis();
    Serial.print("ACK,");
    Serial.print(thymioState);
    Serial.print(',');
    Serial.print(frontSensor);
    if (fields == 5) {
      Serial.print(','); Serial.print(topRed);
      Serial.print(','); Serial.print(topGreen);
      Serial.print(','); Serial.print(topBlue);
    }
    Serial.println();
  } else {
    Serial.println("ERR");
  }
  lineLength = 0;
}

void setup() {
  Serial.begin(115200);
}

void loop() {
  while (Serial.available()) {
    char ch = (char)Serial.read();
    if (ch == '\n') {
      acceptLine();
    } else if (ch != '\r') {
      if (lineLength < sizeof(line) - 1) {
        line[lineLength++] = ch;
      } else {
        lineLength = 0;
        Serial.println("ERR,too-long");
      }
    }
  }

  // Use thymioState, frontSensor, and topRed/topGreen/topBlue here.
  // A message older than one second is stale.
  bool connected = lastMessageMs != 0 && millis() - lastMessageMs < 1000;
  (void)connected;
}
