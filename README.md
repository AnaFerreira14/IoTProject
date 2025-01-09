# Weather Station

This project was made for the course of IoT. It consists of a sensor (raspberry pi) that sends information to the cloud (AWS) which will be processed using python capabilities.

## How was the data collected?

The DH11 sensor was used with an 8 bit microcontroller to output temperature and humidity values as serial data. The resolution for both temperature and humidity was 16 bits. The temperature measurement range is 0 ° C to 50 ° C with an accuracy of ±1°C. The humidity range is 20% to 90% with an accuracy of ±2%. The Pico W board was programmed in micro-python using the Pico W version 1.24.0 firmware. The machine2 library was used to access the data through the Pico W pins.

## How do you run the project?

### Create an AWS DynamoDB Table

Sign up into the ![Amazon website](aws.amamazon.com) or create an account. Search Dynamodb in the console and select the service. Then, select Create a Table, name it as you please (e.g.: DHT11) and choose a partition key (make sure the data type is Number). This is the name of the primary key value in your table. Every key item added to your table should have a unique partition key value. Once you configured that, you can just step through and create the table with the default settings.

### AWS Lambda Function

In order to create a lambda function, go to the services menu in Amazon AWS and select the Lambda icon. Select create function. We want to Author from scratch. You can name it whatever you like and make sure that you select Python for the runtime. Go ahead and click the create button once that is done. In the code source panel, insert the code contained in the file lambdaFunction.py, which is located in the folder LambdaFunction from this repository.

The provided Lambda function is designed to handle events triggered by AWS IoT Core, specifically from a DHT11 sensor on a Raspberry Pi Pico W. In summary, this Lambda function processes IoT Core events, extracts DHT11 sensor data, and writes it to the 'DHT11' DynamoDB table, with logging statements aiding in monitoring and debugging (if your table has a different name, you should change the table_name parameter). 

Note that the names of the fields are dependent on how you pass the event to the Lambda function. Keep in mind that this can be made to fit your use case very easily with some simple changes. Every time you make a change make sure you Deploy your Lambda!

### IAM Permissions

Amazon automatically generates a role for your Lambda function. In order to upload to your table that you created, you will have to increase the permissions on this role. Search IAM in the services console and select the appropriate service. Select the role that was created for your function, in this case it was DHT11-TO-DB-role. Select add permissions and add the AdministratorAccess policy so that the user has access to anything on AWS. Be cautious with this role in production! After doing this, your lambda function should be set up.

### IoT Core Setup

First thing in IoT Core is to setup policies and create a "Thing" so Amazon can receive messages straight from you Raspberry Pi Pico W. Go to the AWS Console and search IoT Core in the search bar, select IoT Core accordingly to open the service. To create a policy scroll down on the left side menu and select Policies under Security. There are many ways you can customize this policy, for our general purpose we can select four Policy actions: iot:Connect, iot:Publish, iot:Receive and iot:Subscribe. For all the Policy actions, select the Policy effect 'Allow' and select the Policy resource '*'. You can name the policy however you like! For further customization of policies, you can look into their documentation. In general, policies are designed to limit/extend access of a device to the channels of your IoT network.

Once you have your policy setup you can create a Thing. Go to All Devices in the left bar and select Things > Create Things. Then, select Create single thing. Afterwards, name the Thing as you please. In order to get the Device Certificate, select Auto-generate a new certificate (which is also the recommended option). Add the policy you created to your Thing. Now you have a Thing, you will need to download 4 files: Device Cert, Public and Private Key, and Root CA 2048 file. You will need to upload these to your Pico W for your MQTT client to work! Finally, save the endpoint of your AWS IoT Core server, we will also be substituting it in the code. You can find it by going to the Settings on the left panel of the AWS Amazon website (it is under Device data endpoint). Keep this information as private as possible!

Now that you have a Thing with a policy, we want to create an IoT Rule, that will tell AWS to send data from an MQTT channel to the Lambda function, completing the tunneling of information on the AWS side. Go to the left panel in Message routing and select Rules. Click Create Rule and name it how you like, in this case we name it PicoW-To_lambda. Next, we define the selection of the rule, in this case we select all values on the 'DHT11' topic for our IoT Core. We do this by writing the SQL statement SELECT * FROM 'DHT11'. This is telling AWS to take the whole message/attributes from every message on that channel.

Next select the Rule actions, in this case we select a Lambda action and the name of the function we created! AWS makes it easy for us, we can click th button 'Add rule action' and our rule is now created. Congratulations, you have set up the AWS infrastructure needed to implement this project!

