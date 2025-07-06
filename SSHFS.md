## First: 
copy SSH key following: https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-22-04

## Second:
On remote linus machine, do:
```shell
sudo apt install openssh-server
sudo ufw disable
sudo service ssh start
```
## Third:
Partly follow: https://www.digitalocean.com/community/tutorials/how-to-use-sshfs-to-mount-remote-file-systems-over-ssh

On mac:
In stall macfuse to manage file system:
```shell
brew install --cask macfuse
```
Then install SSHFS:
```shell
brew tap gromgit/fuse
brew install gromgit/fuse/sshfs-mac
```
Then create a dir to save the files:
```shell
sudo mkdir /Volumes/ubuntu_mount
```
Then allow sshfs communication:
```shell
sshfs -o allow_other,default_permissions {machine_name}@{ip}:{home_dir} {save_file_dir}
```

For example: 
```shell
sshfs -o allow_other,default_permissions qwang@192.168.6.129:/home/qwang /Volumes/ubuntu_mount
```
