#!/bin/bash
sudo apt-get update
sudo apt-get --yes --force-yes install git
sudo apt-get --yes --force-yes install python3-pip
	
git clone https://github.com/j-buss/text_gen_lstm.git
cd text_gen_lstm/train/app
pip3 install -r requirements.txt
	
python3 train_app.py -e 5 -s 10 -g 40

gsutil cp -r output_data* gs://text_gen_lstm_001_output/
