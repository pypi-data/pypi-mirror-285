import unittest
import socket
import select
import time

from src.VSTLight.network_controller import NetworkController

# Define the localhost and ports for the dummy light controller. Two different ports are used to
# ensure that the two test classes do not interfere with each other by trying to bind to the same port.
HOST = "127.0.0.1"
PORT_A = 6070
PORT_B = 6080

# Define the wait time for the socket to receive data
WAIT_TIME = 0.0001


class TestNetworkControllerInitialization(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Runs once before all tests in class.

        Operations:
        ----------
        - Creates a mock controller by opening a socket on localhost
        - Listens for incoming connections allowing a NetworkController to connect
        """
        cls.mock_controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.mock_controller.bind((HOST, PORT_A))
        cls.mock_controller.listen()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Runs once after all tests have been completed.

        Operations:
        ----------
        - Close the dummy socket connection
        - Wait for the socket to close before continuing
        """
        cls.mock_controller.close()

    def tearDown(self) -> None:
        """
        Destroy the NetworkController object after each test if it exists
        """
        if hasattr(self, "lights"):
            self.controller.destroy()

    def test_network_controller_initialization(self):
        """
        Test that the NetworkController object can be initialized with good arguments
        """
        self.controller = NetworkController(4, HOST, PORT_A)
        self.assertIsInstance(self.controller, NetworkController)

    def test_network_controller_initialization_with_bad_channels(self):
        """
        Test that the NetworkController object cannot be initialized with a bad number of channels
        """
        with self.assertRaises(ValueError):
            self.controller = NetworkController(5, HOST, PORT_A)

    def test_network_controller_initialization_with_bad_port(self):
        """
        Test that the NetworkController object cannot be initialized with a bad IP
        """
        with self.assertRaises(ValueError):
            self.controller = NetworkController(4, HOST, -1)

    def test_network_controller_destruction(self):
        """
        Test that the NetworkController object can be destroyed
        """
        self.controller = NetworkController(4, HOST, PORT_A)
        self.controller.destroy()
        self.assertNotIn("controller", locals())


class TestNetworkControllerFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Runs once before all tests in class.

        Operations:
        ----------
        - Creates a mock controller by opening a socket on localhost
        - Listens for incoming connections allowing a NetworkController to connect
        - Initializes a NetworkController object
        - Accepts the incoming connection from the NetworkController to establish a communication channel
        - Clears input buffer of the mock connection
        """
        cls.mock_controller = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.mock_controller.bind((HOST, PORT_B))
        cls.mock_controller.listen()

        cls.controller = NetworkController(4, HOST, PORT_B)

        cls.mock_conn, _ = cls.mock_controller.accept()

        time.sleep(WAIT_TIME)
        cls.mock_conn.recv(1024)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Runs once after all tests have been completed.
        - Destroy the NetworkController object
        - Close the mock connection
        - Close the mock controller socket
        """
        cls.controller.destroy()

        cls.mock_conn.close()
        cls.mock_controller.close()

    def tearDown(self) -> None:
        """
        Clears the input buffer of the mock connection after each test if any data is present
        """
        read, _, _ = select.select([self.mock_conn], [], [], 0.001)

        if read:
            self.mock_conn.recv(1024)

    def test_checksum(self):
        """
        Test that the checksum is calculated correctly for the message
        (Uses example from the VLP controller specsheet setting channel 2 to 125 intensity)
        """
        self.controller.set_on(2)
        self.controller.set_intensity(2, 125)

        cmd = self.mock_conn.recv(1024).decode(encoding="ascii")

        self.assertEqual(cmd[7:9], "7F")

    def test_set_intensity_local(self):
        """
        Test that the set_intensity method changes the local intensity of a channel
        """
        self.controller.set_intensity(1, 255)
        self.assertEqual(self.controller._NetworkController__channels[0].intensity, 255)

    def test_set_intensity_remote(self):
        """
        Test that the set_intensity method changes the remote intensity of a channel
        """
        self.controller.set_on(4)
        self.controller.set_intensity(4, 255)

        cmd = self.mock_conn.recv(1024).decode(encoding="ascii")

        self.assertEqual(cmd[1:7], "03F255")

    def test_set_on_local(self):
        """
        Test that the set_on method changes the local state of a channel
        """
        self.controller.set_on(1)
        self.assertTrue(self.controller._NetworkController__channels[0].state)

    def test_set_on_remote(self):
        """
        Test that the set_on method changes the remote state of a channel
        """
        self.controller.set_intensity(2, 128)
        self.controller.set_on(2)

        cmd = self.mock_conn.recv(1024).decode(encoding="ascii")

        print(f"Command: {cmd}")
        self.assertEqual(cmd[1:7], "01F128")

    def test_set_off_local(self):
        """
        Test that the set_off method changes the local state of a channel
        """
        self.controller.set_off(3)

        self.assertFalse(self.controller._NetworkController__channels[2].state)

    def test_set_off_remote(self):
        """
        Test that the set_off method changes the remote state of a channel
        """
        self.controller.set_off(4)

        cmd = self.mock_conn.recv(1024).decode(encoding="ascii")

        self.assertEqual(cmd[1:7], "03F000")

    def test_return_intensity(self):
        """
        Test that the get_intensity method returns the correct intensity of a channel
        """
        self.controller.set_intensity(1, 200)

        self.assertEqual(self.controller.get_intensity(1), 200)

    def test_set_strobe_mode_local(self):
        """
        Test that the set_strobe_mode method changes the local strobe mode of a channel
        """
        self.controller.set_strobe_mode(1, 5)
        self.assertEqual(self.controller._NetworkController__channels[0].strobe_mode, 5)

    def test_set_strobe_mode_remote(self):
        """
        Test that the set_strobe_mode method changes the remote strobe mode of a channel
        """
        self.controller.set_strobe_mode(2, 5)

        cmd = self.mock_conn.recv(1024).decode(encoding="ascii")

        self.assertEqual(cmd[1:6], "01S05")

    def test_return_strobe_mode(self):
        """
        Test that the get_strobe_mode method returns the correct strobe mode of a channel
        """
        self.controller.set_strobe_mode(1, 5)

        self.assertEqual(self.controller.get_strobe_mode(1), 5)
