#!/bin/bash

sudo apt update && sudo apt install -y python3 python3-pip lm-sensors smartmontools nvme-cli 
sudo sensors-detect --auto
sudo pip3 install urwid
