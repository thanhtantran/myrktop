# 🖥️ myrktop - Orange Pi 5 (RK3588) System Monitor COLORED BRANCH

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
wget -O ~/myrktop.sh https://raw.githubusercontent.com/mhl221135/myrktop/colored/myrktop.sh
wget -O /usr/local/bin/myrktop https://raw.githubusercontent.com/mhl221135/colored/main/myrktop
```
Then, make the script executable:
```bash
sudo chmod +x ~/myrktop.sh
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
Every 0.5s: /root/myrktop.sh                                                                                                                      orangepi5: Thu Mar 13 11:30:16 2025

───────────────────────────────────────────────────────────
 🔥 Orange Pi 5 - System Monitor
───────────────────────────────────────────────────────────
 Device: rockchip,rk3588s-orangepi-5rockchip,rk3588
 Version: RKNPU driver: v0.9.8
───────────────────────────────────────────────────────────
 📊 CPU Usage & Frequency
 Total CPU Load:   2%
 Core 0:   1%  1800 MHz   Core 4:   1%  2352 MHz
 Core 1:   1%  1800 MHz   Core 5:   1%  2352 MHz
 Core 2:   1%  1800 MHz   Core 6:   1%   408 MHz
 Core 3:   1%  1800 MHz   Core 7:   2%   408 MHz
───────────────────────────────────────────────────────────
 🎮 GPU Load:   0%   300 MHz
───────────────────────────────────────────────────────────
 🧠 NPU Load: 0% 0% 0%    1000 MHz
───────────────────────────────────────────────────────────
 🖼️  RGA Load: 0% 0% 0%  
───────────────────────────────────────────────────────────
 🌡️ Temperatures
 npu_thermal-virtual-0          36°C
 center_thermal-virtual-0       35°C
 bigcore1_thermal-virtual-0     36°C
 soc_thermal-virtual-0          36°C
 nvme-pci-44100                 34°C
 gpu_thermal-virtual-0          35°C
 littlecore_thermal-virtual-0   36°C
 bigcore0_thermal-virtual-0     36°C
───────────────────────────────────────────────────────────
 📊 Disk Usage
 /                  59G     5.2G    53G
 /media/ssdmount    938G    305G    586G
 /media/wdmount     1.8T    356G    1.4T
───────────────────────────────────────────────────────────
 🔌 Network Traffic (eth0)
 Download: 0     Mbps | Upload: .02   Mbps
───────────────────────────────────────────────────────────
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

