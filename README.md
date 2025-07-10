<b>Modbus Monitoring for Zabbix (using external script)</b>

This repository provides a custom Python script and two distinct Zabbix templates for monitoring Modbus TCP devices. The solution enables flexible data acquisition from various Modbus devices and integrates them seamlessly into Zabbix for comprehensive monitoring and alerting.

Table of Contents

1. Modbus_custom_like_plugin.py Script
3. Zabbix Templates
4. Requirements
5. Installation
6. Monitored Items
7. Triggers
8. Graphs
9. Value Maps

Modbus_custom_like_plugin.py Script

This Python script acts as a custom Zabbix agent plugin to read data from Modbus TCP devices. It connects to a specified Modbus endpoint and reads values from holding or input registers, decoding them into various data types.

Script Functionality

The Modbus_custom_like_plugin.py script performs the following core functions:

- Modbus TCP Connectivity: Establishes a TCP connection to a Modbus device using the provided IP address and port.
- Register Reading: Supports reading both Holding Registers (function code 3) and Input Registers (function code 4), allowing for versatile data retrieval.
- Data Type Handling: Capable of decoding various data types, including float, double, uint16, int16, uint32, and int32. This is crucial for correctly interpreting numerical values stored across multiple Modbusregisters.
- Command-Line Arguments: The script accepts the following arguments, making it highly configurable:
    endpoint: The Modbus TCP address, e.g., tcp://IP:Port.
    slave_id: The Modbus slave ID of the device.
    function_code: The Modbus function code (3 for Holding Registers, 4 for Input Registers).
    address: The starting Modbus register address to read from.
    count: The number of registers to read.
    data_type: The data type to decode the read registers into (e.g., float, uint16, int32).
    timeout: Connection timeout in seconds (e.g., 5s).
- Error Handling: Includes robust error handling for connection issues, incorrect endpoint formats, insufficient registers for the specified data type, and general Modbus communication errors.

Script Usage:

The script is designed to be executed by Zabbix agent as a UserParameter.

Bash

python3 Modbus_custom_like_plugin.py[<endpoint>,<slave_id>,<function_code>,<address>,<count>,<data_type>,<timeout>]

