"""
This example demonstrates how to dynamically control the intensity of a light using the VSTLight module.
The intensity of the light is increased when the 'up' key is pressed and decreased when the 'down' key is pressed.

Note that it utilizes the 'keyboard' package to listen for key presses.
"""

import VSTLight
import keyboard


def main() -> None:
    # Create controller object
    lights = VSTLight.NetworkController(4)

    # Configure light
    lights.set_intensity(3, 128)

    # Turn on light
    lights.set_on(3)

    # Set key bindings
    keyboard.add_hotkey(
        "up", lambda: lights.set_intensity(3, min(lights.get_intensity(3) + 5, 255))
    )
    keyboard.add_hotkey(
        "down", lambda: lights.set_intensity(3, max(lights.get_intensity(3) - 5, 0))
    )

    # Listen for key presses and quit on "q"
    while True:
        if keyboard.is_pressed("q"):
            break

    # Turn off light
    lights.set_off(4)

    # Close down gracefully
    lights.destroy()


if __name__ == "__main__":
    main()
