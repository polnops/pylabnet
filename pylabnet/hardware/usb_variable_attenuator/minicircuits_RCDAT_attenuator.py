import ctypes

from pylabnet.utils.logging.logger import LogHandler


class Driver():
    """ Hardware class to control RCDAT type USB attenuator."""

    def __init__(self, serial_nm, logger=None):
        """ Instantiate USB attenuator (Minicircuits)

        :param logger: instance of LogClient class (optional)
        """

        # Log
        self.log = LogHandler(logger=logger)

        # Load WLM DLL
        try:
            self._dll = ctypes.windll.LoadLibrary('C:\\Users\\User\\pylabnet\\pylabnet\\hardware\\usb_variable_attenuator\\mcl_RUDAT64.dll')

        except:
            msg_str = 'Minicircuits RCDAT driver is not properly installed on this computer'
            self.log.error(msg_str)
            raise Error(msg_str)

        # Set all DLL function parameters and return value types

        self._serial_nm = serial_nm
        # Check that WLM is running and log details
        self._is_running = self._connect_to_device()
        if self._is_running > 0:
            self.log.info(
                'Connected to USB Attenuator-{0}'.format(serial_nm)
            )
        else:
            msg_str = 'Could not connect to USB Attenuator-{0}'.format(serial_nm)
            self.log.warn(msg_str)

    def set_attenuation(self, attenuation):
        """ Returns the wavelength in specified units for a given channel

        :param channel: Channel number from 1-8
        :param units: "Frequency (THz)" or "Wavelength (nm)". Defaults to frequency.
        """
        self._connect_to_device()
        result = self._dll.SetAttenuation(attenuation)
        if result > 0:
            self.log.info()
        if units == 'Wavelength (nm)':
            return self._wavemeterdll.GetWavelengthNum(channel, 0)

        else:
            return self._wavemeterdll.GetFrequencyNum(channel, 0)

    def get_attenuation(self):
        self._connect_to_device()
        (result, attenuation) = self._dll.ReadAttenuation(attenuation)
        return attenuation

    def _connect_to_device(self):
        (result, serial_number) = self._dll.Read_SN('')
        if (result == 0 or serial_number != self._serial_nm):
            #Either we are not connected to any attenuator or are ocnnected to the wrong attenuator
            if (result == 0): #Disconnect from old device if connected to the wrong device  `
                self._dll.Disconnect()
            return self._dll.Connect(self._serial_nm)
        return 1 #Otherwise we are connected and are good to go

    def __del__(self):
        #Destructor to close connection if this object is deleted
        (result, serial_number) = self._dll.Read_SN('')
        if (result != 0 and serial_number == self._serial_nm):
            #Disconnect from this device if we are currently connected to this device
            self._dll.Disconnect()

def main():
    driver = Driver('12006020010')


if __name__ == '__main__':
    main()