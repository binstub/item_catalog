### Installing the Virtual Machine
We are using a virtual machine (VM) to run an SQL database server and a Python script that uses it.The VM is a Linux server system that runs on top of your own computer

#### Install VirtualBox
VirtualBox is the software that actually runs the virtual machine. You can download it from [virtualbox.org]. Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.
Ubuntu users: If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center instead. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.
#### Install Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. Download it from [vagrantup.com]. Install the version for your operating system.
**Windows users**: The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.
This will give you the PostgreSQL database and support software needed for this project. If you have used an older version of this VM, you may need to install it into a new directory.
From your terminal, inside the vagrant subdirectory, Bring VM up and running with  ```vagrant up```. Then log into it with ```vagrant ssh```.

You can sync files with the host system with the ```/vagrant``` directory. If this folder is not visible from within your VM, check if the
-guest installations are up to date
-the file has appropriate permissions
-try mounting the folder explicitly

After you are finished working with the virtual machine, you can simply press ```CTRL+D``` to log out and execute vagrant halt to properly shut down the virtual machine.
