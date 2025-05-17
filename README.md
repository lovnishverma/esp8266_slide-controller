# 1. ESP8266 Arduino Sketch (`esp8266_code.ino`)

This sketch:

* Connects ESP8266 to your WiFi.
* Hosts a web server with a simple slide control UI.
* Sends UDP commands to your PC (default port 4211).
* Controls onboard LED with different effects.
* Supports mDNS for `slidecontroller.local`.
* Handles LED blink, lightshow, static on/off, and pulse effects on commands.

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiUdp.h>
#include <ESP8266mDNS.h>

// WiFi Settings
const char* ssid = "YOUR_WIFI_NAME(SSID)";
const char* password = "yOUR_WIFI_PASSWORD";

// mDNS hostname
const char* hostName = "slidecontroller";

// UDP setup
WiFiUDP udp;
unsigned int localUdpPort = 4210;
unsigned int remoteUdpPort = 4211;

ESP8266WebServer server(80);

// LED control
const int LED_PIN = LED_BUILTIN;
const int PWM_RANGE = 1023;

// Blink variables
unsigned long previousMillis = 0;
const unsigned long blinkInterval = 500;
bool ledBlinkState = false;

// Command effect flags
bool commandEffect = false;
unsigned long commandEffectStartTime = 0;
byte commandEffectType = 0; // 0=next, 1=prev, 2=start, 3=exit, 4=current
const unsigned long COMMAND_EFFECT_DURATION = 1500;

// Lightshow / Blink / LED state
bool lightshowEnabled = true;
bool blinkEnabled = false;
bool ledOn = false;

