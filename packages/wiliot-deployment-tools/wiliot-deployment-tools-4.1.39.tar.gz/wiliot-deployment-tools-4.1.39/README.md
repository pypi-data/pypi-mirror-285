# PyWiliot: wiliot-deployment-tools #

wiliot-deployment-tools is a python library for accessing Wiliot's Deployment and Automation Tools.
This python package includes the following CLI utilities:
 - Automatic Configuration Tool (`wlt-config`)
 - Calibration Management Tool (`wlt-clibration-mgmt`)
 - Firmware Update Tool (`wlt-firmware`)
 - Power Management Tool (`wlt-power-mgmt`)
 - Log Viewer (`wlt-log`)
 - Connectivity Analyzer (`wlt-connectivity-analyzer`)
 - Gateway Certificate (`wlt-gw-certificate`)
 - Power Optimization Tool (`wlt-power-optimization`)
 - BLE Simulator CLI (`wlt-ble-simulator`)
 - BLE Sniffer CLI (`wlt-ble-sniffer`)

## Installing wiliot-deployment-tools
````commandline
pip install wiliot-deployment-tools
````

## Using wiliot-deployment-tools
This package includes the following CLI Utilities:
### Automatic Configuration Tool
Automatically connects to all Gateways / Bridges in the location specified, and configure them to optimal parameters.

```
usage: wlt-config -owner OWNER -location LOCATION [-ota] [-no_gp_zone] [-pacing_interval PACING_INTERVAL] [-ignore_bridges [IGNORE_BRIDGES [IGNORE_BRIDGES ...]]] [--expected_num_brgs EXPECTED_NUM_BRGS]

required arguments:
  -owner OWNER         Platform owner id
  -location LOCATION   Location name in Wiliot platform. If location has ' ' in name, input location wrapped with double quotes: --location "LOCATION NAME"

additional (optional) arguments:
  -ota         Updating FW version to latest for all devices
  -no_gp_zone          don't use Global pacing group by zone (all bridges will be GPG=0)
  -pacing_interval PACING_INTERVAL
                        Pacing interval for all devices
  -ignore_bridges [IGNORE_BRIDGES [IGNORE_BRIDGES ...]]
                        bridges to ignore in the tool - their configuration won't be changed
  -expected_num_brgs EXPECTED_NUM_BRGS
                        Number of expected bridges in location. The tool will try to connect to all bridges (excluding those specified in ignore bridges) until reaching expected number.

example usage: wlt-config --owner wiliot --location "My Deployment" --ota_upgrade --pacing_interval 10 --ignore_bridges 1234ABCD0123
```

### Calibration Management
Configure Wiliot Bridge calibration mode, broadcast is optional
```
usage: wlt-calibration-mgmt -owner OwnerID -brg BridgeID -gw GW -mode CalibrationMode [-timeout TIMEOUT]
usage (broadcast): wlt-calibration-mgmt -owner OwnerID -gw GW -mode CalibrationMode [-timeout TIMEOUT]

required arguments:
  -owner OWNER  Owner ID
  -brg BRG      Bridge ID (required only for non broadcast)
  -gw GW        GW ID to configure bridge (required only for broadcast)
  -mode Mode    CalibrationMode on of 3 options: 0-regular, 1-no ch37, 2-ch37 on data only

optional arguments:
  -timeout TIMEOUT      Minutes timeout (not required, defaults to 5 minutes)

  example usage: wlt-calibration-mgmt -owner wiliot -brg 0123ABCD -gw AB1234CD -mode 1
```

### Firmware Update
Update Wiliot Gateways and Bridges firmware version OTA.
 #### Print Available Versions 
 Prints all avaliable Firmware versions for update for every GW Type
```
usage: wlt-firmware -owner OWNER [-beta] versions

optional arguments:
  -beta              show available beta versions / update to beta firmware

example usage: wlt-firmware -o wiliot versions
```

 #### Firmware Update
 Run OTA Process, first updating specified GWs to latest / specified FW version. Afterwards seuqentially update each specified Bridges / all Bridges to the same Firmware version.
 ```
usage: wlt-firmware update -owner OWNER [-beta] [-version VERSION] [-gw GW [GW ...]] [-brg BRG [BRG ...]] [-all_brgs] [-ignore_bridges IGNORE_BRIDGES [IGNORE_BRIDGES ...]] [-action]


optional arguments:
  -beta              show available beta versions / update to beta firmware
  -version VERSION      Desired version. if not specified, will update to latest available version
  -gw GW [GW ...]       Gateways to update (multiple allowed)
  -brg BRG [BRG ...]    Bridges to update (multiple allowed)
  -all_brgs             update all bridges connected to Gateways
  -ignore_bridges IGNORE_BRIDGES [IGNORE_BRIDGES ...]
                        bridges to ignore
  -action               update using action API
  -force                update bridge even if its already in desired version (applicable only with -action)

  example usage: wlt-firmware -o wiliot update -gw GW0123 -all_brgs
  ```

