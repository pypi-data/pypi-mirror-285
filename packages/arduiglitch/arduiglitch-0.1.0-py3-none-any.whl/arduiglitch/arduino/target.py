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

Child class of Base that handles the communication with the target
Arduino.
"""

import binascii
from .com_base import ComBase
from ..utils.result import Result, Ok, Err
from ..utils.logger import Log


class Target(ComBase):
    """
    Class that handles communication with the Arduino board on which errors
    are injected.
    """

    def __init__(self,
                 log: Log,
                 url: str,
                 baudrate: int = 9600,
                 timeout_s: float = 0.5):
        """
        Args:
            log: log object to use for console logging
            port: com port to use (ex: "COMx" ,"/dev/ttyACMx", "/dev/ttyUSBx" or
                "hwgrep://2341:0043")
            baudrate: baudrate to use, usually 9600 or 115200
            timeout_s: serial com timeout in seconds

        Example:
            .. code-block:: python

                from arduiglitch import Target
                from arduiglitch import Log
                from logging import DEBUG

                log = Log(__name__, level=DEBUG)
                target = Target(log, "hwgrep://2341:0043")
                target.strict_open_instrument()
                # ...
                target.close_instrument()
        """
        super().__init__(log, url, baudrate, timeout_s)
        self._led_state: bool = False

    def set_led_on(self) -> Result[None]:
        """
        Set user LED on.
        """
        self._safe_instrument_reset_input_buffer()
        match self._safe_write_then_readline("H"):
            case Ok("OK\r\n"):
                self._led_state = True
                return Ok(None)
            case Ok(answer):
                return Err(
                    Exception(f"Unexpected response from Arduino: {answer}."))
            case err:
                return err

    def set_led_off(self) -> Result[None]:
        """
        Set user LED off.
        """
        self._safe_instrument_reset_input_buffer()
        match self._safe_write_then_readline("L"):
            case Ok("OK\r\n"):
                self._led_state = False
                return Ok(None)
            case Ok(answer):
                return Err(
                    Exception(f"Unexpected response from Arduino: {answer}."))
            case err:
                return err

    def toggle_led(self) -> Result[None]:
        """
        Toggle user LED on or off.
        """
        if self._led_state:
            return self.set_led_off()
        else:
            return self.set_led_on()

    def set_asmcode(self) -> Result[None]:
        """
        Start a series of 10 LDI assembler instructions.
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("A"):
                    case Ok("OK\r\n"):
                        return Ok(None)
                    case Ok(answer):
                        return Err(
                            Exception(
                                f"Received something else than OK: {answer}"))
                    case err:
                        return err
            case err:
                return err

    def get_regs(self) -> Result[list[int]]:
        """
        Read the 10 registers R16 to R25 from the SRAM.

        :return: something like this if the communication worked :
            `Ok([0x39, 0x38, 0x37, 0x36, 0x35, 0x34, 0x33, ..., 0x30])`
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("Z"):
                    case Ok(regs_str):
                        # received `regs_str` format should be :
                        # "0x39 0x38 0x37 0x36 0x35 0x34 0x33 0x32 0x31 0x30"
                        regs_str = regs_str.rstrip()
                        try:
                            regs = list(
                                map(lambda x: int(x, 0), regs_str.split(" ")))
                        except ValueError:
                            return Err(
                                Exception(
                                    f"Could not parse received regs: {regs_str}"
                                ))

                        if len(regs) != 10:
                            return Err(
                                Exception(
                                    f"Received less/more than 10 regs: {regs}")
                            )
                        else:
                            return Ok(regs)
                    case err:
                        return err
            case err:
                return err

    def set_user_pin(self, pin: int) -> Result[None]:
        """
        Set the PIN code entered by the user.

        Args:
            pin: the 4 digits PIN code
        """
        # clamp pin to 4 digits
        pin = min(9999, max(0, pin))

        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("P" + str(pin).zfill(4),
                                                     sleep_before_read_s=0.1):
                    case Ok("OK\r\n"):
                        return Ok(None)
                    case Ok(answer):
                        return Err(
                            Exception(
                                f"Received something else than OK: {answer}"))
                    case err:
                        return err
            case err:
                return err

    def get_user_pin(self) -> Result[int]:
        """
        Get the PIN code entered by the user [0;9999].
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_read("R", nb_bytes=4):
                    case Ok(pin_str):
                        self._log.warning(pin_str)
                        return Ok(min(9999, max(0, int(pin_str))))
                    case err:
                        return err
            case err:
                return err

    def verifypin(self) -> Result[bool]:
        """
        Verify the PIN code entered by the user.

        Returns:
            answer from Arduino (True(0xAA) (successful attack) or
            False(0x55) (no double fault))
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("V"):
                    case Ok(status_str):
                        status_str = status_str.rstrip()
                        try:
                            return Ok(int(status_str, 0) == 0xAA)
                        except ValueError:
                            return Err(
                                Exception(
                                    f"Could not parse received status: {status_str}"
                                ))
                    case err:
                        return err
            case err:
                return err

    def verifypinasm(self) -> Result[bool]:
        """
        Verify the PIN code entered by the user by making use of the assembly routine.

        :return: answer from Arduino (True(0xAA) (successful attack) or
            False(0x55) (no double fault))
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("W"):
                    case Ok(status_str):
                        status_str = status_str.rstrip()
                        try:
                            return Ok(int(status_str, 0) == 0xAA)
                        except ValueError:
                            return Err(
                                Exception(
                                    f"Could not parse received status: {status_str}"
                                ))
                    case err:
                        return err
            case err:
                return err

    def verifypinhard(self) -> Result[bool]:
        """
        Verify the PIN code entered by the user by making use of the hardened
        routine.

        Returns:
            answer from Arduino (True(0xAA) (successful attack) or
            False(0x55) (no double fault))
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("X"):
                    case Ok(status_str):
                        status_str = status_str.rstrip()
                        try:
                            return Ok(int(status_str, 0) == 0xAA)
                        except ValueError:
                            return Err(
                                Exception(
                                    f"Could not parse received status: {status_str}"
                                ))
                    case err:
                        return err
            case err:
                return err

    def verifypinstatus(self) -> Result[tuple[int, bool]]:
        """
        Verify the PIN code status.

        Returns:
            tuple of g_ptc and status (True -> Logged as admin, False ->
            Logged as user)
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write("S"):
                    case Ok(_):
                        # Read two consecutive lines
                        match self._safe_readline(), self._safe_readline():
                            case Ok(line1), Ok(line2):
                                line1 = line1.rstrip()
                                line2 = line2.rstrip()
                                try:
                                    return Ok((int(line1, 0), int(line2,
                                                                  0) == 0xAA))
                                except ValueError:
                                    return Err(
                                        Exception(
                                            f"Could not parse received status:{line1=};{line2=}"
                                        ))
                            case Err(err), _:
                                return Err(err)
                            case _, Err(err):
                                return Err(err)
                            case _:
                                raise AssertionError(
                                    "Impossible case in verifypinstatus")
                    case err:
                        return err
            case err:
                return err

    def set_g_ptc_3(self) -> Result[None]:
        """
        Set the maximum number of tries to enter a correct PIN code to 3.
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("3"):
                    case Ok("OK\r\n"):
                        return Ok(None)
                    case Ok(answer):
                        return Err(
                            Exception(
                                f"Received something else than OK: {answer}"))
                    case err:
                        return err
            case err:
                return err

    def set_noadmin(self) -> Result[None]:
        """
        Close the admin session.
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_read("C"):
                    case Ok("OK\r\n"):
                        return Ok(None)
                    case Ok(answer):
                        return Err(
                            Exception(
                                f"Received something else than OK: {answer}"))
                    case err:
                        return err
            case err:
                return err

    def setadminpin(self, pin: int) -> Result[None]:
        """
        Changes the admin PIN code in SRAM. Requires admin authentication first.
        Returns Ok(False) if the communication worked, but admin PIN write acces
        was denied, else Ok(True).

        Args:
            pin: 4 digits PIN to force set as admin PIN
        """
        pin = min(9999, max(0, pin))  # clamp pin to 4 digits

        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("N" + str(pin).zfill(4),
                                                     sleep_before_read_s=0.1):
                    case Ok("OK\r\n"):
                        return Ok(None)
                    case Ok(answer):
                        return Err(
                            Exception(f"Invalid PIN or not admin: {answer}"))
                    case err:
                        return err
            case err:
                return err

    def duplicate_regs_simu(self) -> Result[bool]:
        """
        Starts the duplicate register simulation function on the target.
        By default, the glitcher is setup to do single glitch attacks. It is
        required to go into double glitch mode by using the corresponding
        method of the glitcher class.

        Returns:
            answer from Arduino (True(0xAA) (successful attack) or False(0x55)
            (no double fault))
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("O", 0.2):
                    case Ok(line):
                        line = line.rstrip()
                        try:
                            return Ok(int(line, 0) == 0xAA)
                        except ValueError:
                            return Err(
                                Exception(
                                    f"Could not parse received status: {line}")
                            )
                    case err:
                        return err
            case err:
                return err

    def instruction_merge(self) -> Result[int]:
        """
        Starts the instruction merge function that executes a SWAP function followed by a NEG on r18.
        If SWAP r18 and NEG r18 are merged, the resulting instruction is INC r18.

        Returns:
            answer from Arduino: content of r18 after the attack. Expects
            46, 55, AB or BB
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_readline("m", 0.2):
                    case Ok(line):
                        line = line.rstrip()
                        try:
                            return Ok(int(line, 0))
                        except ValueError:
                            return Err(
                                Exception(
                                    f"Could not parse received value: {line}"))
                    case err:
                        return err
            case err:
                return err

    def encrypt_aes128(self, plain_text: bytes) -> Result[bytes]:
        """
        Perform AES encryption.

        Args:
            plain_text: the plain text to be encrypted (as bytes `plain_text`
                should look like b"0123456789ABCDEF")
        """
        if len(plain_text) != 16:
            return Err(Exception("Plain text must be 16 bytes long"))
        else:
            match self._safe_instrument_reset_input_buffer():
                case Ok(_):
                    cmd: bytes = binascii.unhexlify(hex(ord("E"))[2:].encode())
                    match self._safe_bytes_write_then_bytes_read(
                            cmd + plain_text, nb_bytes=16,
                            sleep_before_read_s=0.1):
                        case Ok(cipher):
                            if len(cipher) != 16:
                                len_cipher = len(cipher)
                                return Err(
                                    Exception(
                                        f"Received cipher was not 16 bytes long, was {len_cipher} bytes long."
                                    ))
                            else:
                                return Ok(cipher)
                        case Err(err):
                            err.args = (
                                f"Encrypting: {cmd + binascii.hexlify(plain_text)}",
                            ) + err.args
                            return Err(err)
                case err:
                    return err

    def key_aes128(self, key: bytes) -> Result[None]:
        """
        AES128 key + derivation of rounding keys.
        Must be authentificated as admin on target Arduino!
        Will be ignored otherwise.

        Args:
            key: the new AES128 key
        """
        if len(key) != 16:
            return Err(Exception("Key must be 16 characters long"))
        else:
            match self._safe_instrument_reset_input_buffer():
                case Ok(_):
                    cmd: bytes = binascii.unhexlify(hex(ord("K"))[2:].encode())
                    match self._safe_bytes_write_then_read(
                            cmd + key, sleep_before_read_s=0.2):
                        case Ok("OK\r\n"):
                            return Ok(None)
                        case Ok(answer):
                            return Err(
                                Exception(
                                    f"Received something else than OK. Are you admin?: {answer}"
                                ))
                        case err:
                            return err
                case err:
                    return err

    def sbox(self) -> Result[bytes]:
        """
        Ask Arduino to send it's SBOX.
        ("0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, ... , 0xb0, 0x54, 0xbb, 0x16")

        Returns:
            SBOX sent back by Arduino
        """
        match self._safe_instrument_reset_input_buffer():
            case Ok(_):
                match self._safe_write_then_bytes_read(
                        "B", nb_bytes=256, sleep_before_read_s=0.1):
                    case Ok(sbox_b):
                        if len(sbox_b) != 16 * 16:
                            return Err(
                                Exception(
                                    "Received SBOX was not 16*16 bytes long"))
                        else:
                            return Ok(sbox_b)
                    case err:
                        return err
            case err:
                return err