### Setting up the Raspberry Pi Pico W board

This step will walk you through the set up of the Thonny IDE which will be used to write micro-python files in the Raspberry Pi Pico W board. If you have already set up Thonny IDE, please feel free to skip this step!

Without further ado, let's install the Thonny IDE by going to the ![Thonny website](https://thonny.org/) and clicking on the right link to download the package for your operating system. After that, run the downloaded executable file and follow the installation procedure (use all the default settings). Then, the MicroPython Firmware needs to be flashed on the Raspberry Pi Pico W. Therefore, you should connect the Raspberry Pi Pico W to your computer while holding the BOOTSEL button at the same time so that it goes into bootloader mode to flash the firmware. Afterwards, open Thonny IDE and go to Tools > Options. Select the Interpreter tab on the new window that opens. Select MicroPython (Raspberry Pi Pico) for the interpreter, and the Try to detect port automatically for the Port. Then, click on Install or update MicroPython. Select the Pico W/Pico WH MicroPython variant. Finally, click Install. After a few seconds, the installation should be completed.

### Setting up the necessary files

Before we get to the main file, we need to import onto the Raspberry Pi Pico W board the 4 files that encompass the necessary certificates to connect with our Thing. Moreover, we must download the library for MQTT in micro-python. Open your micro-python editor (in this case we are using Thonny) to manage files on the Raspberry Pi Pico W and then upload the 4 files. Next, let's import the umqtt library onto the Raspberry Pi Pico W board. You can find the aforementioned file in this repository by going to the lib folder that is inside the PicoW folder. Then, copy this file and upload it onto the lib folder in your Raspberry Pi Pico W board. This is all you need for the library.

Now that we have the setup, let's go ahead and address the file that will contain the main code.

### Collecting the data

In order to gather data, a micro-python script was made to collect the temperature and humidity captured by the DHT11 sensor. This script was named `PicoW_dht11_Mqtt.py` and is located in the folder PicoW of this repository. To run the program, the file must be uploaded to the Raspberry Pi Pico board. This can be done using the Thonny IDE, which is the recommended MicroPython IDE for the Raspberry Pi Pico. After that, some changes need to be made to the block of code shown below:

```
SSID = ""
WIFI_PASSWORD = ""
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_CLIENT_KEY = ""
MQTT_CLIENT_CERT = ""
MQTT_BROKER = ""
MQTT_BROKER_CA = "AmazonRootCA1.pem"
```

In the SSID parameter write the name of your Wi-Fi network and in the WIFI_PASSWORD write the password of your Wi-Fi. Then, in the MQTT_CLIENT_KEY parameter, write the name of the private key file (this file's name ends with pem.key). In the MQTT_CLIENT_CERT parameter, write the name of the device certificate (this file's name ends with pem.crt). Next, write the previously obtained device endpoint to the MQTT_BROKER parameter. Finally, write the root CA certificate's name to the MQTT_BROKER_CA parameter.

When you finish completing this information, you can run the micro-python file in your board.

In summary, the code initializes the I2C interface for communication with the DHT11 sensor, reads temperature and humidity data from the sensor, and publishes this data to the AWS IoT Core using MQTT with secure SSL/TLS communication. This setup ensures the integrity and security of the communication between the Raspberry Pi Pico W and the AWS IoT Core.

### Testing the MQTT connection

To ensure that everything is running smoothly, go back to the DynamoDb service in AWS, select Explore items and then select your table. If the board has succesfully connected to the AWS services, you should see data popping up on the DynamoDb table as time goes by. The table should be filled progressively with more and more data points.

However, if you ran the MicroPython code successfully yet you don't see anything in your table, it is likely you configured something wrong in your Lambda function. You can view the logs of your Lambda in the CloudWatch service by selecting it from the Services menu. Go to the appropriate Log Group and view the Python logs, it is likely you will see errors and you will have to debug the Lambda function and redeploy if you would like to make some changes.

## References

https://www.hackster.io/Shilleh/how-to-send-data-to-aws-dynamodb-from-raspberry-pi-pico-w-6a4ee1

https://github.com/gianmarcozizzo/IoT-2020/tree/master

https://randomnerdtutorials.com/getting-started-raspberry-pi-pico-w/#install-thonny-ide

https://randomnerdtutorials.com/raspberry-pi-pico-dht11-dht22-micropython/

## Schematic diagram of the project

![IoTDiagramv2](https://github.com/user-attachments/assets/025b2f39-fa44-4a02-b56c-3c6fb8fd936e)
