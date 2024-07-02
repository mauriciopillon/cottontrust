##
Instructions for installing Indy Pool using the Von Network infrastructure on a new virtual machine
##

sudo apt-get update && sudo apt-get upgrade

sudo apt install -y docker.io docker-compose python3 python-pip maven net-tools

sudo usermod -aG docker ubuntu
newgrp docker

sudo systemctl daemon-reload
sudo service docker restart

git clone https://github.com/bcgov/von-network
cd von-network
./manage build
./manage start --logs