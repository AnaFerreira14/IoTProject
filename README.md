# Weather Station

This project was made for the course of IoT. It consists of a sensor (raspberry pi) that sends information to the cloud (AWS) which will be processed using python capabilities.

## How was the data collected?

The DH11 sensor was used with an 8 bit microcontroller to output temperature and humidity values as serial data. The resolution for both temperature and humidity was 16 bits. The temperature measurement range is 0 ° C to 50 ° C with an accuracy of ±1°C. The humidity range is 20% to 90% with an accuracy of ±2%. The Pico W board was programmed in micro-python using the Pico W version 1.24.0 firmware. The machine2 library was used to access the data through the Pico W pins.

## How do you run the project?

### Setting up the Raspberry Pi Pico W board

Firstly, let's install the Thonny IDE by going to the ![url](https://thonny.org/) and clicking on the right link to download the package for your operating system. After that, run the downloaded executable file and follow the installation procedure (use all the default settings). Then, the MicroPython Firmware needs to be flashed on the Raspberry Pi Pico W. Therefore, you should connect the Raspberry Pi Pico W to your computer while holding the BOOTSEL button at the same time so that it goes into bootloader mode to flash the firmware. Afterwards, open Thonny IDE and go to Tools > Options. Select the Interpreter tab on the new window that opens.

### Collecting the data

In order to collect the data, a micro-python script was made to collect the temperature and humidity captured by the DHT11 sensor. This script was named `PicoW/PicoW_dht11_Mqtt.py` and is located in the folder PicoW. To run the program, the file must be uploaded to the Raspberry Pi Pico board. This can be done using the Thonny IDE, which is the recommended MicroPython IDE for the Raspberry Pi Pico. After that, you can run the micro-python file in your board.

## References

https://www.hackster.io/Shilleh/how-to-send-data-to-aws-dynamodb-from-raspberry-pi-pico-w-6a4ee1

https://github.com/gianmarcozizzo/IoT-2020/tree/master

https://randomnerdtutorials.com/getting-started-raspberry-pi-pico-w/#install-thonny-ide

https://randomnerdtutorials.com/raspberry-pi-pico-dht11-dht22-micropython/

## Schematic diagram of the project

![IoTDiagramv2](https://github.com/user-attachments/assets/025b2f39-fa44-4a02-b56c-3c6fb8fd936e)
