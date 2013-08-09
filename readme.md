OpenLFConnect
=
[Command Reference](doc/command_reference.md)

Is a Python 2 based Open Source version of LeapFrog Connect. It allows file navigation on the device, uploading and downloading files, along with updating firmware. Plus a variety of other handy development tools.

Install
=
Extract archive or clone git repo to a location of your choice.
[github](https://github.com/jrspruitt/OpenLFConnect/wiki)

Windows:
--------------
### Didj
You'll need to assign the Didj's USB drive a letter as LFConnect will have assigned it a directory mount point instead. The letter you pick doesn't matter, as long as it doesn't conflict with something else. Plug your Didj in and then go to Disk Management, depending on what version of Windows it should be something like:

     Administrative Tools > Computer Management > Disk Management
Right click the drive, and select Change Drive Letters and Paths click Add and assign the letter.
It is also recommended to disable any disk caching in the drive's properties on Windows. The Didj drive can become easily corrupted, if you are not careful with it. Disabling disk cache, while it takes longer to transfer files initially, is the safest route.

### Explorer and LeapPad v1 Firmware
For LeapPad Explorer 1 and Leapster Explorer with version 1 firmware, which uses USB networking to interact with the host computer.

Windows will default to a zeroconfig address, if you like you can just let it do that. But it takes a bit over a minute for it to do it. Static IP will greatly speed up the process.
Plug your device in and turn it on. You should see an icon in the Start Bar about trying to connect, if not go to Network Connections, right click and choose status. Then properties, scroll down to TCP/IP click on its properties, and make sure to set a static IP. Unless your device is set to a non standard IP, it will be on the 169.254. subnet. Windows will actually default to an address on this subnet, it takes a little over a minute from first turn on though, static IP is much faster.

    Static IP: 169.254.0.1
    Broadcast Mask: 255.255.0.0

### Explorer and LeapPad1 v2 Firmware and LeapPad 2 and Explorer GS
Nothing required beyond installing OpenLFConnect

Linux
--------

To facilitate not needing to run as root you will need to copy the OpenLFConnect/extras/udev_rules files to /etc/udev/rules.d/ The Mass_Storage rules are for all devices.LeapPad1 and Explorer firmware v1 require the Net rules. The rules create a device file /dev/leapfrog that is set to allow regular users permission to use. The Mass_Storage rules also unlock the Didj on plug in, saving you the need to run OpenLFConnect just to mount it.
Make sure the rule is owned by root:root and set to permission 644.

### LeapPad1 and Explorer v1 firmware.
Plug your device in and turn it on, then check

    System > Preferences > Network Connections
If you see Auto Eth1 or something similar open it's properties and go to the IPv4 tab, on the Methods drop down and pick Link Local.

If you like you can install avahi-autoipd and use the Net udev rule to run it, you will need to delete the devices entry from Network Manager, as it will only stay connected for short periods, because Network Manager is attempting to configure it also and times out.

### Explorer and LeapPad1 v2 Firmware and LeapPad 2 and Explorer GS
Add the above mentioned udev rules, nothing else should be required.

Getting Started
===========
####!!Warning
Some of these operations are possibly destructive, especially updating the firmware, or changing critical files for your device's operating system. You've been warned, proceed with caution. Browse [elinux](http://elinux.org/LeapFrog_Pollux_Platform) for more information on what you want to do before jumping into it.
####/Warning!!

Run ./OpenLFConnect.py from the install directory, the first time it will build a directory tree starting with &lt;source&gt;/files. This will be populated with directories corresponding to the different devices, this is merely convenience to give you someplace to store your different firmware and files. It also creates Extras/Profiles/

###Loading  a Profile
The first thing you'll need to do is load a profile. Run:

     local> device_profile_load Extras/Profiles/<your device>.cfg
To save this as default, so its loaded on start up.

      local> device_profile_default

The local&gt; prefix denotes the location you are currently working in, if you were on the device it would change to remote&gt;

There is a help system built in its recommended you have a look at it, as there are many commands, at the prompt run:

      local> help
      ... listing of all commands
      local> help <command>;

This will get you familiar with all thats available. They are in sections basically, Didj is for interacting with the Didj, DFTP is for the rest, there are commands for downloading and unpacking firmware, creating extracting the cbf file format a few files use and for Linux users you can even mount the firmware images. Although as of this moment, LeapPad 2 and the GS model required patching mtd utils, as the NAND emulation was not available in Debian 7 at least, for mounting their UBI images. The rest of the commands should be rather familiar to Linux users, the basic command line directory navigation.

####Didj
Plug in your device, and run:

     local> didj_mount

You should see some info about the device print out, and the prompt change to remote&gt;. From here you can do an update if you like, it formats and copies everything you need. For looking through the files and transfering/editing, its easier just to use normal OS directory navigation.


#### The Rest
After giving your device a moment to boot up, run:

     local> dftp_connect

You should see some device/host info print to the screen, and the prompt change to remote&gt;. From here you can navigate your device, upload/download files or start an update.
