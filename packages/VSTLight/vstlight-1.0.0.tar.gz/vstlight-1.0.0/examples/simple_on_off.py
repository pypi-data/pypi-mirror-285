"""
This example demonstrates how to turn a light on and off using the VSTLight module.
"""

from VSTLight import NetworkController
import time


def main() -> None:
    # Create controller object
    lights = NetworkController(4)

    # Configure light
    lights.set_intensity(4, 128)

    # Turn on light and wait 1 second
    lights.set_on(4)
    time.sleep(1)

    # Strobe light on 10 times
    for _ in range(20):
        lights.toggle(4)
        time.sleep(0.5)

    # Turn off light
    lights.set_off(4)

    # Close down gracefully
    lights.destroy()


if __name__ == "__main__":
    main()