### Power Management
Use Wiliot Bridge power management functionality
#### Enter Power Management
Configure Specified Bridges to work in power management configuration.
```
usage: wlt-power-mgmt -o OwnerID enter -brg BridgeID -sleepduration SLEEPDURATION -onduration ONDURATION [-keepalive KEEPALIVE] [-scan SCAN] [-ledoff] [-gw GW] [-timeout TIMEOUT]

required arguments:
  -owner OWNER  Owner ID
  -brg BRG      Bridge ID

optional arguments:
  -sleepduration SLEEPDURATION
                        Sleep duration (minutes)
  -onduration ONDURATION
                        On duration (seconds) *rounds to nearest 30 second interval*
  -keepalive KEEPALIVE  Keep alive period (seconds) *rounds to nearest 5 second interval* (not required, defaults to 30 seconds)
  -scan SCAN            Keep alive scan (milliseconds) *rounds to nearest 10 millisecond interval* (not required, defaults to 300 milliseconds)
  -ledoff               Configure LEDs off (on by default)
  -gw GW                GW ID to configure bridge (required only for broadcast mode)
  -timeout TIMEOUT      Minutes timeout (not required, defaults to 5 minutes)

  example usage: wlt-power-mgmt -o wiliot enter -brg 0123ABCD -sleepduration 5 -onduration 60
```
#### Exit Power Management
Return specified bridges out of power management mode and into normal working mode.
```
usage: wlt-power-mgmt -o OwnerID exit -brg BridgeID [-gw GW] [-no_config] [-timeout TIMEOUT]

required arguments:
  -owner OWNER  Owner ID
  -brg BRG      Bridge ID

optional arguments:
  -gw GW            GW ID to configure bridge (not required)
  -no_config        If used, GW will not change to optimal configuration
  -timeout TIMEOUT  Minutes timeout (not required, defaults to 5 minutes)

example usage: wlt-power-mgmt -o wiliot exit -brg BridgeID
```

  

### Log Viewer
View Wiliot Gateway logs
```
usage: wlt-log -owner OWNER -gw GW

Log Viewer - CLI Tool to view Wiliot Gateway logs

required arguments:
  -owner OWNER  Owner ID
  -gw GW        Gateway ID
```

### Broker Change
Change MQTT broker for Wiliot GWs
```
usage: wlt-broker-change [-h] -broker {wiliot,hivemq} -owner OWNER -gw GW [-env {prod,test,dev}] [-cloud {aws,gcp}] [-legacy]

required arguments:
  -broker {wiliot,hivemq}
                        Broker to change to
  -owner OWNER          Owner ID
  -gw GW                Gateway ID
  -env {prod,test,dev}  Environment
  -cloud {aws,gcp}      Wiliot Cloud
  -legacy               Legacy Broker Change```

```

### Connectivety Analyzer
Check the RSSI values for GW-> Bridge transmissions (as received at the bridge)
Can operate by: location, bridges or gateways
Return the bridges with low connection
Additional option: bridge-gw connectivity log printer (-bridge_log)
```
usage (connectivity check): wlt-connectivity-analyzer -owner OWNER -location Location
usage (bridge-gw conn log): wlt-connectivity-analyzer -owner OWNER -brg BRG -bridge_log

required arguments:
  -owner OWNER  Owner ID
  -bridge_log (Only for bridge-gw conn log)
  -brg BRG (Only for bridge-gw conn log)


optional arguments:
  -gws GwsList         List of gateways IDs to check connection to the bridges they see
  -brgs BridgesList    List of bridges IDs to check connection 
  -location Location   Location name (as written in platform) to check all bridges in
```

------------------

For more documentation and instructions, please contact us: support@wiliot.com

### Gateway Certificate
Test Wiliot GWs capabilities.
The GW Certificate includes different test that run sequentially to test each capability reported by the GW.
To run the GW Certificate the GW needs to use a public MQTT Broker (HiveMQ):

Host:	broker.hivemq.com
TCP Port:	1883
Websocket Port:	8000
TLS TCP Port:	8883
TLS Websocket Port:	8884

More information can be found at https://www.mqtt-dashboard.com/.

#### Connection Test
Processes status packet sent by the GW to the MQTT Broker and validates it according to API Version.

#### Uplink Test
Simulates Wiliot MEL and validates that data is uploaded correctly to the cloud.

#### Downlink Test
Sends advertising packets via MQTT to GW and validates correct advertising by GW.

#### Stress Test
Increments time delays between packets to evaluate GW's capability in handling increasing packets per second within a minute.

#### GW Certificate Release Notes:
Version 4.1.38:
* Added stress test
* Added info/warning badges
* Separated sequendId/aliasBridgeId validations
* Tooltips
* Brief error explainers
* DFU fix

```
usage: wlt-gw-certificate [-h] -owner OWNER -gw GW [-suffix SUFFIX] [-tests {connection,uplink,downlink}]

