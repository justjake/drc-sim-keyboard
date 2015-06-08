# DRC Simulator

I forked this from https://bitbucket.org/memahaxx/drc-sim, all credit to the
original authors.

So far I've added nothing but this README.

## Goals

keyboard and mouse control for Wii U. Support mouse for "touch" input on the
gamepad screen as well while in CAPSLOCK or something.

## Expected Prodedure:

1. get an rt2800usb with 5ghz support.
1. follow steps described in [this blog post][1] to pair your box with a Wii U.
  - ignore any usage of mac80211; we don't need the patch for drc-sim
  - just follow instructions for pairing, no need for netboot or dhcp server.
  - run `dhclient` on the wifi interface connected to the Wii U to get an IP.
  - basically just run the wpa_supplicant stuff
1. install requirements for drc-sim.py
  - make sure you have libavcodec-dev
1. run drc-sim.py and enjoy flailing around trying to get the Wii U to do something.

## Inspiration

My research starting point was [this Reddit post][2]

[1]: https://rememberdontsearch.wordpress.com/2014/01/05/libdrc-wiiu-linux-setup-with-rt2800usb/
[2]: http://www.reddit.com/r/wiiu/comments/368g2b/my_idea_on_using_libdrc_to_play_splatoon_using_a/

## Resources

- join #libdrc on freenode
- [libdrc's Network services documentation](http://libdrc.org/docs/re/services.html)