// HTML page served by the ESP8266 with %IP_ADDRESS% placeholder
const char* html_content = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Slide Controller</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: sans-serif; text-align: center; padding: 20px; background: #f5f5f5; }
    h1 { color: #333; }
    button {
      font-size: 18px;
      padding: 15px 30px;
      margin: 10px;
      border: none;
      border-radius: 5px;
      color: #fff;
      background-color: #4CAF50;
      transition: background-color 0.3s;
      cursor: pointer;
    }
    button:hover { background-color: #45a049; }
    #prev { background-color: #f44336; }
    #start { background-color: #2196F3; }
    #exit { background-color: #ff9800; }
    #current { background-color: #9c27b0; }
    #toggleBlink { background-color: #607d8b; }
    #toggleBlink.active { background-color: #00796b; }
    #lightshow { background-color: #e91e63; }
    #toggleLed { background-color: #795548; }
    #toggleLed.active { background-color: #5d4037; }
    .status { margin-top: 15px; padding: 10px; background: #e0e0e0; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>PowerPoint Controller</h1>
  <p><strong>Current IP:</strong> <span id="ip">%IP_ADDRESS%</span></p>

  <div>
    <button onclick="send('next')">Next Slide</button>
    <button id="prev" onclick="send('prev')">Previous Slide</button><br>
    <button id="start" onclick="send('start')">Start</button>
    <button id="exit" onclick="send('exit')">Exit</button>
    <button id="current" onclick="send('current')">Current Slide</button><br>
    <button id="toggleBlink">Toggle Blink</button>
    <button id="lightshow" onclick="send('lightshow')">Toggle Lightshow</button>
    <button id="toggleLed">Toggle LED</button>
  </div>
  <div class="status" id="status">Blink: Disabled | LED: Off</div>

  <script>
    let blinkEnabled = false;
    let ledOn = false;

    function send(cmd) {
      fetch('/command?cmd=' + cmd)
        .then(res => res.text())
        .then(text => {
          console.log('Sent:', text);
          if (cmd === 'toggleBlink') {
            blinkEnabled = !blinkEnabled;
            document.getElementById("status").innerText = "Blink: " + (blinkEnabled ? "Enabled" : "Disabled") + " | LED: " + (ledOn ? "On" : "Off");
            const toggleBlink = document.getElementById("toggleBlink");
            toggleBlink.classList.toggle("active", blinkEnabled);
          } else if (cmd === 'lightshow') {
            console.log(text);
            document.getElementById("status").innerText = "Blink: " + (blinkEnabled ? "Enabled" : "Disabled") + " | LED: " + (ledOn ? "On" : "Off");
          } else if (cmd === 'toggleLed') {
            ledOn = !ledOn;
            document.getElementById("status").innerText = "Blink: " + (blinkEnabled ? "Enabled" : "Disabled") + " | LED: " + (ledOn ? "On" : "Off");
            const toggleLed = document.getElementById("toggleLed");
            toggleLed.classList.toggle("active", ledOn);
          }
        })
        .catch(err => console.error('Error:', err));
    }

    document.getElementById("toggleBlink").addEventListener("click", () => {
      send("toggleBlink");
    });
    document.getElementById("toggleLed").addEventListener("click", () => {
      send("toggleLed");
    });
  </script>
</body>
</html>
)rawliteral";

void handleRoot() {
  String html = html_content;
  html.replace("%IP_ADDRESS%", WiFi.localIP().toString());
  server.send(200, "text/html", html);
}

void handleCommand() {
  String command = server.arg("cmd");
  if (command.length() > 0) {
    if (command == "lightshow") {
      if (!blinkEnabled && !ledOn) {
        lightshowEnabled = !lightshowEnabled;
        server.send(200, "text/plain", lightshowEnabled ? "Lightshow enabled" : "Lightshow disabled");
      } else {
        server.send(200, "text/plain", "Blink or LED is enabled, lightshow disabled");
      }
    }
    else if (command == "toggleBlink") {
      blinkEnabled = !blinkEnabled;
      if (blinkEnabled) {
        lightshowEnabled = false; // Disable lightshow when blink starts
        ledOn = false;           // Disable LED when blink starts
        setLedBrightness(255);   // Start blinking immediately
      } else {
        setLedBrightness(0);     // Turn LED off when blink stops
      }
      server.send(200, "text/plain", blinkEnabled ? "Blink enabled" : "Blink disabled");
    }
    else if (command == "toggleLed") {
      ledOn = !ledOn;
      if (ledOn) {
        blinkEnabled = false;    // Disable blink when LED is on
        lightshowEnabled = false; // Disable lightshow when LED is on
        setLedBrightness(255);   // Turn LED on
      } else {
        setLedBrightness(0);     // Turn LED off
      }
      server.send(200, "text/plain", ledOn ? "LED on" : "LED off");
    }
    else {
      commandEffect = true;
      commandEffectStartTime = millis();

      if (command == "next") commandEffectType = 0;
      else if (command == "prev") commandEffectType = 1;
      else if (command == "start") commandEffectType = 2;
      else if (command == "exit") commandEffectType = 3;
      else if (command == "current") commandEffectType = 4;
      else commandEffectType = 0;

      IPAddress broadcastIP = IPAddress(255, 255, 255, 255); // Universal broadcast
      udp.beginPacket(broadcastIP, remoteUdpPort);
      udp.write(command.c_str());
      udp.endPacket();

      server.send(200, "text/plain", "Command sent: " + command);
    }
  } else {
    server.send(400, "text/plain", "Missing command");
  }
}

void handleNotFound() {
  server.sendHeader("Location", "http://" + WiFi.localIP().toString(), true);
  server.send(302, "text/plain", "");
}

void setLedBrightness(int brightness) {
  analogWrite(LED_PIN, PWM_RANGE - (brightness * PWM_RANGE / 255));
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  analogWriteRange(PWM_RANGE);
  analogWriteFreq(10000);

  Serial.begin(115200);

  WiFi.mode(WIFI_STA);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    int tries = 0;
    while (WiFi.status() != WL_CONNECTED && tries < 10) {
      delay(500);
      Serial.print(".");
      tries++;
    }
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("\nRetrying WiFi connection...");
      delay(1000);
    }
  }

  Serial.println("\nConnected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Setup mDNS responder
  if (!MDNS.begin(hostName)) {
    Serial.println("Error setting up MDNS responder!");
  } else {
    MDNS.addService("http", "tcp", 80);
    Serial.println("mDNS responder started: http://slidecontroller.local");
  }

  udp.begin(localUdpPort);

  server.on("/", handleRoot);
  server.on("/command", handleCommand);
  server.onNotFound(handleNotFound);
  server.begin();

  setLedBrightness(0); // Turn LED off initially
}

void runCommandEffect() {
  unsigned long elapsed = millis() - commandEffectStartTime;

  switch (commandEffectType) {
    case 0: // next - quick bright pulse
      if (elapsed < 100) setLedBrightness(255);
      else if (elapsed < 300) setLedBrightness(128);
      else if (elapsed < COMMAND_EFFECT_DURATION) {
        int val = (int)((COMMAND_EFFECT_DURATION - elapsed) * 255 / (COMMAND_EFFECT_DURATION - 300));
        setLedBrightness(val);
      } else commandEffect = false;
      break;

    case 1: // prev - slow fade in and out
      if (elapsed < COMMAND_EFFECT_DURATION) {
        int val = (int)(127 + 128 * sin(2 * 3.14159 * elapsed / COMMAND_EFFECT_DURATION));
        setLedBrightness(val);
      } else commandEffect = false;
      break;

    case 2: // start - pulse up and hold bright
      if (elapsed < 500) {
        int val = (int)(elapsed * 255 / 500);
        setLedBrightness(val);
      } else if (elapsed < COMMAND_EFFECT_DURATION) {
        setLedBrightness(255);
      } else commandEffect = false;
      break;

    case 3: // exit - pulse down and off
      if (elapsed < 500) {
        int val = 255 - (int)(elapsed * 255 / 500);
        setLedBrightness(val);
      } else commandEffect = false;
      break;

    case 4: // current - slow pulse
      if (elapsed < COMMAND_EFFECT_DURATION) {
        int val = (int)(127 + 128 * sin(2 * 3.14159 * elapsed / COMMAND_EFFECT_DURATION));
        setLedBrightness(val);
      } else commandEffect = false;
      break;

    default:
      commandEffect = false;
      break;
  }
}

void runLightshow() {
  static unsigned long lastUpdate = 0;
  static int brightness = 0;
  static int fadeAmount = 5;

  if (millis() - lastUpdate > 30) {
    lastUpdate = millis();
    brightness += fadeAmount;
    if (brightness <= 0 || brightness >= 255) fadeAmount = -fadeAmount;
    setLedBrightness(brightness);
  }
}

void runBlink() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= blinkInterval) {
    previousMillis = currentMillis;
    ledBlinkState = !ledBlinkState;
    setLedBrightness(ledBlinkState ? 255 : 0);
  }
}

