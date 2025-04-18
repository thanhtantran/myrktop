# 🖥️ myrktop - Orange Pi 5/5 Plus (RK3588) System Monitor COLORED

🔥 **myrktop** is a lightweight system monitor for **Orange Pi 5/5 Plus (RK3588)**, providing real-time information about **CPU, GPU, NPU, RAM, RGA, and system temperatures**.

## **📥 Installation Instructions**
### **1️⃣ Install Required Dependencies**
Before running the script, install dependencies to fetch readings:
```bash
sudo apt update && sudo apt install -y python3 python3-pip lm-sensors smartmontools nvme-cli
sudo sensors-detect --auto
sudo pip install urwid
```

### **2️⃣ Download and Install myrktop**
Run the following command to download and install the script:
```bash
git clone https://github.com/thanhtantran/myrktop
```
Then, make the script executable:
```bash
sudo chmod +x myrktop/myrktop.py
```

### **3️⃣ Run the Monitoring Script**
To run the script use:
```bash
sudo python myrktop/myrktop.py
```

---

## **📊 Features**
- **Real-time CPU load & frequency monitoring (per core)**
- **Live GPU usage & frequency**
- **NPU & RGA usage**
- **RAM & Swap usage**
- **System temperature readings**
- **Network: Down/Up readings**
- **Storage Usage (/etc/fstab)**
- **NVMe & USB Storage Info:**


---

## **📌 Example Output**
![orangepi5-myrktop](https://github.com/user-attachments/assets/b26225af-7d15-4d32-aa1d-248d91d4f9e6)

![orangepi5plus-myrktop](https://github.com/user-attachments/assets/b8af73ce-b58c-4090-bccc-518e6144f6c8)


## **🔧 How to Contribute**
This code is forked form other author. If you find a bug or want to improve **myrktop**, feel free to fork the original repository and submit a pull request.

📂 **GitHub Repository:** [https://github.com/mhl221135/myrktop](https://github.com/mhl221135/myrktop)

---

## **❓ Support**
If you have any issues, open an issue on GitHub, or contact me!

---

### **🔗 License**
This project is **open-source** and available under the **MIT License**.

