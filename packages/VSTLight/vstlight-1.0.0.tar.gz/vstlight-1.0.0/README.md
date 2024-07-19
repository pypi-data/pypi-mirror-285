# VST-Light
![Tests](https://github.com/Attrup/VST-Light/actions/workflows/package_tests.yaml/badge.svg)
![Typecheck](https://github.com/Attrup/VST-Light/actions/workflows/static_typecheck.yaml/badge.svg)
![Formatting](https://github.com/Attrup/VST-Light/actions/workflows/formatting.yaml/badge.svg)

*VST-Light* is a Python package designed to facilitate seamless control of network-compatible VLP light controllers from VS Technology. By abstracting the proprietary communication protocols, *VST-Light* provides a straightforward and user-friendly interface, enabling users to easily manage their VLP lighting systems without needing to understand the underlying technical complexities. In order to best utilize the module, it is recommended to read through the [User Guide](#user-guide) before use. Additionally, the [example](#example) of the module in use should also be checked.

### Compatibility
The following light controllers from VS Technology are supported:
- VLP-2430-2eN
- VLP-2430-3eN
- VLP-2430-4eN
- VLP-2460-4eN

## Installation
VST-Light is available on PyPI and can be easily installed using pip:
```zsh
pip install VSTLight
```
## User Guide
### Initialization
To use the module in your project, simply import the `VSTLight` module into your code and create an instance of the `NetworkController` class, specifying the number of channels available on the connected light controller. If the IP of the light controller has been changed from the default `192.168.11.20`, you will need to specify the new IP address as well.
```python
import VSTLight

lights_a = VSTLight.NetworkController(4)                    # Default IP
lights_b = VSTLight.NetworkController(4, "192.168.11.128")  # Updated IP
```

At the time of creation, the `NetworkController` object will open a connection to the physical light controller. If this fails, a `ConnectionError` will be raised. Therefore, it is necessary to connect the light controller and turn it on before running any code that relies on the `NetworkController` object. When connecting a light controller, it is required to update the IP of the Ethernet adapter used to make the connection to be on the same subnet as the controller. The VLP controllers are hardcoded to reply to the IP `192.168.11.1`, so it is recommended to update the Ethernet adapter to this specific IP. However, any IP on the `192.168.11.XXX` subnet will work as long as it is not occupied by another device.  
The network connection has a timeout of 5 seconds, so the call to create the `NetworkController` object is blocking until a connection is established or the timeout period elapses.

Please refer to the documentation of the connected VLP light controller for more information on its operation and the meanings of the different modes.

### Updating the Channels
Having crated an instance of the `NetworkController` class, the intensity and state of a single channel can be updated:
```python
lights_a.set_intensity(2, 158)
lights_a.set_on(2)
```
Alternatively all channels can be updated at once:
```python
lights_b.set_all_intensities(200)
lights_b.set_all_on()
```

Note that if an invalid value is passed to any of the class methods, a `ValueError` will be raised. Additionally, the channel number passed to the controller object corresponds directly to the channel number on the physical light controller. Therefore, it is **NOT** zero-indexed; instead, it starts at 1 for the lowest channel.

### Speed Limitations
The VLP controllers are physically limited in how quickly they can receive new commands. Each command must be spaced out by at least 5 ms to be interpreted correctly. To accommodate this, the `VSTLight` module tracks the time since the last command. If the time is less than 5 ms, the program will sleep until 5 ms have passed since the last command was sent. Therefore, any method call on a `NetworkController` object has the potential to be blocking if performed within 5 ms of another call.

If this behavior is undesirable for your use case, consider running the `NetworkController` in a separate thread to prevent blocking your main thread at any point.

### Example
Below is an example program that turns a light connected to channel 1, on and off 1000 times:
```python
from VSTLight import NetworkController
import time

# Create controller object
lights = NetworkController(4)

# Set the intensity of channel 1 to 255
lights.set_intensity(1, 255)

# Toggle the light on and off 1000 times
for _ in range(1000):
    lights.set_on(1)
    time.sleep(0.5)

    lights.set_off(1)
    time.sleep(0.5)

# Close the connection and shut down gracefully
lights.destroy()
```

Refer to the section below for a list of all available methods. Complete example programs showcasing the module functionality can be found in the [examples](https://github.com/Attrup/VST-Light/tree/main/examples) folder.
## Available Methods
Below is an exhaustive list of all methods currently available using the `NetworkController` class:
- `set_intenisty`: Updates the intensity of a single channel
- `get_intensity`: Returns the intensity of a single channel
- `set_on`: Turn a single channel on
- `set_off`: Turn off a single channel
- `toggle`: Toggle the on-off state of a channel
- `set_strobe_mode`: Updates the strobe mode of a single channel
- `get_strobe_mode`: Returns the strobe mode of a single channel
- `set_all_intensities`: Updates the intensity of all channels
- `set_all_on`: Turn all channels on
- `set_all_off`: Turn all channels off
- `toggle_all`: Toggle the on-off state of a channel
- `set_all_strobe_modes`: Set the strobe mode of all channels
