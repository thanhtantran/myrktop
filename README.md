# 🖥️ myrktop - Orange Pi 5 (RK3588) System Monitor COLORED BRANCH

🔥 **myrktop** is a lightweight system monitor for **Orange Pi 5 (RK3588)**, providing real-time information about **CPU, GPU, NPU, RAM, RGA, and system temperatures**.

## **📥 Installation Instructions**
### **1️⃣ Install Required Dependencies**
Before running the script, install dependencies to fetch readings:
```bash
sudo apt update && sudo apt install -y python3 python3-pip lm-sensors smartmontools nvme-cli && sudo sensors-detect --auto && pip3 install urwid
```

### **2️⃣ Download and Install myrktop**
Run the following command to download and install the script:
```bash
wget -O ~/myrktop.sh https://raw.githubusercontent.com/mhl221135/myrktop/refs/heads/py-colored/myrktop.py
wget -O /usr/local/bin/myrktop https://raw.githubusercontent.com/mhl221135/myrktop/refs/heads/py-colored/myrktop
```
Then, make the script executable:
```bash
sudo chmod +x /usr/local/bin/myrktop
```

### **3️⃣ Run the Monitoring Script**
To run the script use:
```bash
myrktop
```

---

## **📊 Features**
- **Real-time CPU load & frequency monitoring (per core)**
- **Live GPU usage & frequency**
- **NPU & RGA usage**
- **RAM & Swap usage**
- **System temperature readings**
- **Net (eth0): Down/Up readings**
- **Storage Usage (/etc/fstab)**
- **NVMe & USB Storage Info:**


---

## **📌 Example Output**
```bash
──────────────────────────────────────────────────
🔥 System Monitor
──────────────────────────────────────────────────
Device: rockchip,rk3588s-orangepi-5rockchip,rk3588
NPU Version: RKNPU driver: v0.9.8
System Uptime: up 1 day, 1 hour, 31 minutes
Docker Status: Running ✅
──────────────────────────────────────────────────
📊 CPU Usage & Frequency:
Core 0:   8% 1800MHz   Core 1:   9% 1800MHz
Core 2:   3% 1800MHz   Core 3:   5% 1800MHz
Core 4:   7% 2352MHz   Core 5:  10% 2352MHz
Core 6:  14% 2304MHz   Core 7:   7% 2304MHz
──────────────────────────────────────────────────
🎮 GPU Load:   0%    300 MHz
──────────────────────────────────────────────────
🧠 NPU Load: 0% 0% 0%   1000 MHz
──────────────────────────────────────────────────
🖼️  RGA Load: 0% 0% 0%
──────────────────────────────────────────────────
🖥️  RAM & Swap Usage:
RAM Used: 2.9Gi / 15Gi
Swap Used: 12Mi / 7.8Gi
──────────────────────────────────────────────────
🌡️  Temperatures:
npu_thermal-virtual-0          33°C
center_thermal-virtual-0       32°C
bigcore1_thermal-virtual-0     33°C
soc_thermal-virtual-0          33°C
nvme-pci-44100                 30°C
gpu_thermal-virtual-0          32°C
littlecore_thermal-virtual-0   33°C
bigcore0_thermal-virtual-0     33°C
──────────────────────────────────────────────────
🌐 Net (eth0): Down 0.01 Mbps | Up 0.05 Mbps
──────────────────────────────────────────────────
💾 Storage Usage (/etc/fstab):
Mount Point             Total     Used     Free
/                         59G     6.1G      52G
/tmp                     7.8G     8.0K     7.8G
/media/ssdmount          938G     314G     577G
/media/wdmount           1.8T     369G     1.4T
──────────────────────────────────────────────────
💿 NVMe & USB Storage Info:
NVMe Devices:
nvme0n1 - Unknown | Temp: 32°C | Hours: 207
USB Storage Devices:
sda - Elements 10B8 | Temp: 34°C | Hours: 16545
──────────────────────────────────────────────────
Press 'q' to exit. Use arrows or mouse to scroll.
```

---

## **🔧 How to Contribute**
If you find a bug or want to improve **myrktop**, feel free to fork the repository and submit a pull request.

📂 **GitHub Repository:** [https://github.com/mhl221135/myrktop](https://github.com/mhl221135/myrktop)

---

## **❓ Support**
If you have any issues, open an issue on GitHub, or contact me!

---

### **🔗 License**
This project is **open-source** and available under the **MIT License**.