void loop() {
  MDNS.update(); // Required for mDNS
  server.handleClient();

  if (blinkEnabled) {
    runBlink();
  } else if (ledOn) {
    setLedBrightness(255); // LED permanently on
  } else {
    if (commandEffect) {
      runCommandEffect();
    } else {
      if (lightshowEnabled) {
        runLightshow();
      } else {
        setLedBrightness(0); // LED fully off
      }
    }
  }
}
```

---

# 2. Python UDP Server (`slide_controller.py`)

* Listens on UDP port 4211.
* Maps commands to keyboard inputs using `pyautogui`.
* Logs received commands.
* Can be converted to standalone executable with PyInstaller.

```python
import socket
import pyautogui

UDP_IP = "0.0.0.0"
UDP_PORT = 4211

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for slide commands on UDP {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(1024)
    cmd = data.decode().strip()
    print(f"Received: {cmd} from {addr}")
    if cmd == "next":
        pyautogui.press('right')
    elif cmd == "prev":
        pyautogui.press('left')
    elif cmd == "start":
        pyautogui.press('f5')
    elif cmd == "exit":
        pyautogui.press('esc')
    elif cmd == "current":
        pyautogui.hotkey("shift", "f5")

```

---

# 3. Instructions to Convert Python Script to Executable

Run these commands in your terminal/command prompt inside the directory where `slide_controller.py` resides:

```bash
pip install pyinstaller
pyinstaller --onefile --name SlideController slide_controller.py
```

* The executable will be created in `dist/SlideController.exe` (Windows).
* Double-click or run in terminal.

---

# 4. Project Folder Structure

```
slide-controller/
├── esp8266_code/
│   └── esp8266_code.ino        # ESP8266 Arduino sketch
├── python_code/
│   └── slide_controller.py     # Python UDP server script
├── README.md                   # This documentation file
└── LICENSE                     # MIT License file
```

---

# 5. Usage Summary

* Upload ESP8266 sketch after updating WiFi SSID/password and `targetIP` (your PC IP).
* Run Python UDP server on your PC.
* Connect ESP8266 to WiFi.
* Open browser on any device in the same network to `http://slidecontroller.local` or the ESP IP address.
* Control slides and LED effects wirelessly.

---

# 6. Troubleshooting Tips

* Make sure your PC firewall allows UDP port 4211 inbound.
* If `slidecontroller.local` doesn't work, find ESP IP from Serial Monitor and use it.
* Presentation window must be focused for `pyautogui` to send keypresses.
* For macOS, you might need to grant accessibility permissions to control keyboard.
* Confirm `LED_BUILTIN` pin is correct for your ESP board (GPIO2 for NodeMCU).
* Use wired keyboard keys mapping matching your presentation software.

---

# 7. Security Considerations

* This system operates on your local network only.
* No authentication on the web server—consider adding if exposing to larger networks.
* UDP communication is unencrypted.
* Limit access via WiFi network control or VPN.

---

# 8. Future Enhancements (Suggestions)

* Add dynamic configuration page to set target IP, WiFi credentials.
* Implement HTTPS and basic auth for web UI.
* Add WebSocket communication to get real-time LED status feedback on UI.
* Support more complex key sequences or macros.
* Add OTA update for ESP8266 firmware.
* Add mobile app with Bluetooth or MQTT backend.

---

# 9. License (MIT)

```text
MIT License
...

MIT License

Copyright (c) 2025 Lovnish Verma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---
