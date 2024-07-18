"""
`Target` class wrapper that has some knowledge of terminal based gui.
It is also more verbose.
"""

from ..term.selectable import Selectable
from ..arduino.target import Target
from ..utils.result import Ok, Err
from queue import Queue
from typing import Any
import binascii


class TargetGUI(Target):
    """
    `Target` subclass with some wrapper methods to use as callback in the GUI.
    It logs a lot of results, for user feedback.
    """

    def toggle_led(self, parent: Selectable, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Toggles the led on the target.
        """
        if self.instrument.is_open:
            cmd = self.set_led_on() if parent.is_toggled(
            ) else self.set_led_off()
            match cmd:
                case Ok(None):
                    self._log.info(
                        "Led ON" if parent.is_toggled() else "Led OFF")
                case Err(e):
                    self._log.error(e)
        else:
            self._log.error("Serial com with target is not open.")

    def set_asmcode_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target to start skip instruction campaign test function.
        """
        match super().set_asmcode():
            case Ok(None):
                self._log.info("asmcode() launched.")
            case Err(e):
                self._log.error(e)

    def get_regs_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target for the result of the skip instruction campaign test
        function.
        """
        match super().get_regs():
            case Ok(regs):
                self._log.info(regs)
            case Err(e):
                self._log.error(e)

    def set_user_pin_gui(self, _: Queue, user_inputs: dict[str, Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Sends a new user pin to the target.
        """
        pin = user_inputs.get("pin", 0)
        match super().set_user_pin(pin):
            case Ok(None):
                self._log.info(f"User PIN set to {pin}.")
            case Err(e):
                self._log.error(e)

    def get_user_pin_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target for the current user pin.
        """
        match super().get_user_pin():
            case Ok(pin):
                self._log.info(f"User PIN: {pin}")
            case Err(e):
                self._log.error(e)

    def verifypin_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target to verify the user pin against the admin pin (with the
        normal verify function).
        """
        match super().verifypin():
            case Ok(status):
                self._log.info("Status is %s.", "ADMIN" if status else "USER")
            case Err(e):
                self._log.error(e)

    def verifypinasm_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target to verify the user pin against the admin pin (with the
        verify function written in assembly code).
        """
        match super().verifypinasm():
            case Ok(status):
                self._log.info("Status is %s.", "ADMIN" if status else "USER")
            case Err(e):
                self._log.error(e)

    def verifypinhardened_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target to verify the user pin against the admin pin (with the
        verify function written in assembly code with some counter-measures).
        """
        match super().verifypinhard():
            case Ok(status):
                self._log.info("Status is %s.", "ADMIN" if status else "USER")
            case Err(e):
                self._log.error(e)

    def set_noadmin_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target to disconnect from admin mode.
        """
        match super().set_noadmin():
            case Ok(None):
                self._log.info("Forced to USER mode")
            case Err(e):
                self._log.error(e)

    def set_admin_pin_gui(self, _: Queue, user_inputs: dict[str, Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Sends a new admin pin to the target: need to be in admin mode for
        anything to happen.
        """
        pin = user_inputs.get("pin", 0)
        match super().setadminpin(pin):
            case Ok(None):
                self._log.info(f"Admin PIN set to {pin}.")
            case Err(e):
                self._log.error(e)

    def verifypinstatus_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target to send the max failed attempts protection counter as
        well as the admin/user status.
        """
        match super().verifypinstatus():
            case Ok((ptc, authenticated)):
                self._log.info(
                    f"g_ptc: {ptc}, g_authenticated: {authenticated}")
            case Err(e):
                self._log.error(e)

    def set_g_ptc_3_gui(self, _: Queue) -> None:
        """
        Method designed to be a button callback in the GUI.
        Asks the target to reset the max failed auth. attempts counter to 3
        (attack cooperation function). Used in the verify pin campaign.
        """
        match super().set_g_ptc_3():
            case Ok(None):
                self._log.info("g_ptc set to 3.")
            case Err(e):
                self._log.error(e)

    def encrypt_aes128_gui(self, _: Queue, user_inputs: dict[str,
                                                             Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Sends a plain text to the target to be encrypted with AES128. The
        returned cipher is then logged.
        (ex: 3243f6a8885a308d313198a2e0370734)
        """
        plain_hex = user_inputs.get("plain",
                                    "3243f6a8885a308d313198a2e0370734")
        try:
            plain = binascii.unhexlify(plain_hex)
        except binascii.Error as e:
            self._log.error(e)
            return
        match super().encrypt_aes128(plain):
            case Ok(cipher):
                try:
                    cipher = binascii.hexlify(cipher).decode("utf-8")
                    self._log.info(f"Encrypted {plain_hex}")
                    self._log.info(f"=> ⍰ {cipher} ⍰")
                except binascii.Error as e:
                    self._log.error(e)
            case Err(e):
                self._log.error(e)

    def key_aes128_gui(self, _: Queue, user_inputs: dict[str, Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Sends a new key to the target to be used in the AES128 encryption.
        (ex: 2b7e151628aed2a6abf7158809cf4f3c)
        """
        key = user_inputs.get("key", "2b7e151628aed2a6abf7158809cf4f3c")
        try:
            key = binascii.unhexlify(key)
        except binascii.Error as e:
            self._log.error(e)
            return
        match super().key_aes128(key):
            case Ok(None):
                try:
                    key = binascii.hexlify(key).decode("utf-8")
                    self._log.info(f"⚿ Key set to {key} ⚿")
                except binascii.Error as e:
                    self._log.error(e)
            case Err(e):
                self._log.error(e)
