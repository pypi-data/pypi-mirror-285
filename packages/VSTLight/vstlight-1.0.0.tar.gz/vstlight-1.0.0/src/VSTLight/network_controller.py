import socket
import time
from .channel import Channel
from .utils import validate_ip_format, compare_and_wait

# Waiting time between commands in seconds (5ms) to avoid overloading the controller.
# Dictated by the VLP controller specsheet
WAIT_TIME = 0.005


class NetworkController:
    """
    Class representing a VLP light controller. This class is responsible for sending
    commands to the controller and verifying the success by evaluating the responses
    from the unit.
    """

    def __init__(
        self, channels: int, ip: str = "192.168.11.20", port: int = 1000
    ) -> None:
        """
        Initialize the NetworkController object and connect to the controller itself.
        Init will throw `ValueErrors` if the IP address is invalid or the specified
        number of channels is not supported by the controller. If the controller
        is unreachable a `ConnectionError` will be thrown.

        If the light controller is unreachable at any point during the lifetime of the
        object, function calls will be blocking for up to 5 seconds, before raising a
        `ConnectionError`.

        The physical VLP light controller has a limit to the number of commands it can
        process continously. To avoid overloading the controller, commands are limited
        to one every 5ms. If a command is sent before this time has passed, the call will
        block until the time has passed.

        Args:
        -----
            channels (int): The number of channels the controller object should have. Must be between 1 and 4.
            ip (str): The IP address of the controller. Defaults to the native IP address of the VLP controllers.
            port (int): The port of the controller [0-65535]. Hard coded to 1000 in the VLP controllers.
        """
        # Validate arguments
        if not validate_ip_format(ip):
            raise ValueError(f"Invalid IP address: {ip}")

        if not 0 <= port <= 65535:
            raise ValueError(f"Invalid port: {port} - Must be a positive integer")

        if channels not in [1, 2, 3, 4]:
            raise ValueError(
                f"Invalid number of channels: {channels} - Must be between 1 and 4"
            )

        # Validate number of channels
        # Set internal variables and create socket
        self.__ip = ip
        self.__channels = [Channel() for _ in range(channels)]
        self.__port = port
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.settimeout(5)
        self.__last_cmd_time = 0.0

        # Connect to the controller
        try:
            self.__sock.connect((self.__ip, self.__port))
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to controller with IP: {ip}"
            ) from e

        # Initialize all controller channels to intensity 0 (off)
        for i in range(channels):
            self.set_off(i + 1)
            self.set_strobe_mode(i + 1, 1)

    def destroy(self) -> None:
        """
        Destroys the NetworkController object. All channels are set to off and the connection to the controller is closed.
        """
        for i in range(len(self.__channels)):
            self.set_off(i + 1)

        self.__sock.close()
        del self

    def set_intensity(self, channel_id: int, value: int) -> None:
        """
        Set the light intensity of a channel. If the channel is off, the intensity will be set locally but not transmitted
        to the controller. If the channel is on, the intensity will additionally be transmitted to the controller.

        Args:
        -----
            channel_id (int): The channel to set the intensity of. Corresponds to the channel number on the controller [1-4].
            value (int): The intensity to update the channel with. Only 8 bit values are accepted [0-255].
        """
        # Validate arguments
        self.__verify_channel_id(channel_id)

        if not 0 <= value <= 255:
            raise ValueError("Channel intensity must be between 0 and 255")

        # Convert channel ID to index
        channel_idx = channel_id - 1

        # Update the stored channel intensity and send the command
        self.__channels[channel_idx].intensity = value

        # Update the value on the controller if the channel is on
        if self.__channels[channel_idx].state:
            self.__send_command(f"{channel_idx:02}F{value:03}")

    def get_intensity(self, channel_id: int) -> int:
        """
        Get the current intensity of a channel.

        Args:
        -----
            channel_id (int): The channel to get the intensity of. Corresponds to the channel number on the controller [1-4].

        Returns:
        --------
            int: The current intensity of the channel.
        """
        # Validate arguments
        self.__verify_channel_id(channel_id)

        # Convert channel ID to index
        channel_idx = channel_id - 1

        return self.__channels[channel_idx].intensity

    def set_on(self, channel_id: int) -> None:
        """
        Set the state of a channel on the controller.

        Args:
        -----
            channel_id (int): The channel to turn on. Corresponds to the channel number on the controller [1-4].
        """
        # Validate arguments
        self.__verify_channel_id(channel_id)

        # Convert channel ID to index
        channel_idx = channel_id - 1

        # Update the stored channel state and send the command if the intensity is greater than 0
        self.__channels[channel_idx].on()

        if self.__channels[channel_idx].intensity > 0:
            self.__send_command(
                f"{channel_idx:02}F{self.__channels[channel_idx].intensity:03}"
            )

    def set_off(self, channel_id: int) -> None:
        """
        Set the state of a channel on the controller.

        Args:
        -----
            channel_id (int): The channel to turn off. Corresponds to the channel number on the controller [1-4].
        """
        # Validate arguments
        self.__verify_channel_id(channel_id)

        # Convert channel ID to index
        channel_idx = channel_id - 1

        # Update the stored channel state and send the command
        self.__channels[channel_idx].off()
        self.__send_command(f"{channel_idx:02}F000")

    def toggle(self, channel_id: int) -> None:
        """
        Toggle the state of a channel on the controller between on and off (Inverting current state).

        Args:
        -----
            channel_id (int): The channel to toggle. Corresponds to the channel number on the controller [1-4].
        """
        # Validate arguments
        self.__verify_channel_id(channel_id)

        # Convert channel ID to index
        channel_idx = channel_id - 1

        # Toggle the state of the channel
        if self.__channels[channel_idx].state:
            self.set_off(channel_id)
        else:
            self.set_on(channel_id)

    def set_strobe_mode(self, channel_id: int, mode: int) -> None:
        """
        Set the strobe mode of a channel on the controller. The following strobe modes are available,
        where the time specifies the 'on' time of the channel after a trig signal is recieved. Refer to
        the light controller docutmentation for further information.

        Strobe modes:
        - `01` = 40 us
        - `02` = 80 us
        - `03` = 120 us
        - `04` = 200 us
        - `05` = 600 us
        - `06` = 1.2 ms
        - `07` = 4 ms
        - `08` = 10 ms
        - `09` = 20 ms
        - `10` = 40 ms

        Args:
        -----
            channel_id (int): The channel to set the strobe mode of. Corresponds to the channel number on the controller [1-4].
            mode (int): The strobe mode to set [1-10]. Refer to list above, leading zeros are not required.
        """
        # Validate arguments
        self.__verify_channel_id(channel_id)

        # Convert channel ID to index
        channel_idx = channel_id - 1

        # Update the stored channel strobe mode and send the command
        self.__channels[channel_idx].strobe_mode = mode
        self.__send_command(f"{channel_idx:02}S{mode:02}")

    def get_strobe_mode(self, channel_id: int) -> int:
        """
        Get the strobe mode of a channel on the controller.

        Strobe modes:
        - `01` = 40 us
        - `02` = 80 us
        - `03` = 120 us
        - `04` = 200 us
        - `05` = 600 us
        - `06` = 1.2 ms
        - `07` = 4 ms
        - `08` = 10 ms
        - `09` = 20 ms
        - `10` = 40 ms

        Returns:
        --------
            int: Strobe mode of the specified channel
        """
        # Validate arguments
        self.__verify_channel_id(channel_id)

        # Convert channel ID to index
        channel_idx = channel_id - 1

        return self.__channels[channel_idx].strobe_mode

    def set_all_intensities(self, value: int) -> None:
        """
        Set the intensity of all channels to the same value.

        Args:
        -----
            value (int): The intensity to set all channels to. Only 8 bit values are accepted [0-255].
        """
        for i in range(len(self.__channels)):
            self.set_intensity(i + 1, value)

    def set_all_on(self) -> None:
        """
        Set all channels to the on state.
        """
        for i in range(len(self.__channels)):
            self.set_on(i + 1)

    def set_all_off(self) -> None:
        """
        Set all channels to the off state.
        """
        for i in range(len(self.__channels)):
            self.set_off(i + 1)

    def toggle_all(self) -> None:
        """
        Toggle the state of all channels on the controller between on and off (Inverting current state).
        """
        for i in range(len(self.__channels)):
            self.toggle(i + 1)

    def set_all_strobe_modes(self, mode: int) -> None:
        """
        Set the strobe mode of all channels on the controller. The following strobe modes are available,
        where the time specifies the 'on' time of the channel after a trig signal is recieved. Refer to
        the light controller docutmentation for further information.

        Strobe modes:
        - `01` = 40 us
        - `02` = 80 us
        - `03` = 120 us
        - `04` = 200 us
        - `05` = 600 us
        - `06` = 1.2 ms
        - `07` = 4 ms
        - `08` = 10 ms
        - `09` = 20 ms
        - `10` = 40 ms

        Args:
        -----
            mode (int): The strobe mode to set [1-10]. Refer to list above, leading zeros are not required.
        """
        for i in range(len(self.__channels)):
            self.set_strobe_mode(i + 1, mode)

    def __verify_channel_id(self, channel_id: int) -> None:
        """
        Verify that a channel ID is valid. Throws a ValueError if the channel ID if not.

        Args:
        -----
            channel_id (int): The channel ID to verify.
        """
        if not 1 <= channel_id <= len(self.__channels):
            raise ValueError(f"Channel ID must be between 1 and {len(self.__channels)}")

    def __send_command(self, cmd: str) -> None:
        """
        Send a command to the controller in the VLP IP protocol format. This is achieved by adding
        a header (@), checksum, and a delimiter (<CR><LF>) to the command passed to the function,
        before encoding it to ascii bytes and sending it to the controller.

        Args:
        -----
            cmd (str): The command to send to the controller.
        """

        # Add header (@) and calculate checksum according to the VLP IP protocol
        cmd = f"@{cmd}"
        checksum = sum(ord(char) for char in cmd) % 256

        # Add lowest byte of checksum and delimiter (<CR><LF>) to command
        cmd += f"{checksum:02X}\r\n"

        # Check that controller is ready to receive a new command and send when ready
        compare_and_wait(self.__last_cmd_time, WAIT_TIME)
        self.__last_cmd_time = time.monotonic()

        self.__sock.send(cmd.encode(encoding="ascii"))
