import os
from .utils import create_logger


class Bus():
    
    def __init__(self, max_memory=0xFFFF, num_of_banks= 1, log_folder="", debug=True):
        """Initialize Bus Class

        Args:
            max_memory (int, optional): Max memory per bank. Defaults to 0xFFFF.
            num_of_banks (int, optional): Number of banks to setup for the bus to reference. Defaults to 1.
            log_folder (str, optional): Relative path to log folder. Defaults to "".
            debug (bool, optional): Should debug information be collected? Defaults to True.

        Raises:
            ValueError: Raises error if max_memory is beyond 0XFFFF, which is the capability limit for 6502 microprocessor
            ValueError: Raises error if number of banks is negative
            ValueError: Raises error if number of banks is greater than 256
        """
        if log_folder == "":
            _script_path, _dump = os.path.split(os.path.realpath(__file__))
            _log_dir_path = os.path.join(_script_path, "./log")
        else:
            _log_dir_path = log_folder

        if not (os.path.exists(_log_dir_path)):
            os.mkdir(_log_dir_path)

        self._debug = debug
        self._log_file = os.path.join(_log_dir_path, "bus.log")
        self._logger = create_logger("Bus-16", self._log_file) 

        if max_memory > 0xFFFF:
            if self._debug:
                self._logger.error(f"{max_memory:#012X} value is beyond 16-bit (0XFFFF), beyond capability of 6502")
            raise ValueError(f"{max_memory:#012X} value is beyond 16-bit (0XFFFF), beyond capability of 6502")
        elif num_of_banks < 1:
            if self._debug:
                self._logger.error(f"Cannot have negative number of banks ({num_of_banks:#012X})")
            raise ValueError(f"Cannot have negative number of banks ({num_of_banks:#012X})")
        elif num_of_banks > 256:
            if self._debug:
                self._logger.error(f"Does not support more than 256 banks ({num_of_banks:#012X})")
            raise ValueError(f"Does not support more than 256 banks ({num_of_banks:#012X})")
        else:
            self._num_of_banks = num_of_banks
            self._max_memory = max_memory         
            self._memory = [[0xFF for x in range(self._max_memory)] for y in range(self._num_of_banks)]
            if self._debug:
                self._logger.info("Successfully initialized the Bus")

    def read(self, addr, bank=1):
        """Read at address from memory bank

        Args:
            addr (hex): Memory address in a memory bank
            bank (int, optional): Bank number from which to read address. Defaults to 1.

        Raises:
            ValueError: Raises error if bank id is less than 0 or greater than 256
            ValueError: Raises error if memory address is beyond max memory of each bank

        Returns:
            hex: Value stored at address `addr` and bank `bank`
        """
        if bank < 1 or bank > 256:  # number of banks cannot be less than 0
            if self._debug:
                self._logger.error(f"Bank id ({bank}) is not valid")

            raise ValueError(f"Bank id ({bank}) is not valid")
        
        if addr > self._max_memory:
            if self._debug:
                self._logger.error(f"Address ({addr:#010X}) cannot be more than {self._max_memory}")
            raise ValueError(f"Address ({addr:#010X}) cannot be more than {self._max_memory}")
        elif addr < 0:
            if self._debug:
                self._logger.error(f"Address ({addr:#010X}) cannot be negative")
            raise ValueError(f"Address ({addr:#010X}) cannot be negative")
        else:
            if self._debug:
                self._logger.info(f"Reading bus at {addr:#06X}, returning {self._memory[bank - 1][addr]}")

        return self._memory[bank - 1][addr]

    def write(self,val, addr, bank=1):
        """Write value to address in memory bank

        Args:
            val (hex): Value that needs to be stored [0X00 - 0XFF]
            addr (hex): Address to where value needs to be stored in memory bank            
            bank (int, optional): Bank number to which value has to be written to at address. Defaults to 1.

        Raises:
            ValueError: Raises error if bank id is less than 0
            ValueError: Raises error if memory address is beyond max memory of each bank
        """
        if bank < 1 or bank > 256:  # number of banks cannot be less than 0
            if self._debug:
                self._logger.error(f"Bank id ({bank}) is not valid")

            raise ValueError(f"Bank id ({bank}) is not valid")
        
        if addr > self._max_memory:
            if self._debug:
                self._logger.error(f"Address ({addr:#010X}) cannot be more than {self._max_memory}")
            raise ValueError(f"Address ({addr:#010X}) cannot be more than {self._max_memory}")
        elif addr < 0:
            if self._debug:
                self._logger.error(f"Address ({addr:#010X}) cannot be negative")
            raise ValueError(f"Address ({addr:#010X}) cannot be negative")
        else:
            if self._debug:
                self._logger.info(f"Writing value {val:#04X} to bus at {addr:#06X}")

            self._memory[bank - 1][addr] = val