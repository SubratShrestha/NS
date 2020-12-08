#!/bin/bash
# optional arguments: -prune -uuid_format
echo "Running Application for $OSTYPE"
echo $1 $2
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
python Windows.py &
sleep 1;
python ble/ble.py $1 &
elif [[ "$OSTYPE" == "darwin"* ]]; then
python App.py $1 &
elif [[ "$OSTYPE" == "cygwin" ]]; then
python Windows.py &
sleep 1;
python ble/ble.py $1 &
elif [[ "$OSTYPE" == "msys" ]]; then
python Windows.py &
sleep 1;
python ble/ble.py $1 &
elif [[ "$OSTYPE" == "win32" ]]; then
python Windows.py &
sleep 1;
python ble/ble.py $1 &
elif [[ "$OSTYPE" == "freebsd"* ]]; then
python App.py $1 &
else
python App.py $1 &
fi