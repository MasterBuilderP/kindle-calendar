# kindle-calendar

A small project to turn an old kindle into a live-calendar.
Requires rooted kindle device.
Uses Gnome/Evolution calendar integration to fetch events from all added calendars.

Quickstart: Run `./pc_script.sh` on the PC connected to the kindle.

### Install evolution lib dependencies
```bash
sudo apt install -y python3-gi gir1.2-edataserver-1.2 gir1.2-ecal-2.0
```

### Set up USB network
```bash
sudo ip addr add 192.168.15.201/24 dev usb0
sudo ip link set usb0 up
ssh root@192.168.15.244
```
### Prevent Screensaver
`lipc-set-prop com.lab126.powerd preventScreenSaver 1`
