# Slide Controller

A system to control presentation slides (e.g., PowerPoint, Keynote) using an ESP8266-based web interface and a Python UDP server. The ESP8266 hosts a web server to send commands (next, prev, start, exit, current) via UDP to a Python script, which simulates keyboard inputs using `pyautogui`. The ESP8266 also controls an onboard LED with visual effects (blink, lightshow, command-specific patterns). The Python script can be converted to a standalone executable using PyInstaller for easier deployment.

---

## Features

- **Web Interface**: Control slides and LED effects via a browser (accessible at `http://slidecontroller.local` or IP address).
- **UDP Communication**: Sends commands to a Python UDP server listening on port 4211.
- **LED Effects**:
  - Blink: 500ms on/off cycle.
  - Lightshow: Smooth fading effect.
  - Command-specific patterns (e.g., quick pulse for next, slow fade for prev).
  - Static on/off toggle.
- **mDNS Support**: Access the web interface via `http://slidecontroller.local` (network-dependent).
- **Executable Conversion**: Convert the Python script to a standalone `.exe` using PyInstaller for Windows deployment.
- **Cross-Platform**: Python script runs on Windows, macOS, or Linux; ESP8266 works with any WiFi network.

---

## Components

| Component            | Description                                                  |
|----------------------|--------------------------------------------------------------|
| **Python UDP Server** | Listens for UDP packets on port 4211 and simulates keyboard inputs. |
| **ESP8266 Sketch**    | Hosts web server on port 80, sends UDP commands, controls onboard LED with PWM. |

---

## Requirements

### Hardware
- ESP8266 board (e.g., NodeMCU, Wemos D1 Mini)
- Onboard LED (connected to `LED_BUILTIN`, active-low)
- WiFi network access

### Software
- **Python Environment** (for running/converting the script):
  - Python 3.x
  - `pyautogui` (`pip install pyautogui`)
  - `PyInstaller` (for executable conversion, `pip install pyinstaller`)
- **Arduino Environment**:
  - Arduino IDE or compatible editor
  - ESP8266 board support: [ESP8266 Arduino Core](http://arduino.esp8266.com/stable/package_esp8266com_index.json)
  - Libraries: `ESP8266WiFi`, `ESP8266WebServer`, `WiFiUdp`, `ESP8266mDNS`
- Presentation software that responds to keyboard inputs (e.g., PowerPoint, Keynote)
- OS: Windows (for `.exe`), macOS, or Linux

---

## Project Structure

```

slide-controller/
├── python/
│   └── slide\_controller.py    # Python UDP server script
├── esp8266/
│   └── slide\_controller.ino   # ESP8266 Arduino sketch
├── README.md                  # Project documentation
└── LICENSE                    # License file (MIT)

````

---

## Setup

### Python UDP Server

1. **Install Dependencies:**

```bash
pip install pyautogui pyinstaller
````

2. **Save the Script:**

Save `python/slide_controller.py` to your project directory.

3. **Run the Script:**

```bash
python python/slide_controller.py
```

The script listens on UDP `0.0.0.0:4211` and logs received commands. Make sure your presentation software is active to receive key presses.

---

### Converting Python Script to Executable

1. **Install PyInstaller:**

```bash
pip install pyinstaller
```

2. **Navigate to Python Directory:**

```bash
cd python
```

3. **Create Executable:**

```bash
pyinstaller --onefile --name SlideController slide_controller.py
```

* `--onefile`: Packages everything into a single executable.
* `--name SlideController`: Names the output executable `SlideController.exe`.

4. **Locate Executable:**

The `.exe` will be created in `python/dist/SlideController.exe`.

5. **Run Executable:**

Double-click `SlideController.exe` or run from command line:

```bash
./dist/SlideController.exe
```

---

### ESP8266 Setup

1. **Install Arduino IDE and ESP8266 Support:**

* Add ESP8266 board URL to Arduino IDE Preferences:
  `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
* Install ESP8266 platform from Boards Manager.

2. **Install Required Libraries:**
   Install via Library Manager:
   `ESP8266WiFi`, `ESP8266WebServer`, `WiFiUdp`, `ESP8266mDNS`

3. **Open Sketch:**
   Open `esp8266/slide_controller.ino` in Arduino IDE.

4. **Configure WiFi Credentials:**

```cpp
const char* ssid = "your-ssid";
const char* password = "your-password";
```

5. **(Optional) Update UDP Target IP:**

If not using UDP broadcast, replace broadcast IP:

```cpp
IPAddress broadcastIP(192, 168, 1, 100); // Replace with your Python server IP
```

6. **Upload Sketch:**
   Connect ESP8266 and upload.

7. **Monitor Serial:**
   Open Serial Monitor at 115200 baud to see IP address and status.

---

## Usage

1. **Start Python Server:**

Run the Python script or executable. Ensure the presentation is open and focused.

2. **Power On ESP8266:**

Ensure it connects to WiFi.

3. **Access Web Interface:**

Open a browser and navigate to:

* `http://slidecontroller.local` (if mDNS works), or
* The ESP8266 IP address (e.g., `http://192.168.x.x`).

4. **Control Presentation:**

Buttons available on the web interface:

| Button         | Action                 | Keyboard Equivalent |
| -------------- | ---------------------- | ------------------- |
| Next Slide     | Move to next slide     | Right Arrow         |
| Previous Slide | Move to previous slide | Left Arrow          |
| Start          | Start presentation     | F5                  |
| Exit           | Exit presentation mode | Esc                 |
| Current Slide  | Go to current slide    | Shift + F5          |

5. **LED Controls:**

* Toggle Blink (500ms cycle)
* Toggle Lightshow (fading effect)
* Toggle LED On/Off
* Visual LED feedback on slide commands

---

## Testing

### Python Server

Send test UDP packets from terminal:

```bash
echo -n "next" | nc -u 127.0.0.1 4211
```

Verify presentation responds and server logs commands.

### ESP8266

* Open web interface, click buttons.
* Confirm LED reacts to effects and commands.
* Confirm Python server logs commands.
* Presentation responds accordingly.

---

## Troubleshooting

* **WiFi Connection:** Check SSID/password and signal.
* **UDP Issues:** Ensure UDP port 4211 is open on host firewall.
* **Web Interface:** Use IP if `slidecontroller.local` does not resolve.
* **Python/Executable:** Test `pyautogui` with a simple script. Check for antivirus blocking.
* **LED:** Verify `LED_BUILTIN` pin and active-low behavior.
* **Presentation:** Focus window and check key mapping compatibility.

---

## Security Notes

* Python UDP server listens on all interfaces (`0.0.0.0`). Restrict IP in production.
* ESP8266 web server is open on local network. Add authentication if needed.
* Secure WiFi credentials and executable distribution.
* Use private networks or VPN to avoid unauthorized access.

---

## Future Improvements

* Add command-line args for UDP IP/port in Python.
* GUI for Python server using Tkinter.
* Configurable UDP target IP on ESP8266 via web interface.
* WebSocket support for LED status updates.
* EEPROM storage for ESP8266 settings persistence.
* OTA firmware updates using ArduinoOTA.
* Support more presentation software key mappings.
* Mobile app for remote control.
* Enhanced security (HTTPS, token auth).

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Contributions welcome! Please submit pull requests or open issues on GitHub.

---

## Contact

For questions or support, open an issue on the GitHub repository.

---

## Acknowledgments

* Built with PyInstaller for executable conversion.
* Uses ESP8266 Arduino Core for WiFi and web server functionality.
* Inspired by the need for simple, wireless presentation control.

```
**Made with Lots of Love by Lovnish Verma**
---
