#include <Arduino.h>
#include <USBHost.h>
#include <USBHostSerial.h>
#include <string.h>

// XIAO ESP32-S3 + powered USB hub + Thymio II USB cable.
// This sketch reads Aseba variables over Thymio's USB CDC connection.
// LED: slow blink = no USB device; fast blink = no fresh "state" value;
//       1-6 short flashes, then a pause = the Thymio state number.

USBHostSerialClass thymioUsb;

constexpr uint8_t LED_PIN = 21;  // XIAO ESP32-S3 user LED, active LOW
constexpr uint16_t HOST_NODE = 1;
constexpr uint16_t PROTOCOL_VERSION = 5;
constexpr uint16_t ID_DESCRIPTION = 0x9000;
constexpr uint16_t ID_NAMED_VARIABLE_DESCRIPTION = 0x9001;
constexpr uint16_t ID_VARIABLES = 0x9005;
constexpr uint16_t ID_NODE_PRESENT = 0x900c;
constexpr uint16_t ID_GET_VARIABLES = 0xa00b;
constexpr uint16_t ID_GET_NODE_DESCRIPTION = 0xa010;
constexpr uint16_t ID_LIST_NODES = 0xa011;
constexpr size_t MAX_PAYLOAD = 256;

uint8_t frame[6 + MAX_PAYLOAD];
size_t frameLength = 0;
size_t expectedFrameLength = 0;

bool wasMounted = false;
bool foundNode = false;
bool descriptionComplete = false;
uint16_t thymioNode = 0;
uint16_t expectedVariables = 0;
uint16_t describedVariables = 0;
uint16_t nextVariableOffset = 0;
int32_t stateOffset = -1;
int32_t proximityOffset = -1;

// These two values are available for your own XIAO logic after each reply.
int16_t thymioState = 0;
int16_t frontProximity = 0;  // prox.horizontal[2]
uint32_t lastStateAt = 0;
uint32_t lastProximityAt = 0;
uint32_t lastDiscoveryAt = 0;
uint32_t lastDescriptionAt = 0;
uint32_t lastPollAt = 0;

uint16_t wordAt(const uint8_t *p) {
  return uint16_t(p[0]) | (uint16_t(p[1]) << 8);
}

void putWord(uint8_t *p, uint16_t value) {
  p[0] = uint8_t(value);
  p[1] = uint8_t(value >> 8);
}

void sendMessage(uint16_t id, const uint16_t *words, size_t wordCount) {
  if (!thymioUsb.mounted() || wordCount > 3) return;
  uint8_t packet[12];
  putWord(packet, uint16_t(wordCount * 2));  // payload byte length
  putWord(packet + 2, HOST_NODE);
  putWord(packet + 4, id);
  for (size_t i = 0; i < wordCount; ++i) {
    putWord(packet + 6 + i * 2, words[i]);
  }
  thymioUsb.write(packet, 6 + wordCount * 2);
}

void askForDescription() {
  const uint16_t request[] = {thymioNode, PROTOCOL_VERSION};
  sendMessage(ID_GET_NODE_DESCRIPTION, request, 2);
  lastDescriptionAt = millis();
}

void askForVariables(uint16_t offset, uint16_t count) {
  const uint16_t request[] = {thymioNode, offset, count};
  sendMessage(ID_GET_VARIABLES, request, 3);
}

