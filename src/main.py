import socket
import struct
import sys

_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

PNS_PRODUCT_ID = b'AB'
"""product category"""

# PNS command identifier
PNS_RUN_CONTROL_COMMAND = b'S'
"""operation control command"""
PNS_CLEAR_COMMAND = b'C'
"""clear command"""
PNS_GET_DATA_COMMAND = b'G'
"""get status command"""

# response data for PNS command
PNS_ACK = 0x06
"""normal response"""
PNS_NAK = 0x15
"""abnormal response"""

# LED unit for motion control command
PNS_RUN_CONTROL_LED_OFF = 0x00
"""light off"""
PNS_RUN_CONTROL_LED_ON = 0x01
"""light on"""
PNS_RUN_CONTROL_LED_BLINKING_SLOW = 0x02
"""blinking(slow)"""
PNS_RUN_CONTROL_LED_BLINKING_MEDIUM = 0x03
"""blinking(medium)"""
PNS_RUN_CONTROL_LED_BLINKING_HIGH = 0x04
"""blinking(high)"""
PNS_RUN_CONTROL_LED_FLASHING_SINGLE = 0x05
"""flashing single"""
PNS_RUN_CONTROL_LED_FLASHING_DOUBLE = 0x06
"""flashing double"""
PNS_RUN_CONTROL_LED_FLASHING_TRIPLE = 0x07
"""flashing triple"""
PNS_RUN_CONTROL_LED_NO_CHANGE = 0x09
"""no change"""

# buzzer for motion control command
PNS_RUN_CONTROL_BUZZER_STOP = 0x00
"""stop"""
PNS_RUN_CONTROL_BUZZER_RING = 0x01
"""ring"""
PNS_RUN_CONTROL_BUZZER_NO_CHANGE = 0x09
"""no change"""


class PnsRunControlData:
    """operation control data class"""

    def __init__(self, led_red_pattern: int, led_amber_pattern: int, led_green_pattern: int, led_blue_pattern: int, led_white_pattern: int,
                 buzzer_mode: int):
        """
        operation control data class

        Parameters
        ----------
        led_red_pattern: int
            LED Red pattern
        led_amber_pattern: int
            LED Amber pattern
        led_green_pattern: int
            LED Green pattern
        led_blue_pattern: int
            LED Blue pattern
        led_white_pattern: int
            LED White pattern
        buzzer_mode: int
            buzzer mode
        """
        self._led_red_pattern = led_red_pattern
        self._led_amber_pattern = led_amber_pattern
        self._led_green_pattern = led_green_pattern
        self._led_blue_pattern = led_blue_pattern
        self._led_white_pattern = led_white_pattern
        self._buzzer_mode = buzzer_mode

    def get_bytes(self) -> bytes:
        """
        Get the binary data of the operation control data.

        Returns
        -------
        data: bytes
            Binary data of operation control data
        """
        data = struct.pack(
            'BBBBBB',               # format
            self._led_red_pattern,     # LED Red pattern
            self._led_amber_pattern,     # LED Amber pattern
            self._led_green_pattern,     # LED Green pattern
            self._led_blue_pattern,     # LED Blue pattern
            self._led_white_pattern,     # LED White pattern
            self._buzzer_mode,   # buzzer mode
        )
        return data


class PnsStatusData:
    """status data of operation control"""

    def __init__(self, data: bytes):
        """
        status data of operation control

        Parameters
        ----------
        data: bytes
            Response data for get status command
        """
        self._ledPattern = data[0:5]
        self._buzzer = int(data[5])

    @property
    def ledPattern(self) -> bytes:
        """LED Pattern 1 to 5"""
        return self._ledPattern[:]

    @property
    def buzzer(self) -> int:
        """buzzer mode"""
        return self._buzzer


