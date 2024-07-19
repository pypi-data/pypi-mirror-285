import unittest
import time
from src.VSTLight.network_controller import validate_ip_format, compare_and_wait


class TestIPFormat(unittest.TestCase):
    def test_default_ip(self):
        """
        Test that the valid default IP is accepted
        """
        ip = "192.168.11.20"
        self.assertTrue(validate_ip_format(ip))

    def test_valid_ip(self):
        """
        Test that a valid IP is accepted
        """
        ip = "114.0.11.20"
        self.assertTrue(validate_ip_format(ip))

    def test_valid_ip2(self):
        """
        Test that a valid IP is accepted
        """
        ip = "10.0.0.11"
        self.assertTrue(validate_ip_format(ip))

    def test_valid_ip3(self):
        """
        Test that a valid IP is accepted
        """
        ip = "0.255.0.1"
        self.assertTrue(validate_ip_format(ip))

    def test_ip_with_too_high_value(self):
        """
        Test that an IP with too high subnet values is rejected
        """
        ip = "192.168.11.256"
        self.assertFalse(validate_ip_format(ip))

    def test_ip_with_invalid_subnet_value(self):
        """
        Test that an IP with incorrect subnet value is rejected
        """
        ip = "114..11.20"
        self.assertFalse(validate_ip_format(ip))

    def test_ip_with_few__subnets(self):
        """
        Test that an IP with too few subnets is rejected
        """
        ip = "10.0.11"
        self.assertFalse(validate_ip_format(ip))

    def test_ip_with_many_subnets(self):
        """
        Test that an IP with too many subnets is rejected
        """
        ip = "0.255.0.0.1"
        self.assertFalse(validate_ip_format(ip))


class TestCompareAndWait(unittest.TestCase):
    def test_waiting_time(self):
        """
        Test that the compare_and_wait function waits for at least the specified time
        """
        last_cmd_time = time.monotonic()
        wait_time = 0.005
        compare_and_wait(last_cmd_time, wait_time)

        self.assertGreaterEqual(time.monotonic() - last_cmd_time, wait_time)

    def test_no_waiting_time(self):
        """
        Test that the compare_and_wait function does not wait if the specified time has already passed
        """
        last_cmd_time = time.monotonic()
        wait_time = 0.005
        compare_and_wait(0, wait_time)

        self.assertLessEqual(time.monotonic() - last_cmd_time, wait_time)
