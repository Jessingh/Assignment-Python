"""
Author: Jessica Singh
Date:   January/24
Description: This Python script leverages the Flask web framework to create a RESTful API 
             for interacting with Cisco DEVNet SandBox via Netmiko.

             Below are the endpoints -
             /network_interaction      #Connection to the device.
             /configure_loopback       #Configuring loopback.
             /delete_loopback          #Deleting loopback.
             /device_interfaces        #Display all the device interfaces.        
             
"""

# Import necessary modules from Flask and Netmiko libraries
from flask import Flask, request, jsonify
from netmiko import ConnectHandler

# Create a Flask web application
app = Flask(__name__)

# Cisco DevNet Sandbox device details
device_info = {
    'device_type': 'cisco_xr',
    'ip': 'sandbox-iosxr-1.cisco.com',
    'username': 'USER',     #Your Username
    'password': 'PASSWORD', #Your Password 
    'port': 22,  # SSH port
}

# Creates a pathway for handling network interaction via REST POST request
@app.route('/network_interaction', methods=['POST'])
def network_interaction():
    try:
        # Extract data from the incoming request
        data = request.json

        # Assuming data includes information like command to be executed
        command = data.get('command')

        # Interact with the network device using Netmiko
        netmiko_response = send_netmiko_request(device_info, command)

        # Format the data into a JSON response
        return jsonify(format_response(netmiko_response))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
      
# Configuring a loopback on the device
@app.route('/configure_loopback', methods=['POST'])
def configure_loopback():
    try:
        # Extract data from the incoming request
        data = request.json

        # Assuming data includes information like loopback_number and ip_address
        loopback_number = data.get('loopback_number')
        ip_address = data.get('ip_address')

        # Configuration command for the loopback interface
        config_commands = [
            f'interface Loopback{loopback_number}',
            f'ip address {ip_address}',
            'commit',  
            'exit'     
        ]

        # Interact with the network device using Netmiko
        netmiko_response = send_netmiko_config(device_info, config_commands)
    
        # Format the data into a JSON response
        return jsonify(format_response(netmiko_response))

    except Exception as e:
        return jsonify({'error': str(e)}), 500
      
# Deleting a loopback on the device 
@app.route('/delete_loopback', methods=['POST'])
def delete_loopback():
    try:
        # Extract data from the incoming request
        data = request.json

        # Assuming data includes information like loopback_number
        loopback_number = data.get('loopback_number')

        # Configuration command to delete the loopback interface
        delete_commands = [
            f'no interface Loopback{loopback_number}',
            'commit',  
            'exit'     
        ]

        # Interact with the network device using Netmiko
        netmiko_response = send_netmiko_config(device_info, delete_commands)
    
        # Format the data into a JSON response
        return jsonify(format_response(netmiko_response))     

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# List all interfaces on device    
@app.route('/device_interfaces', methods=['POST'])
def device_interfaces():
    try:
        # Interact with the network device using Netmiko
        netmiko_response = send_netmiko_request(device_info, 'show ip interface brief')

        # Format the data into a JSON response
        return jsonify(format_response(netmiko_response))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
      
# Network_interaction & Device_interfaces function call.
# Sends a Netmiko request to a network device.
#The output received from the device after executing the command, or an error message if an exception occurs.
def send_netmiko_request(device_info, command):
    try:
        # Establish an SSH connection using Netmiko
        with ConnectHandler(**device_info) as ssh_conn:
            output = ssh_conn.send_command(command)
        return output
      
    except Exception as e:
        return f'Netmiko Error: {str(e)}'
      
# Loopback_configure & Delete_loopback function call. 
# Sends configuration commands to a network device using Netmiko.
def send_netmiko_config(device_info, config_commands):
    try:
        # Establish an SSH connection using Netmiko
        with ConnectHandler(**device_info) as ssh_conn:
            # Send configuration commands
            output = ssh_conn.send_config_set(config_commands)
        return output
      
    except Exception as e:
        return f'Netmiko Error: {str(e)}'
      
# Format response function call
def format_response(netmiko_response):
    lines = [line.strip() for line in netmiko_response.split('\n') if line.strip()]
    return {'netmiko_response': lines}
    
# Run the Flask application on the specified host and port.
# host: '0.0.0.0' allows the application to be accessible externally.
# port: 5000 is the default port for Flask applications
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)    
