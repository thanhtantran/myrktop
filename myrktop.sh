#!/bin/bash

# Enable Colors using `tput`
BOLD=$(tput bold)
RESET=$(tput sgr0)
GREEN=$(tput setaf 2)  # Force all load values to green
BLUE=$(tput setaf 4)
CYAN=$(tput setaf 6)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)

# Wider Separator Line
LINE="───────────────────────────────────────────────────────────"

echo -e "${BLUE}$LINE${RESET}"
echo -e " 🔥 ${YELLOW}Orange Pi 5 - System Monitor${RESET}"
echo -e "${BLUE}$LINE${RESET}"



# 🌍 Device Info
device_info=$(cat /sys/firmware/devicetree/base/compatible 2>/dev/null | tr -d '\0' || echo "N/A")
npu_version=$(cat /sys/kernel/debug/rknpu/version 2>/dev/null || echo "N/A")
system_uptime=$(uptime -p)  # Get system uptime
docker_status=$(systemctl is-active docker)  # Get Docker status

printf " ${CYAN}Device:${RESET} ${BOLD}%s${RESET}\n" "$device_info"
printf " ${CYAN}Version:${RESET} ${BOLD}%s${RESET}\n" "$npu_version"
printf " ${CYAN}System Uptime:${RESET} ${BOLD}%s${RESET}\n" "$system_uptime"

# 🐳 Docker Service Status
if [ "$docker_status" == "active" ]; then
    printf " ${CYAN}Docker Status:${RESET} ${GREEN}${BOLD}Running ✅${RESET}\n"
else
    printf " ${CYAN}Docker Status:${RESET} ${RED}${BOLD}Not Running ❌${RESET}\n"
fi

echo -e "${BLUE}$LINE${RESET}"


# 📊 CPU Usage & Frequency
echo -e " ${YELLOW}📊 CPU Usage & Frequency${RESET}"

declare -A prev_total prev_idle cpu_loads
core_count=$(nproc)

# Capture initial CPU stats for **each core individually**
for ((i=0; i<core_count; i++)); do
    cpu_line=$(grep "cpu$i " /proc/stat)
    read -r _ user nice system idle iowait irq softirq steal guest guest_nice <<< "$cpu_line"
    prev_total[$i]=$((user + nice + system + idle + iowait + irq + softirq + steal))
    prev_idle[$i]=$idle
done

sleep 1

# Capture new stats for each core
for ((i=0; i<core_count; i++)); do
    cpu_line=$(grep "cpu$i " /proc/stat)
    read -r _ user nice system idle iowait irq softirq steal guest guest_nice <<< "$cpu_line"
    total=$((user + nice + system + idle + iowait + irq + softirq + steal))
    diff_total=$((total - prev_total[$i]))
    diff_idle=$((idle - prev_idle[$i]))
    
    if [ $diff_total -ne 0 ]; then
        cpu_loads[$i]=$((100 * (diff_total - diff_idle) / diff_total))
    else
        cpu_loads[$i]=0
    fi

    prev_total[$i]=$total
    prev_idle[$i]=$idle
done

# Display per-core CPU load & frequency (NO SHARED VALUES)
for ((i=0; i<core_count/2; i++)); do
    freq1=$(cat /sys/devices/system/cpu/cpu$i/cpufreq/scaling_cur_freq 2>/dev/null || echo 0)
    freq2=$(cat /sys/devices/system/cpu/cpu$((i+4))/cpufreq/scaling_cur_freq 2>/dev/null || echo 0)
    printf " Core %d: ${GREEN}${BOLD}%3d%%%s  %4d MHz   Core %d: ${GREEN}${BOLD}%3d%%%s  %4d MHz\n" \
        "$i" "${cpu_loads[$i]}" "$RESET" "$((freq1 / 1000))" \
        "$((i+4))" "${cpu_loads[$((i+4))]}" "$RESET" "$((freq2 / 1000))"
done

echo -e "${BLUE}$LINE${RESET}"

# 🎮 GPU Load & Frequency (Always Green)
gpu_load=$(awk -F'[@ ]' '{print $1}' /sys/class/devfreq/fb000000.gpu/load 2>/dev/null || echo "N/A")
gpu_freq=$(cat /sys/class/devfreq/fb000000.gpu/cur_freq 2>/dev/null || echo "N/A")
printf " ${YELLOW}🎮 GPU Load:${RESET} ${GREEN}${BOLD}%3d%%%s  %4d MHz${RESET}\n" "$gpu_load" "$RESET" "$((gpu_freq / 1000000))"
echo -e "${BLUE}$LINE${RESET}"

