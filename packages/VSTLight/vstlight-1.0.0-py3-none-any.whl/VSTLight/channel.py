from enum import Enum


class ChannelState(Enum):
    """
    Enum representing the possible states of a channel.
    """

    ON = True
    OFF = False


class Channel:
    """
    Class representing a single output channel of the VLP light controller.
    """

    def __init__(self) -> None:
        """
        Initialize the channel object with a default value of 0 and off state.
        Channel intensity is represented as an 8 bit value [0-255].
        State is represented as a boolean value [On: True, Off: False].
        """

        self._intensity = 0
        self._strobe_mode = 1
        self._state = ChannelState.OFF

    @property
    def intensity(self) -> int:
        """
        Get the current intensity of the channel.

        Returns:
        --------
            int: The current intensity of the channel.
        """
        return self._intensity

    @intensity.setter
    def intensity(self, value: int) -> None:
        """
        Set the intensity of the channel. Raises a `ValueError` if the passed value is outside
        the valid range of values.

        Args:
        -----
            value (int): The value to set the channel to. Only 8 bit values are accepted [0-255].
        """
        if not 0 <= value <= 255:
            raise ValueError("Channel intensity must be between 0 and 255")

        self._intensity = value

    @property
    def strobe_mode(self) -> int:
        """
        Get the current strobe mode of the channel

        Returns:
        --------
            int: The current strobe mode of the channel
        """
        return self._strobe_mode

    @strobe_mode.setter
    def strobe_mode(self, mode: int) -> None:
        """
        Set the strobe mode of the channel

        Args:
        -----
            mode (int): The strobe mode to set the channel to. Only values between 1 and 10 are accepted.
        """
        if not 0 < mode <= 10:
            raise ValueError(
                f"Strobe mode identifyer must be integer between 1 and 10, got: {mode}"
            )

        self._strobe_mode = mode

    @property
    def state(self) -> bool:
        """
        Get the current state of the channel.

        Returns:
        --------
            bool: The current state of the channel [On: True, Off: False].
        """
        return self._state.value

    def on(self) -> None:
        """
        Set the state of the channel to on.
        """
        self._state = ChannelState.ON

    def off(self) -> None:
        """
        Set the state of the channel to off.
        """
        self._state = ChannelState.OFF

    def toggle(self) -> None:
        """
        Toggle the state of the channel.
        """
        self._state = ChannelState(not self._state.value)
