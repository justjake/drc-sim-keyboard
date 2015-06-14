#!/usr/bin/env bash
# run this in a Tmux split and then start fetch-key-b.sh in another split.
set -e
WLAN=wlan0

echo "
WPA CLI. type 'scan' then once you see CTRL-EVENT-SCAN-RESULTS, type 'scan results'.

Depending on the WiFi situation around you, you will see quite some access
points. Look for one with an ESSID like this: WiiUAABBCCDDEEFF_STA1 Note down
the BSSID. Now calculate the pin, from the four symbols you noted down before,
each symbol is associated with a number:
♠ = 0
♥ = 1
♦ = 2
♣ = 3

So ♥♣♠♠ represents 1300. The pin also has a static part, namely 5678 which is
appended to the symbols, so for the previous example the pin would be 13005678.
With the BSSID and the pin we can now try to obtain the WPS credentials. In the
wps cli type:
  
wps_pin BSSID PIN

This indicates that we received the credentials:
  
WPS-CRED-RECEIVED
WPS-SUCCESS

Possibly, Exit the wpa cli (b) and wpa supplicant (a)."
exec rlwrap sudo ./wpa_cli -p /var/run/wpa_supplicant_drc
