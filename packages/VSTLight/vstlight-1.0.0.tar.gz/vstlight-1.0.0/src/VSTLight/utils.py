import time


def validate_ip_format(ip: str) -> bool:
    """
    Validate the format of an IP address by checking the following:
    - The IP address must contain 3 dots separating the subnets
    - Each subnet of the IP address must be between 1 and 3 characters long
    - Each subnet of the IP address must be a value between 0 and 255

    Args:
    -----
        ip (str): The IP address to validate.

    Returns:
    --------
        bool: True if the IP address is valid, False otherwise.
    """

    return (
        ip.count(".") == 3
        and all(0 < len(val) <= 3 for val in ip.split("."))
        and all(0 <= int(val) <= 255 for val in ip.split("."))
    )


def compare_and_wait(last_cmd_time: float, wait_time: float) -> None:
    """
    Blocking function call! Compare the current time to the time of the last command
    and wait until at least wait_time have passed since the last command was sent before returning.

    Args:
    -----
        last_cmd_time (int): The time the last command was sent.
        wait_time (int) [s]: The minimum time to wait before returning (in seconds).
    """
    if time.monotonic() - last_cmd_time < wait_time:
        time.sleep(wait_time - (time.monotonic() - last_cmd_time))
