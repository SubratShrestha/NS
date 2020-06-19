#!/bin/bash

echo "Running Application for $OSTYPE"
echo $1
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
python App.py $1 &
echo "Starting on Windows";
elif [[ "$OSTYPE" == "darwin"* ]]; then
python App.py $1 &
elif [[ "$OSTYPE" == "cygwin" ]]; then
        # POSIX compatibility layer and Linux environment emulation for Windows
python Windows.py &
sleep 1;
python ble/ble.py $1 &
elif [[ "$OSTYPE" == "msys" ]]; then
# Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
python Windows.py &
sleep 1;
python ble/ble.py $1 &
elif [[ "$OSTYPE" == "win32" ]]; then
# I'm not sure this can happen.
python Windows.py &
sleep 1;
python ble/ble.py $1 &
elif [[ "$OSTYPE" == "freebsd"* ]]; then
python App.py $1 &
else
python App.py $1 &
fi