# 🧠 NPU Load & Frequency (Always Green)
npu_load=$(cat /sys/kernel/debug/rknpu/load 2>/dev/null | grep -oP '\d+%' | tr '\n' ' ' || echo "0% 0% 0%")
npu_freq=$(cat /sys/class/devfreq/fdab0000.npu/cur_freq 2>/dev/null || echo "N/A")
printf " ${YELLOW}🧠 NPU Load:${RESET} ${GREEN}${BOLD}%-10s${RESET}  %4d MHz${RESET}\n" "$npu_load" "$((npu_freq / 1000000))"
echo -e "${BLUE}$LINE${RESET}"


# 🖼️ RGA Load (Always Green for Stability)
rga_load=$(cat /sys/kernel/debug/rkrga/load 2>/dev/null || echo "N/A")
rga_values=$(echo "$rga_load" | grep -oP 'load = \K[0-9]+%' | head -n 3 | tr '\n' ' ')
# Ensure output is never empty
rga_values=${rga_values:-"0% 0% 0%"}

printf " ${YELLOW}🖼️  RGA Load:${RESET} ${GREEN}${BOLD}%-12s${RESET}\n" "$rga_values"
echo -e "${BLUE}$LINE${RESET}"

# 🖥️ RAM & Swap Usage
echo -e " ${YELLOW}🖥️  RAM & Swap Usage:${RESET}"
ram_usage=$(free -h | awk '/Mem:/ {print $3}')
ram_total=$(free -h | awk '/Mem:/ {print $2}')
swap_usage=$(free -h | awk '/Swap:/ {print $3}')
swap_total=$(free -h | awk '/Swap:/ {print $2}')

printf " RAM Used:  ${BOLD}${GREEN}%-6s${RESET} / ${BOLD}%s${RESET}\n" "$ram_usage" "$ram_total"
printf " Swap Used: ${BOLD}${GREEN}%-6s${RESET} / ${BOLD}%s${RESET}\n" "$swap_usage" "$swap_total"


echo -e "${BLUE}$LINE${RESET}"

# 🌡️ Temperatures (Fixed)
echo -e " ${YELLOW}🌡️ Temperatures${RESET}"
sensors | awk '
/thermal|nvme|gpu/ {name=$1}
/temp1|Composite/ {
    temp = substr($2, 2, length($2)-5) + 0;
    color = (temp >= 70) ? "'${RED}'" : (temp >= 60) ? "'${YELLOW}'" : "'${GREEN}'";
    printf " %-30s %s%s°C%s\n", name, color, temp, "'${RESET}'";
}'
echo -e "${BLUE}$LINE${RESET}"

# 📊 Disk Usage
echo -e " ${YELLOW}📊 Disk Usage${RESET}"
echo -e " ${CYAN}Mount Point         Total   Used    Free${RESET}"
df -h | awk '$6=="/" || $6=="/media/wdmount" || $6=="/media/ssdmount" {printf " %-18s %-7s %-7s %-7s\n", $6, $2, $3, $4}'
echo -e "${BLUE}$LINE${RESET}"


# 🔌 Network Traffic (eth0) - Now Stable
RX1=$(cat /proc/net/dev | awk '/eth0:/ {print $2}')
TX1=$(cat /proc/net/dev | awk '/eth0:/ {print $10}')
sleep 1
RX2=$(cat /proc/net/dev | awk '/eth0:/ {print $2}')
TX2=$(cat /proc/net/dev | awk '/eth0:/ {print $10}')
RX_RATE=$(echo "scale=2; ($RX2 - $RX1) / 125000" | bc)
TX_RATE=$(echo "scale=2; ($TX2 - $TX1) / 125000" | bc)

printf " ${YELLOW}🔌 Network Traffic (eth0)${RESET}\n"
printf " ${CYAN}Download:${RESET} ${GREEN}${BOLD}%-5s Mbps${RESET} | ${CYAN}Upload:${RESET} ${GREEN}${BOLD}%-5s Mbps${RESET}\n" "$RX_RATE" "$TX_RATE"
echo -e "${BLUE}$LINE${RESET}"

#🔌 2. Connected USB Devices (Only Active Devices)
#echo -e " ${YELLOW}🔌 Connected USB Devices${RESET}"
#lsusb | awk -F 'ID ' '{if ($2 !~ /Linux Foundation/) print "• "$2}'
#echo -e "${BLUE}$LINE${RESET}"



