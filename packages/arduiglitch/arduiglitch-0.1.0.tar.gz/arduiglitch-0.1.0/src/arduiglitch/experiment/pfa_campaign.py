"""
This class should be instanciated in the callback that runs a fault
injection campaign. `Target` and `Glitcher` do not need to be already
opened before `__init__`.
"""
from ..arduino.target import Target
from ..arduino.glitcher import Glitcher
from ..utils.logger import Log
from ..utils.result import Ok, Err, Result
from ..experiment.campaign import Campaign
from ..utils.pfa_utils import PfaUtils
from queue import Queue
from time import sleep, gmtime, strftime
import binascii
from typing import Any
import numpy as np
import os


class PfaCampaign(Campaign):
    """
    This class should be instanciated in the callback that runs a fault
    injection campaign. `Target` and `Glitcher` do not need to be already
    opened before `__init__`.
    """

    def __init__(
        self,
        log: Log,
        glitcher: Glitcher,
        target: Target,
        csv_filename: str,
        batch_size: int,
    ):
        # `Queue()` needs to be overriden by the caller before running.
        super().__init__(log, glitcher, target, csv_filename, Queue())

        # needs to be initialized with `set_delay_sweep` before running.
        self._min_delay: int = 0
        self._max_delay: int = 0
        self._step_delay: int = 1

        self._batch_size: int = batch_size

        self._template_row: dict[str, Any] = {
            "time": 0,
            "min_delay": self._min_delay,
            "max_delay": self._max_delay,
            "step_delay": self._step_delay,
            "keys": 0,
            "delay": 0,
        }

        self._healthy_pairs: list[tuple[bytes, bytes]] = []
        self._pfa = PfaUtils()

    def generate_pairs(self, length: int) -> list[tuple[bytes, bytes]]:
        pairs: list[tuple[bytes, bytes]] = []

        for _ in range(length):
            plaintext = os.urandom(16)
            match self._target.encrypt_aes128(plaintext):
                case Ok(ciphertext):
                    pairs.append((plaintext, ciphertext))
                case Err(err):
                    self._log.error(
                        f"Error while generating a healthy plain/cipher pairs: {err}"
                    )

        self._log.info(
            f"Successfully created {len(pairs)} healthy plain/cipher pairs.")
        return pairs

    def generate_healthy_pairs(self):
        # Open instruments if needed
        if self._target.open_instrument() != Ok(None):
            return
        if self._glitcher.open_instrument() != Ok(None):
            return
        # Generate 10 healthy plain/cipher pairs with the target
        self._healthy_pairs = self.generate_pairs(10)

    def set_queue(self, queue: Queue):
        self._queue = queue

    def set_delay_sweep(self, min_delay: int, max_delay: int, step_delay: int):
        """
        Sets the delay sweep parameters for the glitcher.
        """
        self._min_delay = min_delay
        self._max_delay = max_delay
        self._step_delay = step_delay
        self._template_row["min_delay"] = min_delay
        self._template_row["max_delay"] = max_delay
        self._template_row["step_delay"] = step_delay

    def run(self):
        """
        Run experiment loop. Logs an error and returns immediatly if the set of
        healthy plain/cipher pairs was not already generated on the target
        (with `generate_healthy_pairs` method).
        Opens communication with instruments if not already opened. Sweeps
        through delays specified during instance initialization.
        """
        if len(self._healthy_pairs) == 0:
            self._log.error(
                "You should generate a set of healthy plaintext/ciphertext pairs before injecting faults."
            )
        else:
            # Open instruments if not already
            self._target.open_instrument()
            self._glitcher.open_instrument()

            # Set glitcher cooldown to 100ms and reset target
            self.ensure_set_glitch_cooldown(100)
            self._glitcher.reset_target()
            sleep(0.8)

            # For this experiment we use the method glitch_after_reset(). On the Arduino, the associated
            # function uses the delay value as a number of microseconds to wait before the glitch.
            # Because of the huge start time jitter, sweeping accross multiple delays is useless.
            # Instead we only set one value and wait for a lucky jitter to enable the right fault to be injected.
            self.set_glitch_delay(self._min_delay)
            sleep(0.2)
            self._glitcher.set_no_glitch()

            # Delays to iterate the test on
            delays = list(
                range(self._min_delay, self._max_delay, self._step_delay))

            # Thread loop
            loop = True
            for _, delay in enumerate(delays):
                # Following control_queue read and handle must be in loop to be executed regularily
                loop = not Campaign.should_stop_thread(self._queue)
                # ====================================================================================================================
                # ================================================== EXPERIMENT ======================================================
                # In this experiment, the reset is the trigger signal
                self.set_glitch_delay(delay)
                sleep(0.2)

                for _ in range(5):
                    self._log.info(
                        f"Resetting the target to trigger the glitch (delay: {delay})..."
                    )
                    self._glitcher.glitch_after_reset()
                    sleep(0.3)

                    if self.cheat_verify_mono_byte_sbox_fault():
                        self._log.info(
                            f"Mono-byte fault detected (delay: {delay}).")
                        return None
                    # Attempts to detect error by comparing healthy plain/cipher pairs with newly encrypted ones
                    #match self.was_sbox_faulted():
                    #    case Ok(True):
                    #        # For the purpose of this Notebook, even though a SBOX fault was detected, we cheat
                    #        # by asking the target to send its SBOX to make sure that a correct mono-byte fault was
                    #        # injected before moving on to compute the key.
                    #        if self.cheat_verify_mono_byte_sbox_fault():
                    #            return None
                    if not loop:
                        break
                if not loop:
                    break
            if loop:
                # if the loop ended without being interrupted, the experiment
                # failed
                self._log.error("End of sweep, no SBOX error detected.")

    def was_sbox_faulted(self) -> Result[bool]:
        """
        The purpose of this method is to detect when the SBOX was successfully
        faulted. One way of doing this would be to directly ask the target what
        the SBOX stored in SRAM is, but it requires cooperation with the target
        which we'd like to avoid for this experiment.
        Thus this method makes the hypothesis that a cipher error implies a
        successful error on the SBOX storage in SRAM.

        :return: Ok(True) when the ref cipher and the received cipher do not
            match, Ok(False) if they all matched
        """

        # Set plaintext, encrypt and get cipher result
        for (plain, ref_cipher) in self._healthy_pairs:
            match self._target.encrypt_aes128(plain):
                case Ok(cipher):
                    # Check if cipher is different from reference cipher
                    if ref_cipher != cipher:
                        # Only one unmatching cipher is required to detect a faulted SBOX
                        self._log.debug(
                            "At least one test vector failed, assuming that SBOX was successfully faulted.\n"
                            + "ref_cipher = " +
                            str(binascii.hexlify(ref_cipher)) + "\n" +
                            "cipher     = " + str(binascii.hexlify(cipher)))
                        return Ok(True)
                case Err(err):
                    return Err(err)
        # If all test vectors passed, assume that SBOX was not faulted
        return Ok(False)

    def format_sbox_diff(self, sbox: list[int]):
        """
        Renders the differences between the reference SBOX and the argument SBOX
        as text.

        :param sbox: SBOX to compare with the reference SBOX.
        :type sbox: list[int]
        """
        message = "Diff:\n"
        nb_lines = 0
        for i in range(64):
            line = ""
            for j in range(4):
                index = i * 4 + j
                if sbox[index] != self._pfa.ref_sbox[index]:
                    line += f"[{index}]: {hex(self._pfa.ref_sbox[index])}->{hex(sbox[index])}\t\t|"
                else:
                    line += f"[{index}]: {hex(sbox[index])}\t\t\t|"

            # Only add line to output message if it contains an error
            if line.find("->") != -1:
                line = "\n|" + line
                nb_lines += 1
            else:
                line = ""
            message += line
            if nb_lines >= 4:
                message += "\n..."
                break
        return message

    def is_mono_byte_fault(self, sbox: list[int]) -> bool:
        """
        :return: True when only one byte differs between argument sbox and
            reference sbox
        """
        faulted = False
        for i in range(256):
            if sbox[i] != self._pfa.ref_sbox[i]:
                if faulted:
                    return False
                faulted = True
        return faulted

    def cheat_verify_mono_byte_sbox_fault(self) -> bool:
        """
        The goal of this method is to directly ask the SBOX to the target to
        confirm or reject the mono-byte error hypothesis. This is relevent in
        the context of a training so as to prevent the trainee to proceed to the
        next step with a wrong error injection. In a real scenario, the PFA
        algorithm would converge to a number of possible keys higher than one,
        wich would enable a rejection of the mono-byte error hypothesis.

        :return: True when a mono-byte error was found on the target's SBOX
            loaded in SRAM
        """
        match self._target.sbox():
            case Ok(sbox_b):
                sbox = list(sbox_b)
                for line in self.format_sbox_diff(sbox).split("\n"):
                    self._log.debug(line)
                if self.is_mono_byte_fault(sbox):
                    self._log.debug(
                        "Verification system confirmed mono-byte fault on SBOX. Thread stopped."
                    )
                    return True
                else:
                    self._log.debug(
                        "Verification system did not confirm mono-byte fault: either something else was faulted or more than one SBOX byte."
                    )
                    return False
            case err:
                self._log.critical(f"Failed to read SBOX: {err}")
                return False

    def generate_test_vectors(self, p_key: bytes) -> Result[bytes]:
        """
        Generates a test vector. Asks the target to encrypt it with the key as
        argument. Then returns the received ciphertext.

        :param p_key: the encryption key to use (ex: b'0123456789ABCDEF')
        :type p_key: bytes

        :return: Something like b'0123456789ABCDEF'
        """
        # First step, generate a random pair of (key, plain) with their
        # associated reference cipher
        (key, plain, _) = self._pfa.generate_sim_vectors(p_key)

        # Second step, perform an encryption with the test vector
        self._target.set_user_pin(1972)
        self._target.verifypin()
        self._target.key_aes128(key)
        match self._target.encrypt_aes128(plain):
            case Ok(rec_cipher):
                # Third step, store the test tuple for later analysis
                return Ok(rec_cipher)
            case err:
                return err

    def glitch_function_pfa(self):
        """
        PFA attack data analysis function called in a separate thread by a
        `Glitcher_GUI` instance in a button callback to compute the secret key.
        """

        self._log.info("Start of PFA analysis step")

        self.to_csv([], append=False)

        counts = np.zeros((16, 256), dtype=np.uint64)
        all_ciphers: list[np.ndarray] = []
        possible_keys = 100000  # placeholder definition value
        raw_guess = b""

        while possible_keys > 1:
            # Regularily check if thread needs to be interrupted
            if Campaign.should_stop_thread(self._queue):
                self._log.info("Experiment interrupted")
                return None

            # Generate a batch of new test vectors
            ciphers_batch = []
            self._log.info(
                "Generating {}th batch of {} vectors...",
                len(all_ciphers) // self._batch_size,
                self._batch_size,
            )

            while len(ciphers_batch) < self._batch_size:
                # Generate a random plain text
                plain = os.urandom(16)
                # Encrypt it with the target
                match self._target.encrypt_aes128(plain):
                    case Ok(cipher):
                        # Append it to vector lists
                        ciphers_batch.append(cipher)
                        all_ciphers.append(
                            np.array(list(cipher)).reshape(
                                (4, 4)).astype(np.uint8))
                    case Err(err):
                        self._log.warning(
                            f"Failed to encrypt plain text: {err}")

            # Analyse vectors with PFA algorithm
            self._log.info("Analyzing batch...")
            (possible_keys, raw_guess,
             _) = self._pfa.pfa(ciphers_batch, counts)
            # Not a percent per say but serves its purpose
            log_possible_keys = np.log10(float(possible_keys))
            # TODO: Adapt JS to handle key guess progress graph
            self._template_row["time"] = strftime("%H:%M:%S", gmtime())
            self._template_row["delay"] = len(all_ciphers) // self._batch_size
            self._template_row["keys"] = log_possible_keys
            self.to_csv([dict(self._template_row)], append=True)

        # Try to guess the key
        (err_i,
         fault) = self._pfa.find_right_key_hypothesis(raw_guess,
                                                      np.array(all_ciphers))
        if err_i != -1:
            # Hypothesis was valid SB'[i] is the faulted byte, thus SB[i] is
            # indeed the missing byte
            self._log.info(f"Error position detected at : {err_i}")
            self._log.info(f"Missing byte: {hex(self._pfa.ref_sbox[err_i])}")
            self._log.info(f"Overpresent byte: {hex(fault)}")

            # The computed key is for j in [0; 16]: K_j = C_j^min xor SB[i]
            ref_sbox = self._pfa.ref_sbox[err_i]
            guessed_key = bytes(
                [guess_byte ^ ref_sbox for guess_byte in raw_guess])
            final_key_guess_h = binascii.hexlify(
                self._pfa.inverse_key_expansion(guessed_key, np.uint8(fault),
                                                err_i)[0])

            self._log.info(f"Key guess: {final_key_guess_h}")
        else:
            self._log.warning(
                "Could not find a satisfying SBOX error position hypothesis")

        # End of thread
        self._log.info("End of thread.")
