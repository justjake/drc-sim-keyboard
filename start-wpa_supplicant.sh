#!/usr/bin/env bash
# run this in a Tmux split in your wpa_supplicant directory and then start fetch-key-b.sh in another split.
set -e
WLAN=wlan0
echo "start ./fetch-key-b.sh as well! it contains most of the instructions."
sudo ifconfig $WLAN up
sudo iwlist $WLAN scan
exec sudo ./wpa_supplicant -Dnl80211 -i $WLAN -c connect-to-wiiu.conf -dd | tee "supplicant-log-$(date --iso-8601=seconds).txt"
