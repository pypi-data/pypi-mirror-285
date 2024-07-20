import serial

class LaserSerial:
    def __init__(self, port='COM6', baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False, dsrdtr=False, timeout=2):
        self.ser = serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, xonxoff=xonxoff, rtscts=rtscts, dsrdtr=dsrdtr, timeout=timeout)

    def calcBIP4(self, data):
        bip8 = (data[0] & 0x0f) ^ data[1] ^ data[2] ^ data[3]
        bip4 = ((bip8 & 0xf0) >> 4) ^ (bip8 & 0x0f)
        return bip4

    def convertCommand(self, data):
        BIP4 = self.calcBIP4(data)
        commandArray = bytearray(data)
        commandArray[0] |= BIP4 << 4
        return bytes(commandArray)

    def sendCommand(self, data):
        command = self.convertCommand(data)
        self.ser.write(command)

    def checkResponse(self):
        response = self.ser.read(4)
        response_first_4_bits = format(response[0], '08b')[:4]
        bip4_result = format(self.calcBIP4(response), '04b')
        if response_first_4_bits == bip4_result:
            return True
        else:
            return False
    
    def closeSerial(self):
        self.ser.close()

    def send_starting_frequency(self, starting_frequency):
        # Calculate the value to send to the module
        value = 196251 - starting_frequency

        # Convert the value to bytes
        value_bytes = value.to_bytes(2, 'big')

        # Construct the command to send
        self.sendCommand(bytes([0x01, 0x93]) + value_bytes)

        return self.checkResponse()
	
    def send_scan_step(self, scan_step):
        # Convert the scan step to bytes
        scan_step_bytes = scan_step.to_bytes(2, 'big')

        # Construct the command to send
        self.sendCommand(bytes([0x01, 0x94]) + scan_step_bytes)

        return self.checkResponse()

    def send_stop_frequency(self, stop_frequency):
        # Calculate the value to send to the module
        value = 196251 - stop_frequency

        # Convert the value to bytes
        value_bytes = value.to_bytes(2, 'big')

        # Construct the command to send
        self.sendCommand(bytes([0x01, 0x95]) + value_bytes)

        return self.checkResponse()

    def send_scan_speed(self, scan_speed):
        # Convert the scan speed to bytes
        scan_speed_bytes = scan_speed.to_bytes(2, 'big')

        # Construct the command to send
        self.sendCommand(bytes([0x01, 0x96]) + scan_speed_bytes)

        return self.checkResponse()

    def send_scan_control_command(self, command):
        
        self.sendCommand(bytes([0x01, 0xA4, 0x00, command]))

        return self.checkResponse()
    
    def read_serial_number(self):
        self.sendCommand(bytes([0x00, 0xc1, 0x00, 0x00]))

        response = self.ser.read(4)

        serial_number = (response[2] << 24) | (response[3] << 16) | (response[0] << 8) | response[1]

        return serial_number
    
    def read_firmware_version(self):
        self.sendCommand(bytes([0x00, 0xc3, 0x00, 0x01]))

        response = self.ser.read(4)

        firmware_version = (response[2] << 8) | response[3]

        return firmware_version
    