void handleMessage(uint16_t source, uint16_t id,
                   const uint8_t *payload, size_t length) {
  if (id == ID_NODE_PRESENT && length >= 2) {
    if (!foundNode || source != thymioNode) {
      thymioNode = source;
      foundNode = true;
      descriptionComplete = false;
      stateOffset = -1;
      proximityOffset = -1;
      lastStateAt = 0;
      askForDescription();
    }
    return;
  }
  if (!foundNode || source != thymioNode) return;

  if (id == ID_DESCRIPTION && length >= 15) {
    const uint8_t nameLength = payload[0];
    if (size_t(nameLength) + 15 > length) return;
    const size_t fields = 1 + nameLength;
    expectedVariables = wordAt(payload + fields + 8);  // fifth field
    describedVariables = 0;
    nextVariableOffset = 0;
    stateOffset = -1;
    proximityOffset = -1;
    descriptionComplete = (expectedVariables == 0);
    return;
  }

  if (id == ID_NAMED_VARIABLE_DESCRIPTION && length >= 3 &&
      !descriptionComplete && describedVariables < expectedVariables) {
    const uint16_t size = wordAt(payload);
    const uint8_t nameLength = payload[2];
    if (size_t(nameLength) + 3 > length) return;
    const char *name = reinterpret_cast<const char *>(payload + 3);
    if (nameLength == 5 && memcmp(name, "state", 5) == 0 && size >= 1) {
      stateOffset = nextVariableOffset;
    }
    if (nameLength == 15 && memcmp(name, "prox.horizontal", 15) == 0 && size >= 3) {
      proximityOffset = nextVariableOffset;
    }
    nextVariableOffset += size;
    if (++describedVariables == expectedVariables) descriptionComplete = true;
    return;
  }

  if (id == ID_VARIABLES && length >= 4 && (length % 2) == 0) {
    const uint16_t offset = wordAt(payload);
    const uint16_t count = (length - 2) / 2;
    if (stateOffset >= 0 && offset <= stateOffset &&
        uint32_t(stateOffset) < uint32_t(offset) + count) {
      thymioState = int16_t(wordAt(payload + 2 + 2 * (stateOffset - offset)));
      lastStateAt = millis();
    }
    if (proximityOffset >= 0 && offset <= proximityOffset + 2 &&
        uint32_t(proximityOffset + 2) < uint32_t(offset) + count) {
      frontProximity = int16_t(wordAt(payload + 2 + 2 * (proximityOffset + 2 - offset)));
      lastProximityAt = millis();
    }
  }
}

void receiveByte(uint8_t value) {
  if (frameLength >= sizeof(frame)) {
    frameLength = 0;
    expectedFrameLength = 0;
  }
  frame[frameLength++] = value;
  if (frameLength == 2) {
    const uint16_t payloadLength = wordAt(frame);
    if (payloadLength > MAX_PAYLOAD) {
      frameLength = 0;
      expectedFrameLength = 0;
      return;
    }
    expectedFrameLength = 6 + payloadLength;
  }
  if (expectedFrameLength && frameLength == expectedFrameLength) {
    handleMessage(wordAt(frame + 2), wordAt(frame + 4),
                  frame + 6, expectedFrameLength - 6);
    frameLength = 0;
    expectedFrameLength = 0;
  }
}

void resetConnection() {
  frameLength = 0;
  expectedFrameLength = 0;
  foundNode = false;
  descriptionComplete = false;
  stateOffset = -1;
  proximityOffset = -1;
  lastStateAt = 0;
  lastProximityAt = 0;
  lastDiscoveryAt = 0;
  lastDescriptionAt = 0;
  lastPollAt = 0;
}

void updateLed() {
  const uint32_t now = millis();
  bool on;
  if (!thymioUsb.mounted()) {
    on = (now % 1000) < 120;  // slow blink: USB not mounted
  } else if (lastStateAt == 0 || now - lastStateAt > 1500 ||
             thymioState < 1 || thymioState > 6) {
    on = (now % 250) < 70;   // fast blink: no usable state yet
  } else {
    const uint32_t phase = now % 3000;
    on = phase < uint32_t(thymioState) * 300 && (phase % 300) < 100;
  }
  digitalWrite(LED_PIN, on ? LOW : HIGH);
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  USBHost.begin();
  thymioUsb.begin(115200);  // CDC line coding plus DTR when Thymio mounts
}

void loop() {
  USBHost.task();
  const bool mounted = thymioUsb.mounted();
  if (mounted != wasMounted) {
    resetConnection();
    wasMounted = mounted;
  }

  if (mounted) {
    uint8_t bytes[64];
    size_t count;
    while ((count = thymioUsb.read(bytes, sizeof(bytes))) > 0) {
      for (size_t i = 0; i < count; ++i) receiveByte(bytes[i]);
      USBHost.task();
    }

    const uint32_t now = millis();
    if (!foundNode && (lastDiscoveryAt == 0 || now - lastDiscoveryAt >= 1500)) {
      const uint16_t version = PROTOCOL_VERSION;
      sendMessage(ID_LIST_NODES, &version, 1);
      lastDiscoveryAt = now;
    } else if (foundNode && !descriptionComplete &&
               now - lastDescriptionAt >= 5000) {
      askForDescription();
    }
    if (descriptionComplete && now - lastPollAt >= 250) {
      if (stateOffset >= 0) askForVariables(stateOffset, 1);
      if (proximityOffset >= 0) askForVariables(proximityOffset, 3);
      lastPollAt = now;
    }
  }
  updateLed();
  delay(1);
}
