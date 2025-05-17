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
