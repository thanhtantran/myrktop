# 🖥️ myrktop - Orange Pi 5 (RK3588) System Monitor

🔥 **myrktop** is a lightweight system monitor for **Orange Pi 5 (RK3588)**, providing real-time information about **CPU, GPU, NPU, RAM, RGA, and system temperatures**.

## **📥 Installation Instructions**
### **1️⃣ Install Required Dependencies**
Before running the script, install `lm-sensors` to fetch temperature readings:
```bash
sudo apt update && sudo apt install -y lm-sensors
```

### **2️⃣ Download and Install myrktop**
Run the following command to download and install the script:
```bash
wget -O /usr/local/bin/myrktop.sh https://raw.githubusercontent.com/mhl221135/myrktop/main/myrktop.sh
wget -O /usr/local/bin/myrktop https://raw.githubusercontent.com/mhl221135/myrktop/main/myrktop
```
Then, make the script executable:
```bash
sudo chmod +x /usr/local/bin/myrktop.sh
sudo chmod +x /usr/local/bin/myrktop
```

### **3️⃣ Run the Monitoring Script**
To run the script with **live updates every 0.5 seconds**, use:
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
- **Runs efficiently on Orange Pi 5 (RK3588)**

---

## **📌 Example Output**
```bash
Every 0.5s: /usr/local/bin/myrktop                                        orangepi5: Wed Mar 12 13:28:15 2025

🔥 Orange Pi 5 - System Monitor 🔥
Device: rockchip,rk3588s-orangepi-5rockchip,rk3588
Version: RKNPU driver: v0.9.8
--------------------------------------
📊 CPU Usage & Frequency:
Total CPU Load: 4%
Core 0: 4% 1800 MHz
Core 1: 4% 1800 MHz
Core 2: 4% 1800 MHz
Core 3: 4% 1800 MHz
Core 4: 4% 600 MHz
Core 5: 4% 600 MHz
Core 6: 4% 600 MHz
Core 7: 4% 600 MHz
--------------------------------------
🎮 GPU Load: 0%
🎮 GPU Frequency: 300 MHz
🧠 NPU Load: 0% 0% 0%
🧠 NPU Frequency: 1000 MHz
🖼️  RGA Load: 0% 0% 0%
--------------------------------------
🖥️  RAM & Swap Usage:
RAM Used: 1.8Gi / 15Gi
Swap Used: 16Mi / 7.8Gi
--------------------------------------
🌡️  Temperatures:
npu_thermal-virtual-0: +33.3°C
center_thermal-virtual-0: +32.4°C
bigcore1_thermal-virtual-0: +34.2°C
soc_thermal-virtual-0: +34.2°C
nvme-pci-44100: +31.9°C
gpu_thermal-virtual-0: +32.4°C
littlecore_thermal-virtual-0: +33.3°C
bigcore0_thermal-virtual-0: +33.3°C
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