echo -e " ${YELLOW}💾 NVMe & USB Storage Info${RESET}"

# Get a list of NVMe devices
nvme_devices=$(lsblk -dno NAME,TYPE | awk '$2=="disk" && $1 ~ /^nvme/ {print $1}')

# Display NVMe Information
if [[ -n "$nvme_devices" ]]; then
    echo -e " ${CYAN}📦 NVMe Devices Found:${RESET}"
    for nvme in $nvme_devices; do
        model=$(nvme id-ctrl /dev/$nvme | grep "Model Number" | awk -F ":" '{print $2}' | xargs)
        health=$(nvme smart-log /dev/$nvme | grep "percentage_used" | awk '{print $3}' | tr -d '%')  # Remove %
        temp=$(nvme smart-log /dev/$nvme | grep "temperature" | awk '{print $3}')
        power_hours=$(nvme smart-log /dev/$nvme | grep "power_on_hours" | awk '{print $3}')
        trim_support=$(nvme id-ctrl /dev/$nvme | grep "Volatile Write Cache" | awk -F ":" '{print $2}' | xargs)

        # Handle missing values
        health=${health:-0}  # Default to 0 if empty
        temp=${temp:-"N/A"}
        power_hours=${power_hours:-"N/A"}
        trim_support=${trim_support:-"Unknown"}

        # Determine Health Status
        if [[ "$health" -ge 80 ]]; then
            health_status="${RED}BAD${RESET}"
        elif [[ "$health" -ge 50 ]]; then
            health_status="${YELLOW}WARNING${RESET}"
        else
            health_status="${GREEN}GOOD${RESET}"
        fi

        printf " ${BOLD}Device: ${RESET}/dev/$nvme - ${GREEN}%s${RESET}\n" "${model:-Unknown}"
        printf "  ├── Health Used: ${BOLD}%s%%%s (%s)\n" "$health" "$RESET" "$health_status"
        printf "  ├── Temperature: ${BOLD}%s°C${RESET}\n" "$temp"
        printf "  ├── Power-On Hours: ${BOLD}%s hrs${RESET}\n" "$power_hours"
        printf "  ├── TRIM Support: ${BOLD}%s${RESET}\n" "$trim_support"
    done
else
    echo -e " ${RED}No NVMe devices detected.${RESET}"
fi

# Get a list of USB storage devices
usb_devices=$(lsblk -dno NAME,TRAN | awk '$2=="usb" {print $1}')

# Display USB Storage Information
if [[ -n "$usb_devices" ]]; then
    echo -e " ${CYAN}🔌 USB Storage Devices Found:${RESET}"
    for usb in $usb_devices; do
        model=$(lsblk -dno MODEL /dev/$usb | xargs)
        health=$(smartctl -H /dev/$usb | grep "SMART overall-health self-assessment test result" | awk -F ":" '{print $2}' | xargs)
        temp=$(smartctl -A /dev/$usb | grep "Temperature_Celsius" | awk '{print $10}')
        power_hours=$(smartctl -A /dev/$usb | grep "Power_On_Hours" | awk '{print $10}')
        trim_support=$(lsblk -D /dev/$usb | awk 'NR==2 {print ($2=="1"?"Yes":"No")}')

        # Handle missing values
        health=${health:-"Unknown"}
        temp=${temp:-"N/A"}
        power_hours=${power_hours:-"N/A"}
        trim_support=${trim_support:-"Unknown"}

        # Determine Health Status
        if [[ "$health" == "PASSED" ]]; then
            health_status="${GREEN}GOOD${RESET}"
        elif [[ "$health" == "FAILED" ]]; then
            health_status="${RED}BAD${RESET}"
        else
            health_status="${YELLOW}UNKNOWN${RESET}"
        fi

        printf " ${BOLD}Device: ${RESET}/dev/$usb - ${GREEN}%s${RESET}\n" "${model:-Unknown}"
        printf "  ├── SMART Health: ${BOLD}%s${RESET} (%s)\n" "$health" "$health_status"
        printf "  ├── Temperature: ${BOLD}%s°C${RESET}\n" "$temp"
        printf "  ├── Power-On Hours: ${BOLD}%s hrs${RESET}\n" "$power_hours"
        printf "  ├── TRIM Support: ${BOLD}%s${RESET}\n" "$trim_support"
    done
else
    echo -e " ${RED}No USB storage devices detected.${RESET}"
fi

echo -e "${BLUE}$LINE${RESET}"