def main():
    args = sys.argv
    argc = len(sys.argv)
    
    # Connect to LR5-LAN
    socket_open('192.168.10.1', 10000)

    try:
        if args[1] == 'S':
            # operation control command
            if argc >= 8:
                run_control_data = PnsRunControlData(
                    int(args[2]),
                    int(args[3]),
                    int(args[4]),
                    int(args[5]),
                    int(args[6]),
                    int(args[7]),
                )
                pns_run_control_command(run_control_data)

        elif args[1] == 'C':
            # clear command
            pns_clear_command()

        elif args[1] == 'G':
            # get status command
            status_data = pns_get_data_command()
            # Display acquired data
            print("Response data for status acquisition command")
            # LED Red pattern
            print("LED Red pattern :" + str(status_data.ledPattern[0]))
            # LED Amber pattern
            print("LED Amber pattern :" + str(status_data.ledPattern[1]))
            # LED Green pattern
            print("LED Green pattern :" + str(status_data.ledPattern[2]))
            # LED Blue pattern
            print("LED Blue pattern :" + str(status_data.ledPattern[3]))
            # LED White pattern
            print("LED White pattern :" + str(status_data.ledPattern[4]))
            # buzzer mode
            print("buzzer mode :" + str(status_data.buzzer))

    finally:
        # Close the socket
        socket_close()


def socket_open(ip: str, port: int):
    """
    Connect to LR5-LAN

    Parameters
    ----------
    ip: str
        IP address
    port: int
        port number
    """
    _sock.connect((ip, port))


def socket_close():
    """
    Close the socket.
    """
    _sock.close()


def send_command(send_data: bytes) -> bytes:
    """
    Send command

    Parameters
    ----------
    send_data: bytes
        send data

    Returns
    -------
    recv_data: bytes
        received data
    """
    # Send
    _sock.send(send_data)

    # Receive response data
    recv_data = _sock.recv(1024)

    return recv_data


def pns_run_control_command(run_control_data: PnsRunControlData):
    """
    Send operation control command for PNS command

    Each color of the LED unit and the buzzer can be controlled by the pattern specified in the data area

    Operates with the color and buzzer set in the signal light mode

    Parameters
    ----------
    run_control_data: PnsRunControlData
        Red/amber/green/blue/white LED unit operation patterns, buzzer mode
        Pattern of LED unit (off: 0, on: 1, blinking(slow): 2, blinking(medium): 3, blinking(high): 4, flashing single: 5, flashing double: 6, flashing triple: 7, no change: 9)
        Buzzer pattern (Stop: 0, Ring: 1, no change: 9)
    """
    # Create the data to be sent
    send_data = struct.pack(
        '>2ssxH',                   # format
        PNS_PRODUCT_ID,             # Product Category (AB)
        PNS_RUN_CONTROL_COMMAND,    # Command identifier (S)
        6,                          # Data size
    )
    send_data += run_control_data.get_bytes()

    # Send PNS command
    recv_data = send_command(send_data)

    # check the response data
    if recv_data[0] == PNS_NAK:
        raise ValueError('negative acknowledge')

def pns_clear_command():
    """
    Send clear command for PNS command

    Turn off the LED unit and stop the buzzer
    """
    # Create the data to be sent
    send_data = struct.pack(
        '>2ssxH',           # format
        PNS_PRODUCT_ID,     # Product Category (AB)
        PNS_CLEAR_COMMAND,  # Command identifier (C)
        0,                  # Data size
    )

    # Send PNS command
    recv_data = send_command(send_data)

    # check the response data
    if recv_data[0] == PNS_NAK:
        raise ValueError('negative acknowledge')


def pns_get_data_command() -> 'PnsStatusData':
    """
    Send status acquisition command for PNS command

    LED unit and buzzer status can be acquired

    Returns
    -------
    status_data: PnsStatusData
        Received data of status acquisition command (status of LED unit and buzzer)
    """
    # Create the data to be sent
    send_data = struct.pack(
        '>2ssxH',               # format
        PNS_PRODUCT_ID,         # Product Category (AB)
        PNS_GET_DATA_COMMAND,   # Command identifier (G)
        0,                      # Data size
    )

    # Send PNS command
    recv_data = send_command(send_data)

    # check the response data
    if recv_data[0] == PNS_NAK:
        raise ValueError('negative acknowledge')

    status_data = PnsStatusData(recv_data)

    return status_data


if __name__ == '__main__':
    main()
