# Hermez Link — PS5 Payload Sender for Android

A Kivy-based Android app for sending payloads to your PS5 over TCP.

## Features
- Send `.bin` payloads to PS5 via TCP socket
- Save & manage multiple PS5 IPs (tap ▾ to pick)
- Save & manage port presets (default: 9021)
- Browse and select payload files on device
- Live log output with color-coded status
- Persistent storage across app restarts

---

## Build Instructions

### Requirements (Ubuntu/Debian WSL or native Linux)
```bash
sudo apt update && sudo apt install -y \
    python3-pip git zip unzip openjdk-17-jdk \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake libffi-dev libssl-dev

pip3 install buildozer cython
```

### Build
```bash
cd hermez_sender/
buildozer android debug
```

The `.apk` will be in `bin/` — copy to your phone and install.

> First build takes ~20–30 min (downloads NDK/SDK). Subsequent builds are fast.

### If you're on Windows
Use WSL2 (Ubuntu). Buildozer doesn't work natively on Windows.

---

## Usage
1. Put your PS5 in exploit mode (webpage exploit / BD-J etc.)
2. Open Hermez Link
3. Enter or select your PS5's IP and port (default 9021)
4. Browse and select your `.bin` payload
5. Tap **⚡ SEND PAYLOAD**
6. Watch the log — green = success

---

## Adding a custom icon
Replace `icon.png` in the project root with a 512×512 PNG before building.

---

## Notes
- The app stores data in `~/.hermez_data.json` on the device
- Port 9021 is the default for ps5-payload-elfldr / Hermez
- Requires the PS5 to be on the same Wi-Fi network
