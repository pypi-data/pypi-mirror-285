"""
This example creates a simple light controller that toggles the state of two lights when the "t" key is pressed.
Each of the lights can also be toggled individually by pressing the "1" and "2" keys.

Note that it utilizes the 'keyboard' package to listen for key presses.
"""

import VSTLight
import keyboard


def toggle_lights(lights: VSTLight.NetworkController) -> None:
    # Function to toggle the state of both lights
    lights.toggle(1)
    lights.toggle(2)


def main() -> None:
    # Create controller object
    lights = VSTLight.NetworkController(4)

    # Configure lights with intensity [10/255]
    lights.set_intensity(1, 10)
    lights.set_intensity(2, 10)

    # Set key bindings
    keyboard.add_hotkey("t", lambda: toggle_lights(lights))
    keyboard.add_hotkey("1", lambda: lights.toggle(1))
    keyboard.add_hotkey("2", lambda: lights.toggle(2))

    # Listen for key presses and quit on "q"
    while True:
        if keyboard.is_pressed("q"):
            break

    # Close down gracefully
    lights.destroy()


if __name__ == "__main__":
    main()
