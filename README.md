# kindle-calendar

A small project to turn an old kindle into a live-calendar.
Requires rooted kindle device.
Uses Gnome/Evolution calendar integration to fetch events from all added calendars.

Quickstart: Run `./pc_script.sh` on the PC connected to the kindle.

### Set up USB network
```bash
sudo ip addr add 192.168.15.201/24 dev usb0
sudo ip link set usb0 up
ssh root@192.168.15.244
```
### Prevent Screensaver
`lipc-set-prop com.lab126.powerd preventScreenSaver 1`
