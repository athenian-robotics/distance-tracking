#!/bin/sh
git clone https://github.com/google/protobuf
cd protobuf
./autogen.sh
./configure
make
sudo make install
sudo ldconfig

