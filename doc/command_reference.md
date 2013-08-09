## Command List
This list is currently inbetween updates, check with the OpenLFConnect help for latest.

* [General](#general)
* [Filesystem](#filesystem)
* [Didj](#didj)
* [DFTP](#dftp)
* [USB](#usb-boot)
* [Surgeon](#surgeon)
* [Firmware](#firmware)
 * [LF Packages](#lf2lfp-packages)
 * [CBF](#cbf)
 * [Images](#ubijffs2-images)

 
### General
**debug**


    Usage:
        debug <on|off>
    
    Turning debug on, turns most any filesystem action off, such as, up/download, rm,
    mkdir, etc. It is replaced with text displaying what would have happened. Useful for
    checking updates before they happen, also will not eject Didj on update.


**get_device_id**

    Usage:
        get_dev_id
    
    Returns the currently configured device id.


**set_device_id**

    Usage:
        set_dev_id <device id>
    
    Set the device to use when creating a new mount client.
    The device id, in Linux is the generic scsi device file, ex. /dev/sg2 or harddrive 
    /dev/sdb , or Windows the PhysicalDrive ex. PD1.
    To reset to auto determine leave input blank.


**get_mount_point**

    Usage:
        get_mount_point
    
    Returns the currently configured mount point to use when creating a new mount client.


**set_mount_point**

    Usage:
        set_mount_point <mount point>
    
    Set the mount point to use when creating a new mount client. 
    The mount point, ex. Linux /media/didj, or Windows D:\
    To reset to auto determine leave input blank.


**get_device_ip**

    Usage:
        get_device_ip
    
    Returns currently configured device IP to use when creating a new network client.


**set_device_ip**

    Usage:
        set_device_ip <IP>
    
    Set the device IP address to use when creating a new network client.
    ex. 169.254.123.123
    To reset to auto determine leave input blank.


**get_host_ip**

    Usage:
        get_host_ip
    
    Returns currently configured host IP to use when creating a new network client.


**set_host_ip**

    Usage:
        set_host_ip <IP>
    
    Set the host IP address to use when creating a new network client.
    ex. 169.254.123.123
    To reset to auto determine leave input blank.


**remote**

    Usage:
        remote
    
    Set to remote device for filesystem navigation.


**local**

    Usage:
        local
    
    Set to prompt to local host for filesystem navigation.


### FileSystem
**cwdr**

    Usage:
        cwdr
    
    Print current remote directory path.


**cwdl**

    Usage:
        cwdl
    
    Print current local directory path.


**exit**

    Usage:
        exit
    
    Exit OpenLFConnect

**ls**

    Usage:
        ls [path]
    
    List directory contents. Where depends on which is set, remote or local


**cd**

    Usage:
        cd <path>
    
    Change directories. Where depends on which is set, remote or local


**mkdir**

    Usage:
        mkdir <path>
    
    Create directory. Where depends on which is set, remote or local

     
**rmdir**

    Usage:
        rmd <path>
    
    Delete directory. Where depends on which is set, remote or local


**rm**

    Usage:
        rm <file>
    
    Delete file. Where depends on which is set, remote or local


**upload**

    Usage:
        upload <local path>
    
    Upload the specified local path to the current remote directory, Will overwrite with out prompt.


**download**

    Usage:
        download <remote path>
    
    Download the specified remote path to the current local directory, will over write with out prompt.


**cat**

    Usage:
        cat <path>
    
    Prints the contents of a file to the screen.
    Doesn't care what kind or how big of a file.



### Didj

**didj_mount**

    Usage:
        didj_mount [mount name]
    
    Unlock Didj to allow it to mount on host system.


**didj_eject**

    Usage:
        didj_eject
    
    Eject the Didj which will unmount on host system, if the firmware updates are 
    on the Didj, an update will be triggered. If they are not, it will ask you to unplug it.
    Could take some time to unmount and eject if you have written files to the device..


**didj_device_info**

    Usage:
        didj_device_info
    
    Returns various information about device and mount.


**didj_update**

    Usage:
        didj_update <path>
    
    CAUTION:
    !!Attempts to flash firmware, could potentially be harmful.!!
    !!Make sure Battery's are Fresh, or A/C adpater is used!!
    
    Update Didj firmware and bootloader.
    lightning-boot.bin, erootfs.jffs2 and kernel.bin are all required for the update to work.
    They can all be in the current directory, or in bootstrap-LF_LF1000 and firmware-LF_LF1000 respectively.
    MD5 files will be created automatically.


**didj_update_firmware**

    Usage:
        didj_update_firmware <path>
    
    CAUTION:
    !!Attempts to flash firmware, could potentially be harmful.!!
    !!Make sure Battery's are Fresh, or A/C adpater is used!!
    
    Update Didj firmware.
    erootfs.jffs2 and kernel.bin are both required for update to take place.
    Files can have alternate names as long as their name is in the new name, ex. custom-kernel.bin, or erootfs-custom.jffs2
    Files must be in the current directory or in firmware-LF_LF1000 directory.
    MD5 files will be created automatically.


**didj_update_bootloader**

    Usage:
        didj_update_bootloader <path>
    
    CAUTION:
    !!Attempts to flash firmware, could potentially be harmful.!!
    !!Make sure Battery's are Fresh, or A/C adpater is used!!
    
    Update Didj bootloader.
    File must be in current directory, bootloader-LF_LF1000 directory or direct path to.
    File can have alternate name, but must include lightning-boot in it, ex custom-lightning-boot.bin
    MD5 files will be created automatically.


**didj_update_cleanup**

    Usage:
        didj_update_cleaup
    
    Remove Didj firmware and bootloader from device.


**didj_update_eb**

    Usage:
        didj_update_eb <path to emerald-boot>
    CAUTION:
    !!Attempts to flash firmware, could potentially be harmful.!!
    !!Make sure Battery's are Fresh, or A/C adapter is used!!
    !!Requires NAND enabled Emerald Boot!!
    Flash Emerald Boot to Didj NAND.
    After running Didj will shutdown, unplug USB and turn on device. It should then turn itself off.
    You should now be able to USB Boot like the Explorer and update using DFTP.



### DFTP
Used for LeapPads and Explorers.

**dftp_connect**

    Usage:
        dftp_connect
    
    Connect to device for dftp session.
    Will attempt to configure IPs as needed.
    This could take a minute or so, if you just booted the device.


**dftp_disconnect**

    Usage:
        dftp_disconnect
    
    Disconnect DFTP client.
    This will cause the DFTP server to start announcing its IP again, except Explorer's surgeon.cbf version, which will reboot the device.


**dftp_server_version**

    Usage
        dftp_server_version [number]
    
    Sets the version number of the dftp server. Or retrieves if none specified.
    OpenLFConnect checks for version 1.12 for surgeon running before a firmware update.
    Set this to 1.12 if getting complaints, or surgeon has its dftp version updated.


**dftp_device_info**

    Usage:
        dftp_device_info
    
    Returns various information about the device, and connection.
    Note: Device name is guessed from board id.


**dftp_update**

    Usage:
        update <local path>
    
    CAUTION:
    !!Attempts to flash firmware, could potentially be harmful.!!
    !!Make sure Battery's are Fresh, or A/C adpater is used!!
    
    Uploads and flashes the files found in path, or the file specified by path.
    
    Caution: Has not been tested on LeapPad, theoretically it should work though, please confirm to author yes or no if you get the chance.


**dftp_update_partitions**

    Usage:
        dftp_update_partitions <partitions_file>
    
    Sets the partition configuration file located in files/Extras/Partitions/ for use with DFTP Update.
    Set to custom config file when your device uses DFTP but with modified partition sizes/addresses.
    Default is LeapFrog.cfg
    
    Caution: This does not repartition your device. The table is hard coded in the kernel/bootloader.


**dftp_reboot**

    Usage:
         update_reboot
    
    This will trigger a reboot.


**dftp_reboot_usbmode**

    Usage:
        dftp_reboot_usbmode
    
    This will reboot the device into USB mode, for sending a surgeon.cbf to boot.
    If surgeon is booted, will do a standared reboot.


**dftp_mount_patient**

    Usage:
        dftp_mount_patient 0|1|2
    
    Surgeon booted device only. These give you access to the devices filesystem.
    0 Unmounts /patient-rfs and /patient-bulk/
    1 Mounts /patient-rfs and /patient-bulk/
    2 Mounts only /patient-rfs


**dftp_telnet**

    Usage:
        dftp_telnet <start|stop>
    
    Starts or stops the Telnet daemon on the device.
    Username:root
    Password:<blank>


**dftp_ftp**

    Usage:
        dftp_ftp <start|stop>
    
    Starts or stops the FTP server on the device.
    Username:root
    Password:<blank>


**dftp_sshd**

    Usage:
        dftp_sshd <start|stop>
    
    Starts or stops the SSHD daemon on the device. Does not work on surgeon.
    Username:root
    Password:<blank>


**dftp_sshd_no_password**

    Usage:
        dftp_sshd_no_password
    
    Patches the sshd_config file to permit login with a blank password.
    Should be run before starting sshd, only needs to be done once.


**dftp_run_script**

    Usage:
        dftp_run_script <path>
    
    This takes a shell script as an argument, and proceeds to run it on the device.


**send**

    Usage:
        send <raw command>
    Advanced use only, don't know, probably shouldn't.

 
### USB Boot
**surgeon_boot**

    Usage:
        surgeon_boot <path to surgeon.cbf>
    
    Uploads a Surgeon.cbf file to a device in USB Boot mode. 
    File can be any name, but must conform to CBF standards.


### Surgeon
**surgeon_extract_rootfs**


    Usage:
    
        surgeon_extract_rootfs <rootfs suffix> <path to surgeon.cbf or zImage>
    Extracts the Root file system (initramfs) to <current directory>/rootfs.<suffix>


 
### Firmware

#### LF2/LFP Packages

**package_extract**

    Usage:
        package_extract [path]
    
    Extracts LF Package files (lfp ,lfp2)
    Takes a file path, or will extract all packages in a directory.
    Will overwrite without warning.


**package_download**

    Usage:
        package_download <firmware|surgeon|bootloader|bulk>
    
    Downloads specified files of currently loaded device.
    bootloader is Didj specific.

    surgeon and bulk are not available for Didj.

 
#### CBF Files

**cbf_unwrap**

    Usage:
        cbf_unwrap <file path>
    
    Removes the CBF wrapper and prints a summary.
    CBF is used on kernels and surgeon, to wrap a zImage or Image file.
    Saves the image file to the same directory the cbf file was in.
    If image file already exists will fail.


**cbf_wrap**

    Usage:
        cbf_wrap <low|high> <output file name> <input file path>
    
    Creates the CBF wrapped file <output file name> of the <input file path> and prints a summary.
    File is saved to current directory.
    Kernel should be a zImage or Image file.
    Low is standard setting for everything but LeapPad Kernel which is High


**cbf_summary**

    Usage:
        cbf_summary <file path>
    
    Display the CBF wrapper summary.
    CBF is used on kernels and surgeon, to wrap a zImage or Image file.

 
#### UBI/JFFS2 Images

**ubi_mount**

    Usage:
        ubi_mount <file.ubi>
    
    Mounts an Explorer erootfs.ubi image to /mnt/ubi_leapfrog
    This is a Linux only command.
    Will be prompted for password, sudo required for commands.


**ubi_umount**

    Usage:
        ubi_umount
    
    Unmounts /mnt/ubi_leapfrog
    This is a Linux only command.
    Will be prompted for password, sudo required for commands.


**ubi_create**

    Usage:
        ubi_create <erootfs|bulk> <output file name> <input directory path>
    
    Creates an Explorer UBI image <output file name> of the <input directory path>.
    File is saved to the current directory.
    Caution this image is specifically for the Explorer.
    This is a Linux only command.
    Will be prompted for password, sudo required for commands.


**jffs2_mount**

    Usage:
        jffs2_mount <file_name>.jffs2
    
    Mounts <file_name>.jffs2 image to /mnt/jffs2_leapfrog
    This is a Linux only command.
    Will be prompted for password, sudo required for commands.


**jffs2_umount**

    Usage:
        jffs2_umount
    
    Unmounts /mnt/jffs2_leapfrog
    This is a Linux only command.
    Will be prompted for password, sudo required for commands.


**jffs2_create**

    Usage:
        jffs2_create <output file name> <input directory path>
    
    Creates an <output file name> image of the <input directory path>  
    File is saved in the current directory.
    This is a Linux only command.
    Will be prompted for password, sudo required for commands.

