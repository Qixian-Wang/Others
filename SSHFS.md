# First: 
copy SSH key following: https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-22-04
# Second:
On remote linus machine, do:
```shell
sudo apt install openssh-server
sudo ufw disable
sudo service ssh start
```
