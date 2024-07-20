# General Usage

## Start ARTNet app
- From EC2 dashboard select instance, then Instance State --> Start Instance
- From EC2 instance dashboard, get public IPv4 ip address
- Ensure ssh key has the correct permissions
```
chmod 600 ARTNet_Key.pem
```
- ssh into instance
```
ssh -i ARTNet_Key.pem ubuntu@[IP]
```
- start artnet app in detached mode
```
sudo docker-compose pull --policy always app && sudo docker-compose --profile app up -d
```
- exit SSH session (CTRL+D)

## Stop ARTNet app
- From EC2 instance dashboard, get public IPv4 ip address
- ssh into instance
```
ssh -i ARTNet_Key.pem ubuntu@[IP]
```
- bring down instance
```
sudo docker-compose --profile app down
```
- exit SSH session (CTRL+D)
- From EC2 dashboard select instance, then Instance State --> Stop Instance

## Connecting to ARTNet with GUI
- From EC2 instance dashboard, get public IPv4 ip address
- Start ARTNet GUI
- Paste IP address into ARTNet Address field
- Configure remaining options as needed
- Click "Connect"



# Creating and Configuring a new EC2 instance for ARTNet
## Create EC2 Instance
- Go to EC2 Dashboard, click Launch Instance
- OS Image: Ubuntu 64-bit architecture
- Instance Type: c5.xlarge
- Key Pair: ARTNet_Key (already made, `ARTNet_Key.pem` is found in repo
- Network Settings - Select existing security group -> `ARTNet-Security-Group`
- Configure Storage: Default
- Click Launch Instance

## Install tools on instance
- From EC2 instance dashboard, get public IPv4 ip address
- Ensure ssh key has the correct permissions
```
chmod 600 ARTNet_Key.pem
```
- ssh into instance
```
ssh -i ARTNet_Key.pem ubuntu@[IP]
```
- install docker
```
sudo apt update && sudo apt install -y docker.io
```
- install latest version of docker-compose
``` 
VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | grep -Po '"tag_name": "\K.*\d')
DESTINATION=/usr/bin/docker-compose
sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION
sudo chmod 755 $DESTINATION
```

## Upload docker compose file to instance
- Copy over using scp command
```
scp -i ART_Net.pem -r compose.yaml ubuntu@[IP]:.
```

## Shut Down Instance Without Deleting It
 - From EC2 dashboard select instance, then Instance State --> Stop Instance

# Random Bits of useful info

- wipe all docker containers, networks, etc
   `sudo docker system prune -a -f`
- view docker-compose logs
  `sudo docker-compose --profile dataandvoicetest logs [-f]`
