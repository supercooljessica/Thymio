#include <WiFi.h>
#include <WebServer.h>

const char *ssid = "Thymio-XIAO";
const char *password = "thymio123";  // At least 8 characters for WPA2.
WebServer server(80);

int proximity[7] = {0, 0, 0, 0, 0, 0, 0};
bool hasSample = false;
unsigned long lastSampleMs = 0;

const char page[] PROGMEM = R"HTML(
<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Thymio proximity</title>
<style>body{font:18px system-ui;max-width:36rem;margin:2rem auto;padding:0 1rem}
pre{font-size:1.2rem;line-height:1.8;background:#f3f5f7;padding:1rem;border-radius:.5rem}</style>
<h1>Thymio proximity</h1><p id="status">Waiting for data...</p><pre id="values"></pre>
<script>
const labels=['front left','front mid-left','front center','front mid-right',
              'front right','rear left','rear right'];
async function refresh(){
  try{
    const r=await fetch('/data',{cache:'no-store'});
    const d=await r.json();
    document.getElementById('status').textContent=d.received
      ? `Last update ${d.age_ms} ms ago` : 'Waiting for data...';
    document.getElementById('values').textContent=d.received
      ? d.values.map((v,i)=>`${labels[i].padEnd(16)} ${v}`).join('\n') : '';
  }catch(e){document.getElementById('status').textContent='Connection lost';}
}
refresh();setInterval(refresh,250);
</script></html>
)HTML";

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(IPAddress(192, 168, 4, 1), IPAddress(192, 168, 4, 1),
                    IPAddress(255, 255, 255, 0));
  if (!WiFi.softAP(ssid, password)) {
    Serial.println("Could not start Wi-Fi access point");
    while (true) delay(1000);
  }

  server.on("/", HTTP_GET, []() { server.send_P(200, "text/html", page); });
  server.on("/data", HTTP_GET, []() {
    String json = "{\"received\":";
    json += hasSample ? "true" : "false";
    json += ",\"age_ms\":";
    json += hasSample ? String(millis() - lastSampleMs) : "null";
    json += ",\"values\":[";
    for (int i = 0; i < 7; ++i) {
      if (i) json += ',';
      json += proximity[i];
    }
    json += "]}";
    server.sendHeader("Cache-Control", "no-store");
    server.send(200, "application/json", json);
  });
  server.on("/update", HTTP_POST, []() {
    String body = server.arg("plain");
    int values[7];
    if (body.length() > 80 ||
        sscanf(body.c_str(), "%d,%d,%d,%d,%d,%d,%d", &values[0], &values[1],
               &values[2], &values[3], &values[4], &values[5], &values[6]) != 7) {
      server.send(400, "text/plain", "Expected seven comma-separated readings");
      return;
    }
    for (int i = 0; i < 7; ++i) proximity[i] = values[i];
    lastSampleMs = millis();
    hasSample = true;
    server.send(204);
  });
  server.begin();
  Serial.print("Open http://");
  Serial.println(WiFi.softAPIP());
}

void loop() {
  server.handleClient();
}
