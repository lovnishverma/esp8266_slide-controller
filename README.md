Slide Controller
   A system to control presentation slides (e.g., PowerPoint, Keynote) using an ESP8266-based web interface and a Python UDP server. The ESP8266 hosts a web server to send commands (next, prev, start, exit, current) via UDP to a Python script, which simulates keyboard inputs using pyautogui. The ESP8266 also controls an onboard LED with visual effects (blink, lightshow, command-specific patterns).
Features

Web Interface: Control slides and LED effects via a browser (accessible at http://slidecontroller.local or IP address).
UDP Communication: Sends commands to a Python UDP server listening on port 4211.
LED Effects:
Blink: 500ms on/off cycle.
Lightshow: Smooth fading effect.
Command-specific patterns (e.g., quick pulse for next, slow fade for prev).
Static on/off toggle.


mDNS Support: Access the web interface via http://slidecontroller.local (network-dependent).
Security: Basic HTTP authentication (username: admin, password: password).

Components

Python UDP Server (python/slide_controller.py):
Listens for UDP packets on port 4211.
Simulates keyboard inputs to control presentation software.


ESP8266 Sketch (esp8266/slide_controller.ino):
Hosts a web server on port 80.
Sends UDP commands to the Python server.
Controls the onboard LED with PWM.



Requirements
Hardware

ESP8266 board (e.g., NodeMCU, Wemos D1 Mini).
Onboard LED (connected to LED_BUILTIN, active-low).
WiFi network access.

Software

Python Environment:
Python 3.x
pyautogui (pip install pyautogui)


Arduino Environment:
Arduino IDE or compatible editor.
ESP8266 board support (http://arduino.esp8266.com/stable/package_esp8266com_index.json).
Libraries: ESP8266WiFi, ESP8266WebServer, WiFiUdp, ESP8266mDNS (install via Arduino Library Manager).


Presentation Software: Must respond to keyboard inputs (e.g., right/left arrows, F5, Esc, Shift+F5).

Setup
Python UDP Server

Install Python 3.x and pyautogui:pip install pyautogui


Save python/slide_controller.py to your computer.
Run the script:python python/slide_controller.py


Ensure the presentation software is active to receive key presses.

ESP8266

Install the Arduino IDE and ESP8266 board support.
Install required libraries via the Library Manager.
Open esp8266/slide_controller.ino in the Arduino IDE.
Update WiFi credentials in the sketch:const char* ssid = "your-ssid";
const char* password = "your-password";


(Optional) Update the UDP target IP if not using broadcast:IPAddress targetIP(192, 168, 1, 100); // Replace with Python server's IP


Flash the sketch to the ESP8266 board.
Open the Serial Monitor (115200 baud) to view the IP address or use http://slidecontroller.local.

Usage

Ensure both the Python script and ESP8266 are running on the same WiFi network.
Open a browser and navigate to http://slidecontroller.local or the ESP8266’s IP address.
Log in with username admin and password password.
Use the web interface to:
Control slides: Click Next, Previous, Start, Exit, or Current.
Control LED: Toggle Blink, Lightshow, or LED.


Observe LED effects and check the Python script’s console for received commands.

Testing

Python Server: Send test UDP packets:echo -n "next" | nc -u 127.0.0.1 4211


ESP8266: Access the web interface and click buttons. Verify:
LED responds with appropriate effects.
Python script logs commands (e.g., Received: next from (<ESP_IP>, 4210)).
Presentation software responds to key presses.



Troubleshooting

WiFi Connection:
Check credentials and signal strength.
If connection fails, the ESP8266 starts an AP (SlideControllerAP, password: 12345678).


UDP Issues:
Ensure port 4211 is open on the Python server’s host.
Verify the network allows UDP broadcasts or use a specific target IP.


Web Interface:
If slidecontroller.local fails, use the IP address from the Serial Monitor.
Clear browser cache if the page doesn’t load.


LED:
Confirm LED_BUILTIN is active-low (0 = full brightness, 1023 = off).


Presentation:
Ensure the presentation window is focused.
Verify key mappings match your software.



Security Notes

The Python server listens on 0.0.0.0:4211, allowing commands from any IP. Restrict to a specific IP for production use.
The ESP8266 web server uses basic authentication but is accessible to anyone on the network. Consider stronger authentication or a VPN for public networks.
Hardcoded WiFi credentials and authentication details should be secured or made configurable.

Future Improvements

Configurable UDP target IP via the web interface.
WebSocket for real-time LED status updates.
EEPROM storage for settings persistence.
Over-The-Air (OTA) updates for the ESP8266.
Support for additional presentation software key mappings.

License
   MIT License
Contributing
   Contributions are welcome! Please submit pull requests or open issues on GitHub.
Contact
   For questions or support, open an issue on the GitHub repository.
