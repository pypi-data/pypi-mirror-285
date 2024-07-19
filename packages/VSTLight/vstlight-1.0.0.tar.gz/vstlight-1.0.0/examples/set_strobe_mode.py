"""
This example demonstrates how to set the strobe mode of a channel using the VSTLight module.
"""

from VSTLight import NetworkController


def main() -> None:
    # Create controller object
    lights = NetworkController(4)

    # Set strobe modes of two channels
    lights.set_strobe_mode(2, 4)  # Set channel 2 to strobe mode 4, i.e. 200 us on time
    lights.set_strobe_mode(4, 10)  # Set channel 4 to strobe mode 10, i.e. 40 ms on time

    # Trig the channels using the trig input of the light controller unit
    # Below is simply a dummy loop to keep the program running.
    while True:
        if input("Press 'q' to quit") == "q":
            break

    # Close down gracefully
    lights.destroy()


if __name__ == "__main__":
    main()
