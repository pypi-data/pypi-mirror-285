"""
This example demonstrates how to turn all lights on and off using the VSTLight module.
"""

from VSTLight import NetworkController


def main() -> None:
    # Create controller object
    lights = NetworkController(4)

    # Configure lights
    lights.set_all_intensities(128)

    # Turn on all lights
    lights.set_all_on()

    while True:
        match input("Press 'q' to quit: "):
            case "q":
                break
            case _:
                lights.toggle_all()

    # Turn off light
    lights.set_all_off()

    # Close down gracefully
    lights.destroy()


if __name__ == "__main__":
    main()
