#!/usr/bin/env python3
import urwid
import subprocess
import re
import os
import time

# Globals for CPU and network measurements
prev_cpu = {}
prev_rx = None
prev_tx = None
prev_net_time = None

def get_device_info():
    try:
        device_info = subprocess.check_output(
            "cat /sys/firmware/devicetree/base/compatible", shell=True, stderr=subprocess.DEVNULL
        ).decode("utf-8").replace("\x00", "").strip()
    except Exception:
        device_info = "N/A"
    try:
        npu_version = subprocess.check_output(
            "cat /sys/kernel/debug/rknpu/version", shell=True, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        npu_version = "N/A"
    try:
        uptime = subprocess.check_output("uptime -p", shell=True).decode("utf-8").strip()
    except Exception:
        uptime = "N/A"
    try:
        docker_status = subprocess.check_output("systemctl is-active docker", shell=True, stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        docker_status = "N/A"
    return device_info, npu_version, uptime, docker_status

def get_cpu_info():
    cpu_loads = {}
    core_count = os.cpu_count()
    global prev_cpu
    for i in range(core_count):
        try:
            with open("/proc/stat", "r") as f:
                lines = f.readlines()
            line = next((l for l in lines if l.startswith(f"cpu{i} ")), None)
            if not line:
                continue
            parts = line.split()
            user = int(parts[1])
            nice = int(parts[2])
            system = int(parts[3])
            idle = int(parts[4])
            iowait = int(parts[5])
            irq = int(parts[6])
            softirq = int(parts[7])
            steal = int(parts[8]) if len(parts) > 8 else 0
            total = user + nice + system + idle + iowait + irq + softirq + steal
        except Exception:
            continue

        if i in prev_cpu:
            prev_total, prev_idle = prev_cpu[i]
            diff_total = total - prev_total
            diff_idle = idle - prev_idle
            load = (100 * (diff_total - diff_idle)) // diff_total if diff_total > 0 else 0
        else:
            load = 0
        cpu_loads[i] = load
        prev_cpu[i] = (total, idle)

    cpu_freqs = {}
    for i in range(core_count):
        try:
            with open(f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_cur_freq", "r") as f:
                freq_str = f.read().strip()
            freq = int(freq_str) // 1000  # Convert kHz to MHz
        except Exception:
            freq = 0
        cpu_freqs[i] = freq
    return cpu_loads, cpu_freqs



def get_gpu_info():
    try:
        with open("/sys/class/devfreq/fb000000.gpu/load", "r") as f:
            raw_line = f.read().strip()  # e.g., "0@300000000Hz"
        # Split using '@' or space (same as -F'[@ ]' in AWK)
        fields = re.split(r'[@ ]+', raw_line)
        # The first field is the GPU load (as a number)
        load_str = fields[0]
        # If there's a trailing '%' remove it (not needed for your case)
        if load_str.endswith('%'):
            load_str = load_str[:-1]
        gpu_load = int(load_str)
    except Exception:
        gpu_load = 0

    try:
        with open("/sys/class/devfreq/fb000000.gpu/cur_freq", "r") as f:
            gpu_freq_str = f.read().strip()
        # Convert Hz to MHz
        gpu_freq = int(gpu_freq_str) // 1000000
    except Exception:
        gpu_freq = 0

    return gpu_load, gpu_freq



def get_npu_info():
    try:
        with open("/sys/kernel/debug/rknpu/load", "r") as f:
            data = f.read()
        percents = re.findall(r'(\d+)%', data)
        if percents:
            npu_load = " ".join([p + "%" for p in percents])
        else:
            npu_load = "0% 0% 0%"
    except Exception:
        npu_load = "0% 0% 0%"
    try:
        with open("/sys/class/devfreq/fdab0000.npu/cur_freq", "r") as f:
            npu_freq_str = f.read().strip()
        npu_freq = int(npu_freq_str) // 1000000
    except Exception:
        npu_freq = 0
    return npu_load, npu_freq

def get_rga_info():
    try:
        with open("/sys/kernel/debug/rkrga/load", "r") as f:
            data = f.read()
        rga_values = re.findall(r'load = (\d+)%', data)
        if rga_values:
            rga_values = " ".join([v + "%" for v in rga_values[:3]])
        else:
            rga_values = "0% 0% 0%"
    except Exception:
        rga_values = "0% 0% 0%"
    return rga_values

def get_ram_swap_info():
    try:
        free_output = subprocess.check_output("free -h", shell=True).decode("utf-8")
        lines = free_output.splitlines()
        ram_line = next((l for l in lines if l.startswith("Mem:")), None)
        swap_line = next((l for l in lines if l.startswith("Swap:")), None)
        if ram_line:
            parts = ram_line.split()
            ram_total = parts[1]
            ram_used = parts[2]
        else:
            ram_total = ram_used = "N/A"
        if swap_line:
            parts = swap_line.split()
            swap_total = parts[1]
            swap_used = parts[2]
        else:
            swap_total = swap_used = "N/A"
    except Exception:
        ram_used, ram_total, swap_used, swap_total = "N/A", "N/A", "N/A", "N/A"
    return ram_used, ram_total, swap_used, swap_total

def get_temperatures():
    """
    Process the output of 'sensors' so that any line containing keywords like "thermal",
    "nvme" or "gpu" sets the sensor name, and any subsequent line containing "temp1:" or "Composite:" 
    uses that sensor name when displaying the reading. The numeric temperature is extracted
    using a substring approach similar to your original AWK code.
    """
    try:
        output = subprocess.check_output("sensors", shell=True, stderr=subprocess.DEVNULL).decode("utf-8")
        lines = output.splitlines()
        temp_items = []
        current_name = None
        for line in lines:
            # If the line doesn't contain a colon and has only one field, assume it's a sensor name
            if ":" not in line and len(line.split()) == 1:
                current_name = line.strip()
                continue
            # If the line starts with "temp1:" or "Composite:" then process it
            if line.startswith("temp1:") or line.startswith("Composite:"):
                fields = line.split()
                if len(fields) < 2:
                    continue
                raw_temp = fields[1]  # e.g., "+34.2°C"
                if len(raw_temp) >= 5:
                    # Extract substring from index 1 to len(raw_temp)-4 (mimics AWK's substr($2,2,length($2)-5))
                    temp_str = raw_temp[1:len(raw_temp)-4]
                    try:
                        temp_val = int(float(temp_str))
                    except Exception:
                        temp_val = 0
                    if temp_val >= 70:
                        attr = 'temp_red'
                    elif temp_val >= 60:
                        attr = 'temp_yellow'
                    else:
                        attr = 'temp_green'
                    sensor_name = current_name if current_name is not None else fields[0]
                    formatted = f"{sensor_name:<30} {temp_val:2d}°C"
                    temp_items.append((attr, formatted))
                else:
                    temp_items.append(("default", line))
            else:
                pass
        if not temp_items:
            temp_items = [("default", "No temperature data.")]
    except Exception:
        temp_items = [("default", "No temperature data.")]
    return temp_items

def get_network_traffic():
    global prev_stats, prev_net_time
    
    # Khởi tạo cấu trúc lưu trữ
    current_stats = {}
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()
        
        # Tìm tất cả interface eth0 và enP*
        interfaces = []
        for line in lines:
            if ":" in line:
                ifname = line.split(":")[0].strip()
                if ifname == "eth0" or ifname.startswith("enP"):
                    interfaces.append(ifname)
        
        # Lấy thông số cho từng interface
        for ifname in interfaces:
            line = next((l for l in lines if f"{ifname}:" in l), None)
            if line:
                parts = line.split()
                rx = int(parts[1])
                tx = int(parts[9])
                current_stats[ifname] = {'rx': rx, 'tx': tx}
                
    except Exception:
        pass  # Xử lý lỗi nếu cần
    
    current_time = time.time()
    
    # Khởi tạo kết quả trả về
    results = {}
    
    if prev_net_time is None:
        # Lần đầu chạy, chỉ lưu giá trị hiện tại
        prev_stats = current_stats
        prev_net_time = current_time
        for ifname in current_stats:
            results[ifname] = (0.0, 0.0)  # Down 0, Up 0
    else:
        # Tính toán tốc độ
        dt = current_time - prev_net_time
        if dt > 0:
            # Tính cho các interface hiện có
            for ifname in current_stats:
                if ifname in prev_stats:
                    rx_rate = (current_stats[ifname]['rx'] - prev_stats[ifname]['rx']) * 8 / (1e6 * dt)
                    tx_rate = (current_stats[ifname]['tx'] - prev_stats[ifname]['tx']) * 8 / (1e6 * dt)
                else:
                    rx_rate = tx_rate = 0.0
                results[ifname] = (rx_rate, tx_rate)
            
            # Cập nhật giá trị cũ
            prev_stats = current_stats
            prev_net_time = current_time
    
    return results

def get_fstab_disk_usage():
    mountpoints = []
    try:
        with open("/etc/fstab", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                fields = line.split()
                if len(fields) < 2:
                    continue
                mount = fields[1]
                if mount not in mountpoints:
                    mountpoints.append(mount)
    except Exception:
        mountpoints = []
    usage_lines = []
    header = f"{'Mount Point':<20} {'Total':>8} {'Used':>8} {'Free':>8}"
    usage_lines.append(header)
    for m in mountpoints:
        try:
            df_output = subprocess.check_output(f"df -h {m}", shell=True, stderr=subprocess.DEVNULL).decode("utf-8")
            df_lines = df_output.splitlines()
            if len(df_lines) >= 2:
                parts = df_lines[1].split()
                if len(parts) >= 6:
                    mp = parts[5]
                    total = parts[1]
                    used = parts[2]
                    free = parts[3]
                    line_usage = f"{mp:<20} {total:>8} {used:>8} {free:>8}"
                    usage_lines.append(line_usage)
                else:
                    usage_lines.append(f"{m}: No info")
        except Exception:
            usage_lines.append(f"{m}: No info")
    if not usage_lines:
        usage_lines = ["No disk usage info from /etc/fstab."]
    return usage_lines

def get_storage_info():
    nvme_devices = []
    usb_devices = []
    try:
        lsblk_output = subprocess.check_output("lsblk -dno NAME,TYPE", shell=True).decode("utf-8")
        for line in lsblk_output.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                name, typ = parts[0], parts[1]
                if typ == "disk" and name.startswith("nvme"):
                    nvme_devices.append(name)
    except Exception:
        pass
    try:
        lsblk_usb = subprocess.check_output("lsblk -dno NAME,TRAN", shell=True).decode("utf-8")
        for line in lsblk_usb.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                name, tran = parts[0], parts[1]
                if tran == "usb":
                    usb_devices.append(name)
    except Exception:
        pass

    nvme_info = []
    for dev in nvme_devices:
        try:
            model = subprocess.check_output(
                f"nvme id-ctrl /dev/{dev} | grep 'Model Number'", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8").split(":")[1].strip()
        except Exception:
            model = "Unknown"
        try:
            health = subprocess.check_output(
                f"nvme smart-log /dev/{dev} | grep 'percentage_used'", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8").split()[2].replace("%", "").strip()
        except Exception:
            health = "0"
        try:
            temp = subprocess.check_output(
                f"nvme smart-log /dev/{dev} | grep 'temperature'", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8").split()[2].strip()
        except Exception:
            temp = "N/A"
        try:
            power_hours = subprocess.check_output(
                f"nvme smart-log /dev/{dev} | grep 'power_on_hours'", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8").split()[2].strip()
        except Exception:
            power_hours = "N/A"
        nvme_info.append(f"{dev} - {model} | Temp: {temp}°C | Hours: {power_hours}")
    
    usb_info = []
    for dev in usb_devices:
        try:
            model = subprocess.check_output(
                f"lsblk -dno MODEL /dev/{dev}", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
        except Exception:
            model = "Unknown"
        try:
            health_out = subprocess.check_output(
                f"smartctl -H /dev/{dev}", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8")
            health_match = re.search(r':\s*(\S+)', health_out)
            health = health_match.group(1) if health_match else "Unknown"
        except Exception:
            health = "Unknown"
        try:
            temp_out = subprocess.check_output(
                f"smartctl -A /dev/{dev} | grep 'Temperature_Celsius'", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8").split()[9]
            temp = temp_out
        except Exception:
            temp = "N/A"
        try:
            power_hours_out = subprocess.check_output(
                f"smartctl -A /dev/{dev} | grep 'Power_On_Hours'", shell=True, stderr=subprocess.DEVNULL
            ).decode("utf-8").split()[9]
            power_hours = power_hours_out
        except Exception:
            power_hours = "N/A"
        usb_info.append(f"{dev} - {model} | Temp: {temp}°C | Hours: {power_hours}")
    return nvme_info, usb_info

def build_dashboard():
    lines = []
    sep = "─" * 50

    # Header
    lines.append(("header", sep))
    title = "🔥 System Monitor"
    lines.append(("header", title))
    lines.append(("header", sep))

    # Device Info
    device_info, npu_version, uptime, docker_status = get_device_info()
    lines.append(("default", f"Device: {device_info}"))
    lines.append(("default", f"NPU Version: {npu_version}"))
    lines.append(("default", f"System Uptime: {uptime}"))
    if docker_status == "active":
        lines.append(("good", "Docker Status: Running ✅"))
    else:
        lines.append(("bad", "Docker Status: Not Running ❌"))
    lines.append(("header", sep))

    # CPU Info - build as markup list for colored load percentages and green bold frequencies
    cpu_loads, cpu_freqs = get_cpu_info()
    lines.append(("title", "📊 CPU Usage & Frequency:"))
    cores = sorted(cpu_loads.keys())
    for i in range(0, len(cores), 2):
        if i+1 < len(cores):
            if cpu_loads[cores[i]] >= 80:
                attr1 = 'temp_red'
            elif cpu_loads[cores[i]] >= 60:
                attr1 = 'temp_yellow'
            else:
                attr1 = 'default'
            if cpu_loads[cores[i+1]] >= 80:
                attr2 = 'temp_red'
            elif cpu_loads[cores[i+1]] >= 60:
                attr2 = 'temp_yellow'
            else:
                attr2 = 'default'
            markup = [
                ("default", f"Core {cores[i]}: "),
                (attr1, f"{cpu_loads[cores[i]]:3d}%"),
                ("default", " "),
                ("freq", f"{cpu_freqs[cores[i]]:4d}MHz   "),
                ("default", f"Core {cores[i+1]}: "),
                (attr2, f"{cpu_loads[cores[i+1]]:3d}%"),
                ("default", " "),
                ("freq", f"{cpu_freqs[cores[i+1]]:4d}MHz")
            ]
            lines.append(markup)
        else:
            if cpu_loads[cores[i]] >= 70:
                attr1 = 'temp_red'
            elif cpu_loads[cores[i]] >= 60:
                attr1 = 'temp_yellow'
            else:
                attr1 = 'default'
            markup = [
                ("default", f"Core {cores[i]}: "),
                (attr1, f"{cpu_loads[cores[i]]:3d}%"),
                ("default", " "),
                ("freq", f"{cpu_freqs[cores[i]]:4d}MHz")
            ]
            lines.append(markup)
    lines.append(("header", sep))

    # GPU Info - apply same rules to GPU load and frequency
    gpu_load, gpu_freq = get_gpu_info()
    if gpu_load >= 80:
        gpu_attr = 'temp_red'
    elif gpu_load >= 60:
        gpu_attr = 'temp_yellow'
    else:
        gpu_attr = 'default'
    gpu_markup = [
        ("title", "🎮 GPU Load: "),
        (gpu_attr, f"{gpu_load:3d}%"),
        ("default", "   "),
        ("freq", f"{gpu_freq:4d} MHz")
    ]
    lines.append(gpu_markup)
    lines.append(("header", sep))

    # NPU Info - apply same rules to NPU load and frequency
    npu_load, npu_freq = get_npu_info()
    try:
        npu_numeric = int(re.search(r'(\d+)%', npu_load).group(1))
    except Exception:
        npu_numeric = 0
    if npu_numeric >= 80:
        npu_attr = 'temp_red'
    elif npu_numeric >= 60:
        npu_attr = 'temp_yellow'
    else:
        npu_attr = 'default'
    npu_markup = [
        ("title", "🧠 NPU Load: "),
        (npu_attr, f"{npu_load}"),
        ("default", "   "),
        ("freq", f"{npu_freq:4d} MHz")
    ]
    lines.append(npu_markup)
    lines.append(("header", sep))

    # RGA Info - apply same rules for load (no frequency available)
    rga_info = get_rga_info()
    try:
        rga_numeric = int(re.search(r'(\d+)%', rga_info).group(1))
    except Exception:
        rga_numeric = 0
    if rga_numeric >= 80:
        rga_attr = 'temp_red'
    elif rga_numeric >= 60:
        rga_attr = 'temp_yellow'
    else:
        rga_attr = 'default'
    rga_markup = [
        ("title", "🖼️  RGA Load: "),
        (rga_attr, f"{rga_info}")
    ]
    lines.append(rga_markup)
    lines.append(("header", sep))

    # RAM & Swap Info
    ram_used, ram_total, swap_used, swap_total = get_ram_swap_info()
    lines.append(("title", "🖥️  RAM & Swap Usage:"))
    lines.append(("default", f"RAM Used: {ram_used} / {ram_total}"))
    lines.append(("default", f"Swap Used: {swap_used} / {swap_total}"))
    lines.append(("header", sep))

    # Temperatures
    temp_items = get_temperatures()
    lines.append(("title", "🌡️  Temperatures:"))
    for attr, text in temp_items:
        lines.append((attr, text))
    lines.append(("header", sep))

    # Network Traffic
    net_stats = get_network_traffic()
    for ifname, (rx_rate, tx_rate) in net_stats.items():
        lines.append(("title", f"🌐 Net ({ifname}): Down {rx_rate:.2f} Mbps | Up {tx_rate:.2f} Mbps"))
    lines.append(("header", sep))

    # Disk Usage (from /etc/fstab)
    disk_lines = get_fstab_disk_usage()
    lines.append(("title", "💾 Storage Usage (/etc/fstab):"))
    for d in disk_lines:
        lines.append(("default", d))
    lines.append(("header", sep))

    # Storage Info
    nvme_info, usb_info = get_storage_info()
    lines.append(("title", "💿 NVMe & USB Storage Info:"))
    if nvme_info:
        lines.append(("good", "NVMe Devices:"))
        for info in nvme_info:
            lines.append(("default", info))
    else:
        lines.append(("bad", "No NVMe devices detected."))
    if usb_info:
        lines.append(("good", "USB Storage Devices:"))
        for info in usb_info:
            lines.append(("default", info))
    else:
        lines.append(("bad", "No USB storage devices detected."))
    lines.append(("header", sep))

    # Footer
    lines.append(("footer", "Press 'q' to exit. Use arrows or mouse to scroll."))
    return lines

palette = [
    ('header', 'dark blue,bold', ''),
    ('title', 'yellow,bold', ''),
    ('default', 'default,bold', ''),
    ('good', 'dark green,bold', ''),
    ('bad', 'dark red,bold', ''),
    ('temp_red', 'light red,bold', ''),
    ('temp_yellow', 'yellow,bold', ''),
    ('temp_green', 'light green,bold', ''),
    ('freq', 'light green,bold', ''),
    ('footer', 'dark gray,bold', '')
]

class DashboardWidget(urwid.ListBox):
    def __init__(self):
        self.walker = urwid.SimpleListWalker([])
        super().__init__(self.walker)
        self.update_content()

    def update_content(self):
        # Save current focus position (scroll offset)
        focus_widget, focus_pos = self.get_focus()
        if focus_pos is None:
            focus_pos = 0
        new_items = []
        for item in build_dashboard():
            if isinstance(item, list):
                new_items.append(urwid.Text(item))
            else:
                new_items.append(urwid.Text(item))
        self.walker[:] = new_items
        # Restore focus if possible
        if focus_pos < len(new_items):
            self.set_focus(focus_pos)

def periodic_update(loop, widget):
    widget.update_content()
    loop.set_alarm_in(0.5, periodic_update, widget)

def unhandled_input(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def main():
    dashboard = DashboardWidget()
    loop = urwid.MainLoop(dashboard, palette, handle_mouse=True, unhandled_input=unhandled_input)
    loop.set_alarm_in(0.5, periodic_update, dashboard)
    loop.run()

if __name__ == '__main__':
    main()
