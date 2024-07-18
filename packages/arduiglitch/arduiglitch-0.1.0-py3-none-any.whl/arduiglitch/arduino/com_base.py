"""
Arduiglitch - voltage glitch training on an ATMega328P
Copyright (C) 2024  Hugo PERRIN (h.perrin@emse.fr)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Base class to create an Arduino serial communication object.
"""

from abc import ABC
import time
import serial
from ..utils.logger import Log
from ..utils.result import Result, Ok, Err


class ComBase(ABC):
    """
    Base class to create an Arduino serial communication object.
    Contains private methods to write to or read from serial com.
    """

    def __init__(self,
                 log: Log,
                 url: str,
                 baudrate: int = 9600,
                 timeout_s: float = 0.5):
        """
        Args:
            log: log object to use for console logging.
            port: com port to use (ex: "COMx" ,"/dev/ttyACMx", "/dev/ttyUSBx" or
                "hwgrep://2341:0043")
            baudrate: baudrate to use, usually 9600 or 115200
            timeout_s: serial com timeout in seconds
        """
        self._log = log

        self.port = url
        self.baud_rate = baudrate
        self.bytesize = "EIGHTBITS"
        self.stopbits = "STOPBITS_ONE"
        self.parity = "PARITY_NONE"
        self.timeout = timeout_s

        self.instrument: serial.Serial = serial.Serial()

    def open_instrument(self) -> Result[None]:
        """
        Opens the instrument from the specified url.
        """
        kwargs = {
            "url": self.port,
            "baudrate": self.baud_rate,
            "bytesize": getattr(serial, self.bytesize),
            "stopbits": getattr(serial, self.stopbits),
            "parity": getattr(serial, self.parity),
            "timeout": self.timeout
        }

        class_name = self.__class__.__name__
        port = self.port

        if self.instrument.is_open:
            self._log.debug(f"Port `{port}` is already open for {class_name}")
            return Ok(None)
        else:
            self._log.debug(f"Opening port for {class_name}: `{port}`")
            try:
                self.instrument = serial.serial_for_url(**kwargs)
                time.sleep(0.5)
                self._log.debug(f"...Serial port is open: `{port}`")
                return Ok(None)
            except serial.SerialException as err:
                self._log.debug(f"ERROR : Could not open serial port: {port}")
                return Err(err)

    def strict_open_instrument(self) -> Result[None]:
        """
        Opens the instrument. Crashes the program if it could not be opened.
        """
        match self.open_instrument():
            case Ok(_):
                return Ok(None)
            case _:
                class_name = self.__class__.__name__
                raise RuntimeError(
                    f"Strict open instrument failed for {class_name}")

    def close_instrument(self):
        if self.instrument.is_open:
            self.instrument.close()

    def __del__(self):
        self.close_instrument()

    def _safe_bytes_write(self, cmd: bytes) -> Result[int | None]:
        try:
            return Ok(self.instrument.write(cmd))
        except (serial.SerialException, serial.SerialTimeoutException) as err:
            return Err(err)

    def _safe_write(self, cmd: str) -> Result[int | None]:
        try:
            return self._safe_bytes_write(cmd.encode())
        except (UnicodeEncodeError) as err:
            return Err(err)

    def _safe_bytes_read(self, nb_bytes=100) -> Result[bytes]:
        try:
            answer = self.instrument.read(nb_bytes)
            if len(answer) == 0:
                return Err(
                    Exception(
                        f"Instrument read timed out; Out of the {nb_bytes} bytes expected, only received: {answer}"
                    ))
            else:
                return Ok(answer)
        except serial.SerialException as err:
            return Err(err)

    def _safe_read(self, nb_bytes=100) -> Result[str]:
        match self._safe_bytes_read(nb_bytes):
            case Ok(result_bytes):
                try:
                    return Ok(result_bytes.decode())
                except UnicodeDecodeError as err:
                    return Err(err)
            case err:
                return err

    def _safe_write_then_read(self,
                              cmd: str,
                              nb_bytes: int = 100,
                              sleep_before_read_s: float = 0.0) -> Result[str]:
        """
        Writes the command to the serial port and then reads a max of
        `nb_bytes` chars of answer.
        Returns a Result type alias to propagate errors.

        Args:
            cmd: command to write to the serial port
            nb_bytes: max number of bytes to read from the serial port
            sleep_before_read_s: number of seconds to wait before
                reading an answer from the serial port
        """
        match self._safe_write(cmd):
            case Ok(_):
                time.sleep(sleep_before_read_s)
                return self._safe_read(nb_bytes)
            case err:
                return err

    def _safe_write_then_bytes_read(
            self,
            cmd: str,
            nb_bytes: int = 100,
            sleep_before_read_s: float = 0.0) -> Result[bytes]:
        """
        Writes the command to the serial port and then reads a max of
        `nb_bytes` chars of answer.
        Returns a Result type alias to propagate errors.

        Args:
            cmd: command to write to the serial port
            nb_bytes: max number of bytes to read from the serial port
            sleep_before_read_s: number of seconds to wait before
                reading an answer from the serial port
        """
        match self._safe_write(cmd):
            case Ok(_):
                time.sleep(sleep_before_read_s)
                return self._safe_bytes_read(nb_bytes)
            case err:
                return err

    def _safe_bytes_write_then_read(
            self,
            cmd: bytes,
            nb_bytes: int = 100,
            sleep_before_read_s: float = 0.0) -> Result[str]:
        """
        Writes the command to the serial port and then reads a max of
        `nb_bytes` chars of answer.
        Returns a Result type alias to propagate errors.

        Args:
            cmd: command to write to the serial port.
            nb_bytes: max number of bytes to read from the serial port.
            sleep_before_read_s: number of seconds to wait before
                reading an answer from the serial port.
        """
        match self._safe_bytes_write(cmd):
            case Ok(_):
                time.sleep(sleep_before_read_s)
                return self._safe_read(nb_bytes)
            case err:
                return err

    def _safe_bytes_write_then_bytes_read(
            self,
            cmd: bytes,
            nb_bytes: int = 100,
            sleep_before_read_s: float = 0.0) -> Result[bytes]:
        """
        Writes the command to the serial port and then reads a max of
        `nb_bytes` chars of answer.
        Returns a Result type alias to propagate errors.

        Args:
            cmd: command to write to the serial port
            nb_bytes: max number of bytes to read from the serial port
            sleep_before_read_s: number of seconds to wait before
                reading an answer from the serial port
        """
        match self._safe_bytes_write(cmd):
            case Ok(_):
                time.sleep(sleep_before_read_s)
                return self._safe_bytes_read(nb_bytes)
            case err:
                return err

    def _safe_write_then_readline(self,
                                  cmd: str,
                                  sleep_before_read_s: float = 0.0
                                  ) -> Result[str]:
        """
        Writes the command to the serial port and then reads the line answered.
        Return a Result type alias to propagate errors.

        Args:
            cmd: command to write to the serial port
            sleep_before_read_s: number of seconds to wait before
                reading an answer from the serial port
        """
        match self._safe_write(cmd):
            case Ok(_):
                time.sleep(sleep_before_read_s)
                return self._safe_readline()
            case err:
                return err

    def _safe_readline(self) -> Result[str]:
        """
        Reads and decodes a line from the instrument. Catches serial
        exceptions in the returned Result.
        """
        try:
            line = self.instrument.readline()
            if len(line) == 0:
                return Err(Exception("Instrument read timed out."))
            else:
                return Ok(line.decode())
        except (serial.SerialException, UnicodeDecodeError) as err:
            return Err(err)

    def _safe_instrument_reset_input_buffer(self) -> Result[None]:
        """
        Resets the input buffer of the instrument. Catches serial
        exceptions in the returned Result.
        """
        try:
            self.instrument.reset_input_buffer()
            return Ok(None)
        except serial.SerialException:
            return Err(Exception("Instrument is not open"))
