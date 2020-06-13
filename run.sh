#!/bin/bash

echo "Running Application for $OSTYPE"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
python App.py &
echo "Starting on Windows";
elif [[ "$OSTYPE" == "darwin"* ]]; then
python App.py &
elif [[ "$OSTYPE" == "cygwin" ]]; then
        # POSIX compatibility layer and Linux environment emulation for Windows
python NeuroStim.py &
sleep 1;
python ble.py &
elif [[ "$OSTYPE" == "msys" ]]; then
# Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
python NeuroStim.py &
sleep 1;
python ble.py &
elif [[ "$OSTYPE" == "win32" ]]; then
# I'm not sure this can happen.
python NeuroStim.py &
sleep 1;
python ble.py &
elif [[ "$OSTYPE" == "freebsd"* ]]; then
python App.py &
else
python App.py &
fi