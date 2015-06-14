# DRC Simulator

## Credits

I forked from https://bitbucket.org/memahaxx/drc-sim, which does all the hard
DRC simulator work. all credit to the original authors.

[@delroth_](https://twitter.com/delroth_) was a huge help with connecting to
the Wii U with wpa_supplicant.

## Goals

keyboard and mouse control for Wii U. Support mouse for "touch" input on the
gamepad screen as well while in CAPSLOCK or something.

## Connect to the Wii U

1. get an rt2800usb with 5ghz support.
1. follow some of the steps described in [this blog post][1] to pair your box with a Wii U.
  1. Do the "Preparations" sectio n
  1. Skip the "mac80211 stack" section! That's for libdrc, not drc-sim.
  1. Do everything in the "Obtaining the key" step.
    - the two scripts in this repo can be useful with a bit of customization.

1. Once you have obtained the PSK at the end of "obtaining the key",
   customize the EXAMPLE-connect-to-the-wiiu.conf with your Wii U's information. You need to fill in:
    - your BSSID
    - your PSK
    - your SSID (possibly)
1. launch wpa_supplicant again using your new connect-to-wiiu.conf. After a
   bit you should see wpa_supplicant successfully connect and authenticate.
1. run `sudo dhclient $WLAN` to get an IP address for your connection from
   the Wii U.

When you're finished, you should see something like this: [my hooray
tweet](https://twitter.com/jitl/status/609875855112712193/photo/1)

## Set up drc-sym (untested)

1. Read over install-requirements.sh and decide how you want to install
   everything. install-requirements.sh was written for Debian Jessie, but
   should also work just fine on Ubuntu systems.
1. run `./install-requirements.sh`
1. Plug in a wireless Xbox 360 controller receiver.

## software ideas

I want to have pluggable control schemes for quick reconfiguration.
`Control` implements functions for all the Wii U's inputs. We'll read the nice
public API and from that produce a packed InputData instance in binary.

## Inspiration

My research starting point was [this Reddit post][2]

[1]: https://rememberdontsearch.wordpress.com/2014/01/05/libdrc-wiiu-linux-setup-with-rt2800usb/
[2]: http://www.reddit.com/r/wiiu/comments/368g2b/my_idea_on_using_libdrc_to_play_splatoon_using_a/

## Resources

- join #libdrc on freenode
- [libdrc's Network services documentation](http://libdrc.org/docs/re/services.html)
