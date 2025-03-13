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
printf " ${CYAN}Device:${RESET} ${BOLD}%s${RESET}\n" "$device_info"
printf " ${CYAN}Version:${RESET} ${BOLD}%s${RESET}\n" "$npu_version"
echo -e "${BLUE}$LINE${RESET}"

# 📊 CPU Usage & Frequency
echo -e " ${YELLOW}📊 CPU Usage & Frequency${RESET}"

cpu_loads=()
prev_total=()
prev_idle=()

for i in {0..7}; do
    read -r cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
    prev_total[i]=$((user + nice + system + idle + iowait + irq + softirq + steal))
    prev_idle[i]=$idle
done

sleep 1

for i in {0..7}; do
    read -r cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
    total=$((user + nice + system + idle + iowait + irq + softirq + steal))
    diff_total=$((total - prev_total[i]))
    diff_idle=$((idle - prev_idle[i]))
    if [ $diff_total -ne 0 ]; then
        cpu_loads[i]=$((100 * (diff_total - diff_idle) / diff_total))
    else
        cpu_loads[i]=0
    fi
done

total_load=$(awk "BEGIN {sum=0; for(i=0;i<8;i++) sum+=${cpu_loads[i]}; print sum/8}")
printf " ${CYAN}Total CPU Load:${RESET} ${GREEN}${BOLD}%3d%%%s\n" "$total_load" "$RESET"

for i in {0..3}; do
    freq1=$(cat /sys/devices/system/cpu/cpu$i/cpufreq/scaling_cur_freq 2>/dev/null || echo 0)
    freq2=$(cat /sys/devices/system/cpu/cpu$((i+4))/cpufreq/scaling_cur_freq 2>/dev/null || echo 0)
    printf " Core %d: ${GREEN}${BOLD}%3d%%%s  %4d MHz   Core %d: ${GREEN}${BOLD}%3d%%%s  %4d MHz\n" \
        "$i" "${cpu_loads[i]}" "$RESET" "$((freq1 / 1000))" \
        "$((i+4))" "${cpu_loads[i+4]}" "$RESET" "$((freq2 / 1000))"
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

# 🖼️ RGA Load (Always Green)
rga_load=$(cat /sys/kernel/debug/rkrga/load 2>/dev/null | grep -oP '\d+%' | tr '\n' ' ' || echo "0% 0% 0%")
printf " ${YELLOW}🖼️  RGA Load:${RESET} ${GREEN}${BOLD}%-10s${RESET}\n" "$rga_load"
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