Example:
python3 Modbus_custom_like_plugin.py[tcp://192.168.1.100:502,1,3,40001,2,float,5s]

Zabbix Templates

This repository includes two distinct Zabbix templates:

- Modbus monitoring_an SKRYPT.xml (referred to as Modbus monitoring_an)
- Modbus monitoring_mp SKRYPT.xml (referred to as Modbus monitoring_mp)

Why Two Templates?

The existence of two separate templates is due to their specialized focus on different types of Modbus devices and their specific monitoring needs. Each template is designed to collect a distinct set of parameters, indicating their application in varying industrial automation or energy monitoring scenarios.

Differences Between Templates:
The templates differ significantly in the types of Modbus registers they query and the specific parameters they monitor, reflecting their intended use cases.

Modbus monitoring_an:

This template is likely designed for monitoring energy analyzers or similar devices that provide general electrical grid parameters and digital I/O status.

Monitored Parameters:

- Digital Input/Output Status: Items like "Input 0.0 Status", "Output 0.0 Status" using JavaScript preprocessing to extract bit states from Modbus words.
- Electrical Parameters: Voltage (e.g., "Voltage L1-N"), Current (e.g., "Current L1"), Total Harmonic Distortion for Voltage and Current (e.g., "THD-R Voltage L1", "THD-R Current L1"), and Frequency.
- Power Metrics: Total Apparent Power, Total Active Power.
- Modbus Addresses: Uses register addresses commonly associated with energy meters and analyzers, e.g., 1 (Voltage L1-N), 13 (Current L1), 43 (THD-R Voltage L1), 49 (THD-R Current L1), 55 (Frequency).
- Triggers: Includes specific triggers for electrical anomalies such as low/high voltage, high current, high THD, and Modbus communication issues (no data).

Modbus monitoring_mp:

This template is tailored for monitoring motor drives or similar industrial automation equipment.

Monitored Parameters:

- Drive States: "Drive Fault State Active", "Drive Ready to Switch On Status", "Drive Run State Active" – using JavaScript preprocessing to interpret status bits.
- Motor Data: Motor Output Frequency, Motor Output Current, Motor Thermal State, Motor Output Voltage, DC Bus Voltage.
- Operational Metrics: Motor Run Time, Total Energy Consumption.
- Device Identification: "Drive Name" (read as text with JavaScript conversion).
- Raw States: "Drive State Raw Word" for direct observation of the drive's status register.
- Modbus Addresses: Uses addresses typically found in motor drive systems, e.g., 3240 (Drive State), 3202 (Motor Output Frequency), 3204 (Motor Output Current), 3208 (Motor Thermal State), 3244 (Motor Run Time),7270 (DC Bus Voltage), 7350 (Drive Temperature).
- Triggers: Focuses on drive-specific conditions such as drive fault, high motor current, high motor thermal state, no motor run time increase, or no energy consumption change.
 
Requirements

- Zabbix Server (version 7.0 or higher recommended)
- Zabbix Agent (on the machine that will execute the Python script and connect to Modbus devices)
- Python 3 installed on the Zabbix Agent host.
- pymodbus library installed on the Zabbix Agent host:
- Bash
- pip install pymodbus
- Modbus TCP device(s) (e.g., energy analyzer, motor drive) accessible from the Zabbix Agent host.

Installation

Script Installation

    Place the script: Copy the Modbus_custom_like_plugin.py script to a directory accessible by the Zabbix agent, e.g., /etc/zabbix/scripts/.

    Set permissions: Ensure the script has execute permissions:
    Bash

chmod +x /etc/zabbix/scripts/Modbus_custom_like_plugin.py

Configure Zabbix Agent UserParameter: Add the following line to your Zabbix agent configuration file (zabbix_agentd.conf or a file in zabbix_agentd.d/):
Ini, TOML

UserParameter=modbus.read.dynamic[*],python3 /etc/zabbix/scripts/Modbus_custom_like_plugin.py "$1" "$2" "$3" "$4" "$5" "$6" "$7"

    Note: The python3 command might need to be adjusted based on your system's Python executable path (e.g., /usr/bin/python3).

Restart Zabbix Agent:
Bash

    sudo systemctl restart zabbix-agent

Template Installation:

Download Templates: Download the Modbus monitoring_an SKRYPT.xml and Modbus monitoring_mp SKRYPT.xml files from this repository.
Import into Zabbix:
    - Navigate to Configuration -> Templates in your Zabbix frontend.
    - Click Import in the top right corner.
    - Click Browse and select one of the XML template files.
    - Click Import.
    - Repeat for the second template.

Host Configuration:

Create/Select Host: Go to Configuration -> Hosts. Create a new host or select an existing one representing your Modbus device.
Add Zabbix Agent Interface: Ensure the host has a Zabbix Agent interface configured, pointing to the IP address of the machine where the Modbus_custom_like_plugin.py script is running.
Link Template:
    - Go to the Templates tab of the host configuration.
    - In the Link new templates section, search for either Modbus monitoring_an or Modbus monitoring_mp (choose the one relevant to your device type) and select it.
    - Click Add, then click Update on the host configuration page.
Configure Macros: The templates use host macros to define Modbus communication parameters.
    - On the host configuration page, go to the Macros tab.
    - Configure the following macros:
        - {$MODBUS_ENDPOINT}: e.g., tcp://192.168.1.100:502 (IP and port of your Modbus device)
        - {$MODBUS_TIMEOUT}: e.g., 5s (timeout for Modbus communication)

Monitored Items:
The templates define a variety of items based on their specific Modbus register mappings. Examples include:

Modbus monitoring_an Items:

- digital.input.0_0.status (Input 0.0 Status)
- total.active.power (Total Active Power)
- current.L1 (Current L1)
- voltage.L1_N (Voltage L1-N)
- frequency (Frequency)
- thd.r.voltage.L1 (THD-R Voltage L1)
- modbus.read.dynamic[{$MODBUS_ENDPOINT},1,3,1,2,float,{$MODBUS_TIMEOUT}] (Master item for raw Modbus data, used by dependent items)

Modbus monitoring_mp Items:

- drive.fault.state (Drive Fault State Active)
- motor.output.frequency (Motor Output Frequency)
- motor.output.current (Motor Output Current)
- motor.thermal.state (Motor Thermal State)
- motor.run.time (Motor Run Time)
- drive.name (Drive Name)
- modbus.read.dynamic[{$MODBUS_ENDPOINT},0,3,3240,4,uint16,{$MODBUS_TIMEOUT}] (Master item for raw Modbus data, used by dependent items)

Triggers:
Each template includes a set of pre-defined triggers relevant to the device type it monitors.

Modbus monitoring_an Triggers:

- High voltage L1-N on {HOST.NAME}
- Low voltage L1-N on {HOST.NAME}
- High current L1 on {HOST.NAME}
- High THD-R Voltage L1 on {HOST.NAME}
- Modbus connection issues on {HOST.NAME}

Modbus monitoring_mp Triggers:

- Drive fault state active on {HOST.NAME}
- High motor output current on {HOST.NAME}
- Motor thermal state high on {HOST.NAME}
- Drive not ready to switch on on {HOST.NAME}
- No change in motor run time on {HOST.NAME}

Graphs:
The templates provide useful graphs for visualizing the collected data.

Modbus monitoring_an Graphs:

- "Voltage L1-N and L2-N"
- "Current L1, L2, L3"
- "THD-R Voltage & Current"
- "Modbus Availability"

Modbus monitoring_mp Graphs:

- "Motor Output Parameters (Frequency, Current, Voltage)"
- "Drive State and Thermal State"
- "Total Energy Consumption"
- "DC Bus Voltage"
- "Modbus Availability"

Value Maps
Both templates extensively use Zabbix Value Maps to translate raw numerical Modbus states into human-readable text.

- Modbus Digital Status: Maps 0 to "OFF" and 1 to "ON" for digital inputs/outputs.
- Modbus Drive State: Maps various bit combinations from the drive state word to meaningful descriptions for the Modbus monitoring_mp template.
- Common Zabbix Status: Maps standard Zabbix internal values (e.g., for availability) to "Available" and "Not available".
