import requests


class Relay:
    def __init__(self , base_url , api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_device(self , device_id):
        url = "device/status"
        data = {
            "id": device_id ,
            "auth_key": self.api_key
        }
        response = requests.post(self.base_url + url , data=data)
        if response.status_code == 200:
            print(response.json())
            pass
        if response.status_code != 200:
            print(response.json())

    def control_device(self , channel , turn , device_id):
        url = "device/relay/control"
        data = {
            "channel": channel ,
            "turn": turn ,
            "id": device_id ,
            "auth_key": self.api_key
        }
        response = requests.post(self.base_url + url , data=data)
        if response.status_code == 200:
            pass
        if response.status_code != 200:
            print(response.json())

    def bulk_control_relays(self , devices):
        """
        Control a group of relays with specified parameters.

        Parameters:
        - devices (list of dict): List of devices to control, each device should be a dictionary with keys:
            - "id" (int): ID of the device.
            - "channel" (int): Index of the relay or switch component.

        Sends a POST request to bulk control relays endpoint with authentication.
        """
        url = "device/relay/bulk_control"
        data = {
            "devices": devices ,
            "auth_key": self.api_key
        }

        response = requests.post(self.base_url + url , json=data)

        if response.status_code == 200:
            pass  # Add any success handling here if needed
        else:
            print(response.json())

class Rollers:
    def __init__(self , base_url , api_key):
        self.base_url = base_url
        self.api_key = api_key

    def control_roller_direction(self , direction , device_id):
        """
        Control the direction of a roller device.

        Parameters:
        - direction (str): Desired direction of the roller, should be 'open', 'close', or 'stop'.
        - device_id (str): ID of the roller device to control.

        Sends a POST request to the roller control endpoint with authentication.
        """
        url = "device/relay/roller/control"
        data = {
            "direction": direction ,
            "id": device_id ,
            "auth_key": self.api_key
        }
        response = requests.post(self.base_url + url , data=data)
        if response.status_code == 200:
            pass  # Add any success handling here if needed
        else:
            print(response.json())

    def control_roller_position(self , pos , device_id):
        """
        Control the roller device.

        Parameters:
        - pos (int): Position to set the roller, should be a number within the range [0..100].
        - device_id (str): ID of the device to control.

        Raises:
        - ValueError: If pos is not within the range [0..100].

        Sends a POST request to the device control endpoint with authentication.
        """
        url = "device/relay/roller/control"
        data = {
            "pos": pos ,
            "id": device_id ,
            "auth_key": self.api_key
        }
        response = requests.post(self.base_url + url , data=data)
        if response.status_code == 200:
            pass
        else:
            print(response.json())

    def bulk_control_rollers(self , devices):
        """
        Control a group of rollers with specified parameters.

        Parameters:
        - devices (list of dict): List of devices to control, each device should be a dictionary with keys:
            - "id" (int): ID of the device.
            - "channel" (int): Index of the roller or cover component.
            - "turn" (str): Desired action for the roller, should be 'open', 'close', or 'stop'.
            - Optional:
                - "position" (int): Position (0 to 100) for rollers supporting it.

        Sends a POST request to bulk control rollers endpoint with authentication.
        """
        url = "device/roller/bulk_control"
        data = {
            "devices": devices ,
            "auth_key": self.api_key
        }

        response = requests.post(self.base_url + url , json=data)

        if response.status_code == 200:
            pass  # Add any success handling here if needed
        else:
            print(response.json())

class Lights:
    def __init__(self , base_url , api_key):
        self.base_url = base_url
        self.api_key = api_key

    def control_light(self , turn=None , white=None , red=None , green=None , blue=None , gain=None , device_id=None):
        """
        Control the light device with specified parameters.

        Parameters:
        - turn (str, optional): Desired state of the light, should be 'on' or 'off'.
        - white (int, optional): White light intensity, should be in the range [0..255].
        - red (int, optional): Red color intensity, should be in the range [0..255].
        - green (int, optional): Green color intensity, should be in the range [0..255].
        - blue (int, optional): Blue color intensity, should be in the range [0..255].
        - gain (int, optional): Gain for RGB color, should be in the range [0..100].
        - device_id (str): ID of the device to control.

        Sends a POST request to the light control endpoint with authentication.
        """
        url = "device/light/control"
        data = {
            "id": device_id ,
            "auth_key": self.api_key
        }

        if turn is not None:
            if turn not in ['on' , 'off']:
                raise ValueError("turn must be either 'on' or 'off'")
            data["turn"] = turn

        if white is not None:
            if not (0 <= white <= 255):
                raise ValueError("white must be a number within the range [0..255]")
            data["white"] = white

        if red is not None:
            if not (0 <= red <= 255):
                raise ValueError("red must be a number within the range [0..255]")
            data["red"] = red

        if green is not None:
            if not (0 <= green <= 255):
                raise ValueError("green must be a number within the range [0..255]")
            data["green"] = green

        if blue is not None:
            if not (0 <= blue <= 255):
                raise ValueError("blue must be a number within the range [0..255]")
            data["blue"] = blue

        if gain is not None:
            if not (0 <= gain <= 100):
                raise ValueError("gain must be a number within the range [0..100]")
            data["gain"] = gain

        response = requests.post(self.base_url + url , data=data)
        if response.status_code == 200:
            pass  # Add any success handling here if needed
        else:
            print(response.json())

    def bulk_control_lights(self , devices):
        """
        Control a group of lights with specified parameters.

        Parameters:
        - devices (list of dict): List of devices to control, each device should be a dictionary with keys:
            - "id" (int): ID of the device.
            - "channel" (int): Index of the light or light component.
            - "turn" (str): Desired state of the light, should be 'on' or 'off'.
            - Optional:
                - "brightness" (int): Brightness level (0 to 100) for lights supporting it.
                - "gain" (int): Gain level (0 to 100) for lights supporting RGB or similar controls.

        Sends a POST request to bulk control lights endpoint with authentication.
        """
        url = "device/light/bulk_control"
        data = {
            "devices": devices ,
            "auth_key": self.api_key
        }

        response = requests.post(self.base_url + url , json=data)

        if response.status_code == 200:
            pass  # Add any success handling here if needed
        else:
            print(response.json())


class Connect:
    def __init__(self , base_url , api_key):
        url = "/device/all_status?show_info=true&no_shared=true"
        data = {
            "auth_key": api_key
        }
        response = requests.post(base_url + url , data=data)
        if response.status_code == 200:
            pass
        if response.status_code != 200:
            print('Error while authenticating')
            print(data)

        self.relays = Relay(base_url , api_key)
        self.rollers = Rollers(base_url , api_key)
        self.lights = Lights(base_url , api_key)
