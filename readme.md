#OpenLFConnect

* [Requirements](#requirements)
* [Install](#Install)
 * [Windows](#windows)
 * [Linux](#linux)
* [Getting Started](#getting-started)
 * [Didj](#didj)
 * [Explorer_v1 -> LeapPad2](#the-rest)
 * [Useful Commands](#useful-commands)
* [Command Reference](doc/command_reference.md)

Is a Python 2.6/2.7 based Open Source version of LeapFrog Connect. It allows file navigation on the device, uploading and downloading files, along with updating firmware. Plus a variety of other handy development tools.

**Warning**
Updating your firmware or in anyway messing with your device's Operating System files can cause a broken device, enter at your own risk.

**Support**, this has been tested on an Explorer and LeapPad1, with parts of the code tested on a LeapPad2. From my understanding, this should work fine on the newer devices, as the process is the same. Be warned though, accidents happen.

**Naming**, Explorer is used universally to describe the first hand held device after the Didj, and LeapPad1, for the first tablet based device. LeapPad2 references the second generation tablet and GS to the second gen handheld. Currently Ultra is not supported at all. "The Rest" in this document will here on be in regards to what ever devices that haven't been specifically detailled in that particular section. Specific to Explorer and LeapPad1 is v1 or v2, Around November of 2012 LeapFrog issued an updated firmware that drastically changed how the devices interacted with the host computer. v1, prior to this update, used USB Networking, v2 uses a USB Mass Storage interface. Although Surgeon, which is a recovery image for everything but Didj, seems to remain Networking based.

# Requirements
Windows or Linux compatible

Python 2.6 - No special modules needed for Linux.

Windows requires pyreadline be installed.

[http://sg.danny.cz/sg/sg3_utils.html sg3_utils]
Included for Windows, common on many Linux distros

**Linux**
Check your distro, these are probably standard includes.

Sync, for flushing disk cache

mtd_utils, For mounting/creating JFFS2 and UBI images.
 For LeapPad2 and GS, a patch is required for the larger NAND units.

**Windows**

LeapFrog Ethernet Driver
* If LFConnect is installed, or previously was, this is already installed.
* If not, when it prompts you for a driver, use the Windows update service.

[http://support.apple.com/kb/DL999 Bonjour] For auto device IP discovery
* If LFConnect is installed, or previously was, this is already installed.

For mounting and creating images, you might try cygwin with mtd_utils or what
ever is available for deaing with ubi/jffs2 files. Otherwise these commands
are not supported on Windows.

#Install

Extract archive or clone git repo to a location of your choice.
[github](https://github.com/jrspruitt/OpenLFConnect/wiki)

##Windows:

You many want to look into: [Disabling LFConnect Autostart](http://elinux.org/LeapFrog_Pollux_Platform:_LFConnect#Disable_Auto_Start)

### Didj
You'll need to assign the Didj's USB drive a letter as LFConnect will have assigned it a directory mount point instead. The letter you pick doesn't matter, as long as it doesn't conflict with something else. Plug your Didj in and then go to Disk Management, depending on what version of Windows it should be something like:

     Administrative Tools > Computer Management > Disk Management
Right click the drive, and select Change Drive Letters and Paths click Add and assign the letter.
It is also recommended to disable any disk caching in the drive's properties on Windows. The Didj drive can become easily corrupted, if you are not careful with it. Disabling disk cache, while it takes longer to transfer files initially, is the safest route.

### Explorer and LeapPad with v1 Firmware (Networking)
For LeapPad1 and Explorer with version 1 firmware, which uses USB networking to interact with the host computer.

Windows will default to a zeroconfig address, if you like you can just let it do that. But it takes a bit over a minute for it to do it. Static IP will greatly speed up the process.
Plug your device in and turn it on. You should see an icon in the Start Bar about trying to connect, if not go to Network Connections, right click and choose status. Then properties, scroll down to TCP/IP click on its properties, and make sure to set a static IP. Unless your device is set to a non standard IP, it will be on the 169.254. subnet. Windows will actually default to an address on this subnet, it takes a little over a minute from first turn on though, static IP is much faster.

    Static IP: 169.254.0.1
    Broadcast Mask: 255.255.0.0

### The Rest
Nothing required beyond installing OpenLFConnect

##Linux

To facilitate not needing to run as root you will need to copy the OpenLFConnect/extras/udev_rules files to /etc/udev/rules.d/ The Mass_Storage rules are for all devices. The rules create a device file /dev/leapfrog that is set to allow regular users permission to use. The Mass_Storage rules also unlock the Didj on plug in, saving you the need to run OpenLFConnect just to mount it.
Make sure the rule is owned by root:root and set to permission 644.

### LeapPad1 and Explorer v1 firmware.
Plug your device in and turn it on, then check

    System > Preferences > Network Connections
If you see Auto Eth1 or something similar open it's properties and go to the IPv4 tab, on the Methods drop down and pick Link Local.

If you like you can install avahi-autoipd and use the Net udev rule to run it, you will need to delete the devices entry from Network Manager, as it will only stay connected for short periods, because Network Manager is attempting to configure it also and times it out.

### The Rest
Add the above mentioned udev rules, nothing else should be required.

#Getting Started

Run ./OpenLFConnect.py from the install directory, the first time it will build a directory tree starting with OpenLFConnect/files. This will be populated with directories corresponding to the different devices, this is merely convenience to give you someplace to store your different firmware and files. It also creates Extras/Profiles/

###Loading  a Profile
The first thing you'll need to do is load a profile. If your Explorer or LeapPad are using the older networking style firmware, you want v1. Run:

    local> device_profile_load Extras/Profiles/<your device>.cfg
To save this as default, so its loaded on start up.

    local> device_profile_default

The local&gt; prefix denotes the location you are currently working in, if you were on the device it would change to remote&gt;

Once connected you can change between remote and local with the commands
    remote> local
    local>

    local> remote
    remote>

Current paths are remembered for local and remote, should you ever need a quick reminder, these commands are also location independant, so they can be run at either prompt.

    local> cwdr
    /remote/path/

    local> cwdl
    /home/user/OpenLFConnect/files/

There is a help system built in its recommended you have a look at it, as there are many commands, at the prompt run:

    local> help
    ... listing of all commands
    local> help <command>;

This will get you familiar with all thats available. They are in sections basically, Didj is for interacting with the Didj, DFTP is for the rest, there are commands for downloading and unpacking firmware, creating extracting the cbf file format a few files use and for Linux users you can even mount the firmware images. Although as of this moment, LeapPad 2 and the GS model required patching mtd utils, as the NAND emulation was not available in Debian 7 at least, for mounting their UBI images. The rest of the commands should be rather familiar to Linux users, the basic command line directory navigation.

####Didj
Plug in your device, and run:

    local> didj_mount

You should see some info about the device print out, and the prompt change to remote&gt;. From here you can do an update if you like, it formats and copies everything you need. For most interactions, the udev rule will be all you need as there is no direct access to the Linux OS on the Didj, only the USB drive it has. OpenLFConnect can handle updates and formats the directories needed for you.


#### The Rest
After giving your device a moment to boot up, run:

    local> dftp_connect

You should see some device/host info print to the screen, and the prompt change to remote&gt;. From here you can navigate your device, upload/download files or start an update.

### Useful Commands
**ls,cd,rm,mkdir**

Same as the normal Linux commands, but no arguments available, also included is, **rmdir** which deletes a directory

**cat** works just like the Linux command, printing the contents of a file to the screen. Warning, certain files like sockets, will hang OpenLFConnect.

    remote> cat /etc/version
    1.4.1234

**download** location independant it can be run from local or remote, and will download from the device to your current local directory. Warning, certain files like sockets, will hang OpenLFConnect.

    local> download /some/remote/file

**upload** also location independant, will upload a file from your harddrive to the path you are currently in on the device:
    remote> cd /LF/Bulk/MyFolder
    remote> local
    local> cd LX/MyImages/
    local> upload myimage.png

This will upload myimage.png into the /LF/Bulk/MyFolder directory.
