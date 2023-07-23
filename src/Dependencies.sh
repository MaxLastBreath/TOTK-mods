#!/bin/bash

# Create miniconda directory
mkdir -p ~/miniconda3

# Download Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh

# Install Miniconda
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3

# Remove the Miniconda installer
rm -rf ~/miniconda3/miniconda.sh

# Initialize Conda for bash
~/miniconda3/bin/conda init bash

# Initialize Conda for zsh
~/miniconda3/bin/conda init zsh

# Install packages using pip
~/miniconda3/bin/pip install requests Pillow patool tk