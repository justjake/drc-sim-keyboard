#!/usr/bin/env bash
# run this in a Tmux split in your wpa_supplicant directory and then start fetch-key-b.sh in another split.
set -e
WLAN=wlan0
# set this to the MAC address of your gampepad
echo "drc-sim-keyboard wpa_supplicant & friends"
DRC_MAC_ADDR=""
LOGFILE="supplicant-log-$(date --iso-8601=seconds).txt"
if [ -n "$DRC_MAC_ADDR" ] ; then
  echo "  bringing $WLAN down for a moment"
  sudo ip link set dev $WLAN down 
  echo "  setting $WLAN address to $DRC_MAC_ADDR"
  sudo ip link set dev $WLAN address "$DRC_MAC_ADDR"
fi
echo "  enabling $WLAN"
sudo ip link set dev $WLAN up 
echo "  here's a list of all the networks"
sudo iwlist $WLAN scan
echo "  logging ./wpa_supplicant to $LOGFILE"
exec sudo ./wpa_supplicant -Dnl80211 -i $WLAN -c connect-to-wiiu.conf -dd \
  | tee "$LOGFILE"