Gateway Certificate - CLI Tool to test Wiliot GWs

required arguments:
  -owner OWNER  Owner ID
  -gw GW        Gateway ID

optional arguments:
  -suffix       Allow for different suffixes after the GW ID in MQTT topics.
  -tests        Pick specific tests to run
  -h, --help    show this help message and exit
  ```


## Power Optimization Tool:
Plots the gain-current curve for a given bridge to help determine optimal configuration in terms of power consumption
```
usage: wlt-power-optimization -bridge_type BridgeType -dc DutyCycle -gw GW -rxtx_period RxTxPeriod


required arguments:
  -bridge_type BRIDGE_TYPE  The bridge type that will be analyzed
  -dc DC      Duty cycles to compare in the plot
  -rxtx_period RXTX_PERIOD        The rxtx periods in mili-sec corresponding to the duty cycles
  

  example usage: wlt-power-optimization -bridge_type minew -dc 0.33 0.5 -rxtx_period 15 20
```


## BLE Sniffer:
Uses USB Dev Board to sniff Wiliot BLE Packets
```
BLE Sniffer - CLI Tool to Sniff BLE Packets

optional arguments:
  -h, --help     show this help message and exit

required arguments:
  -p P           UART Port.
  -c {37,38,39}  channel
usage: wlt-sniffer [-h] -p P -c {37,38,39}
```

## BLE Simulator:
Uses USB Dev Board to send Wiliot BLE Packets
```
optional arguments:
  -h, --help      show this help message and exit

required arguments:
  -p P            USB UART Port
  -packet PACKET  packet

optional arguments:
  -c C            channel (if not specified packet will be sent on all BLE adv. channels (37/38/39))
  -delay DELAY    ms delay between packets (if not specified defaults to 20ms)
  -dup DUP        duplicates (defaults to 3)
  -output OUTPUT  output power (defaults to 8dBm)
  -ts TS          trigger by time stamp

usage: wlt-ble-sim [-h] -p P -packet PACKET [-c C] [-delay DELAY] [-dup DUP] [-output OUTPUT] [-ts TS]
```

## Release Notes:
Version 4.2.0:
* Add BLE interfaces CLI (Sniffer/Simulator)

Version 4.1.9:
* Support for GCP/AWS in connectivity analyzer
* Allowing connectivity analyzer to run without specifying a location
* Support FW version 3.16 - MEL modules

Version 4.1.8:
* Added power optimization tool to package

Version 4.1.7:
* Support for GCP/AWS cloud in extended_api
* Support FW 3.15

Version 4.1.1:
* Bridge-Gw connectivity log print

Version 4.1.0:
* Custom message support
* GW Certificate - coupling test
* Fixes for calibration management

Version 4.0.13:
* Add Gateway Certificate (Alpha)

Version 4.0.12:
* Add new Connectivity Analyzer

Version 4.0.11:
* Add broadcast to calibration management
* Bugfixes for power management using android GW

Version 4.0.10:
* Internal fixes

Version 4.0.8:
* Support for python 3.11
* Added new calibration mgmt tool

Version 4.0.7:
* Android power management support
* Bugfix when no gateway logs found
  
Version 4.0.4:
* Bugfixes, add relevant printouts to CLI to help understand errors.

Version 4.0.3:
* Initial release of CLI tools suite - Automatic Configuration Tool, Firmware Update, Power Management, Log Viewer.

Version 4.0.0:
* First version


The package previous content was published under the name 'wiliot' package.
for more information please read 'wiliot' package's release notes

-----------------

### MacOS Installation
#### Getting around SSL issue on Mac with Python 3.7 and later versions

Python version 3.7 on Mac OS has stopped using the OS's version of SSL and started using Python's implementation instead. As a result, the CA
certificates included in the OS are no longer usable. To avoid getting SSL related errors from the code when running under this setup you need
to execute Install Certificates.command Python script. Typically you will find it under
~~~~
/Applications/Python\ 3.7/Install\ Certificates.command
~~~~

-----------------

#### Python 3 on MacOS
The default Python version on mac is 2.x. Since Wiliot package requires Python 3.x you should download Python3 
(e.g.  Python3.7) and make python 3 your default.
There are many ways how to do it such as add python3 to your PATH (one possible solution https://www.educative.io/edpresso/how-to-add-python-to-the-path-variable-in-mac)
