import unittest

from src.VSTLight.channel import Channel


class TestIPFormat(unittest.TestCase):
    def setUp(self) -> None:
        self.channel = Channel()
        return super().setUp()

    def test_default_state(self):
        """
        Test that the default state of the channel is off, intensity is 0 and strobe mode is 1

        """
        self.assertEqual(self.channel.intensity, 0)
        self.assertEqual(self.channel.strobe_mode, 1)
        self.assertFalse(self.channel.state)

    def test_set_intensity(self):
        """
        Test that the intensity of the channel can be set

        """
        self.channel.intensity = 100
        self.assertEqual(self.channel.intensity, 100)

    def test_all_valid_intensities(self):
        """
        Test that all valid intensities can be set

        """
        for i in range(256):
            self.channel.intensity = i
            self.assertEqual(self.channel.intensity, i)

    def test_set_intensity_out_of_range_high(self):
        """
        Test that setting the intensity of the channel to an invalid value (too high) raises a ValueError

        """
        with self.assertRaises(ValueError):
            self.channel.intensity = 256

    def test_set_intensity_out_of_range_low(self):
        """
        Test that setting the intensity of the channel to an invalid value (too low) raises a ValueError

        """
        with self.assertRaises(ValueError):
            self.channel.intensity = -4

    def test_set_strobe_mode(self):
        """
        Test that the strobe mode can be correctly updated

        """
        self.channel.strobe_mode = 8
        self.assertEqual(self.channel.strobe_mode, 8)

    def test_set_strobe_mode_low(self):
        """
        Test that setting the strobe mode to an invalid value (too low) raises a ValueError

        """
        with self.assertRaises(ValueError):
            self.channel.strobe_mode = 0

    def test_set_strobe_mode_high(self):
        """
        Test that setting the strobe mode to an invalid value (too high) raises a ValueError

        """
        with self.assertRaises(ValueError):
            self.channel.strobe_mode = 19

    def test_turn_on(self):
        """
        Test that the channel can be turned on

        """
        self.channel.on()
        self.assertTrue(self.channel.state)

    def test_turn_on_when_on(self):
        """
        Test that the channel can be turned on when it is already on

        """
        self.channel.on()
        self.assertTrue(self.channel.state)

        self.channel.on()
        self.assertTrue(self.channel.state)

    def test_turn_off(self):
        """
        Test that the channel can be turned off (after being turned on)

        """
        self.channel.on()
        self.assertTrue(self.channel.state)

        self.channel.off()
        self.assertFalse(self.channel.state)

    def test_turn_off_when_off(self):
        """
        Test that the channel can be turned off when it is already off

        """
        self.assertFalse(self.channel.state)

        self.channel.off()
        self.assertFalse(self.channel.state)

    def test_toggle(self):
        """
        Test that the channel can be toggled

        """
        self.channel.toggle()
        self.assertTrue(self.channel.state)

        self.channel.toggle()
        self.assertFalse(self.channel.state)

        self.channel.toggle()
        self.assertTrue(self.channel.state)
