import json
import os


def write_devices_to_json(devices, base_path):
    """
    Writes the devices list to a JSON file at the specified base path.

    :param devices: List of devices to be written to the JSON file.
    :param base_path: The base directory where the JSON file will be stored.
    :return: None
    """
    try:
        devices_path = os.path.join(base_path, "devices")
        print(devices_path)
        os.makedirs(devices_path, exist_ok=True)  # Ensure the 'devices' directory exists

        devices_config_path = os.path.join(devices_path, "device_config.json")
        print(devices_config_path)
        data = {
            "devices": devices  # Wrap the devices list inside a dictionary
        }
        with open(devices_config_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)  # Save devices data in a formatted JSON file

    except Exception as e:
        raise Exception(f"Error writing devices to JSON: {e}")
