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

Class used to apply a Persistant Fault Attack on an AES with a single faulty bytes hypothesis.
"""

from typing import Any
from multiprocessing.pool import ThreadPool
import numpy as np
import os
from .aes import AES


class PfaUtils:
    """
    Class used to apply a Persistant Fault Attack on an AES with a single faulty bytes hypothesis.
    """

    def __init__(self):
        self.ref_sbox = np.array([
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67,
            0x2b, 0xfe, 0xd7, 0xab, 0x76, 0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59,
            0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0, 0xb7,
            0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1,
            0x71, 0xd8, 0x31, 0x15, 0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05,
            0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75, 0x09, 0x83,
            0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29,
            0xe3, 0x2f, 0x84, 0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
            0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf, 0xd0, 0xef, 0xaa,
            0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c,
            0x9f, 0xa8, 0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc,
            0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2, 0xcd, 0x0c, 0x13, 0xec,
            0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19,
            0x73, 0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee,
            0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb, 0xe0, 0x32, 0x3a, 0x0a, 0x49,
            0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
            0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4,
            0xea, 0x65, 0x7a, 0xae, 0x08, 0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6,
            0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a, 0x70,
            0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9,
            0x86, 0xc1, 0x1d, 0x9e, 0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e,
            0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf, 0x8c, 0xa1,
            0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0,
            0x54, 0xbb, 0x16
        ],
                                 dtype=np.uint8)

        self.ref_inv_sbox = np.array([
            0x52,
            0x09,
            0x6A,
            0xD5,
            0x30,
            0x36,
            0xA5,
            0x38,
            0xBF,
            0x40,
            0xA3,
            0x9E,
            0x81,
            0xF3,
            0xD7,
            0xFB,
            0x7C,
            0xE3,
            0x39,
            0x82,
            0x9B,
            0x2F,
            0xFF,
            0x87,
            0x34,
            0x8E,
            0x43,
            0x44,
            0xC4,
            0xDE,
            0xE9,
            0xCB,
            0x54,
            0x7B,
            0x94,
            0x32,
            0xA6,
            0xC2,
            0x23,
            0x3D,
            0xEE,
            0x4C,
            0x95,
            0x0B,
            0x42,
            0xFA,
            0xC3,
            0x4E,
            0x08,
            0x2E,
            0xA1,
            0x66,
            0x28,
            0xD9,
            0x24,
            0xB2,
            0x76,
            0x5B,
            0xA2,
            0x49,
            0x6D,
            0x8B,
            0xD1,
            0x25,
            0x72,
            0xF8,
            0xF6,
            0x64,
            0x86,
            0x68,
            0x98,
            0x16,
            0xD4,
            0xA4,
            0x5C,
            0xCC,
            0x5D,
            0x65,
            0xB6,
            0x92,
            0x6C,
            0x70,
            0x48,
            0x50,
            0xFD,
            0xED,
            0xB9,
            0xDA,
            0x5E,
            0x15,
            0x46,
            0x57,
            0xA7,
            0x8D,
            0x9D,
            0x84,
            0x90,
            0xD8,
            0xAB,
            0x00,
            0x8C,
            0xBC,
            0xD3,
            0x0A,
            0xF7,
            0xE4,
            0x58,
            0x05,
            0xB8,
            0xB3,
            0x45,
            0x06,
            0xD0,
            0x2C,
            0x1E,
            0x8F,
            0xCA,
            0x3F,
            0x0F,
            0x02,
            0xC1,
            0xAF,
            0xBD,
            0x03,
            0x01,
            0x13,
            0x8A,
            0x6B,
            0x3A,
            0x91,
            0x11,
            0x41,
            0x4F,
            0x67,
            0xDC,
            0xEA,
            0x97,
            0xF2,
            0xCF,
            0xCE,
            0xF0,
            0xB4,
            0xE6,
            0x73,
            0x96,
            0xAC,
            0x74,
            0x22,
            0xE7,
            0xAD,
            0x35,
            0x85,
            0xE2,
            0xF9,
            0x37,
            0xE8,
            0x1C,
            0x75,
            0xDF,
            0x6E,
            0x47,
            0xF1,
            0x1A,
            0x71,
            0x1D,
            0x29,
            0xC5,
            0x89,
            0x6F,
            0xB7,
            0x62,
            0x0E,
            0xAA,
            0x18,
            0xBE,
            0x1B,
            0xFC,
            0x56,
            0x3E,
            0x4B,
            0xC6,
            0xD2,
            0x79,
            0x20,
            0x9A,
            0xDB,
            0xC0,
            0xFE,
            0x78,
            0xCD,
            0x5A,
            0xF4,
            0x1F,
            0xDD,
            0xA8,
            0x33,
            0x88,
            0x07,
            0xC7,
            0x31,
            0xB1,
            0x12,
            0x10,
            0x59,
            0x27,
            0x80,
            0xEC,
            0x5F,
            0x60,
            0x51,
            0x7F,
            0xA9,
            0x19,
            0xB5,
            0x4A,
            0x0D,
            0x2D,
            0xE5,
            0x7A,
            0x9F,
            0x93,
            0xC9,
            0x9C,
            0xEF,
            0xA0,
            0xE0,
            0x3B,
            0x4D,
            0xAE,
            0x2A,
            0xF5,
            0xB0,
            0xC8,
            0xEB,
            0xBB,
            0x3C,
            0x83,
            0x53,
            0x99,
            0x61,
            0x17,
            0x2B,
            0x04,
            0x7E,
            0xBA,
            0x77,
            0xD6,
            0x26,
            0xE1,
            0x69,
            0x14,
            0x63,
            0x55,
            0x21,
            0x0C,
            0x7D,
        ],
                                     dtype=np.uint8)

        # AES RCON
        self.ref_rcon = np.array([
            0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36, 0x6C,
            0xD8, 0xAB
        ],
                                 dtype=np.uint8)

    def generate_sim_vectors(self,
                             p_key: bytes | None = None
                             ) -> tuple[bytes, bytes, bytes]:
        """
        Generates a test vector and returns it as a tuple (key, plain, cipher).
        Encryption is done with a Python AES implementation (not with the
        target).
        """
        key: bytes = b''
        if p_key is None:
            key: bytes = os.urandom(16)
        else:
            key = p_key
        plain: bytes = os.urandom(16)

        #encryptor = AES.new(key, AES.MODE_ECB)
        encryptor = AES(key)
        cipher: bytes = encryptor.encrypt_block(plain)

        return (key, plain, cipher)

    def pfa(self,
            test_vectors: list[bytes],
            p_counts: np.ndarray | None = None) -> tuple[int, bytes, np.uint8]:
        """
        Performs a PFA on the given list of test vectors.

        Possibility of supplying a pre-existing counts array to continue a previous PFA attempt, in
        which case the test vectors should be new ones not already processed in the counts array.

        :param p_counts: matrix with shape (16, 256) that is modified in place
            to save the number of occurences of each byte value over each byte
            index in a ciphertext; used to find a byte value distribution
            anomaly in the faulted ciphertexts
        :type p_counts: np.ndarray | None

        :return: tuple of : the number of possible keys; one key out of the
            possible keys; the overrepresented byte in the count matrix
        """
        # get received ciphers from test vectors
        rec_ciphers = test_vectors

        # N is the number of test vectors
        N = len(test_vectors)
        b = np.uint8

        # initialize empty key
        cmin_candidates: list[list[b]] = []
        for u in range(16):
            cmin_candidates.append(list(np.arange(0, 2**8)))

        counts: np.ndarray
        if p_counts is None:
            counts = np.zeros((16, 2**8), dtype=np.uint64)
        else:
            counts = p_counts

        for u in range(16):
            for n in range(N):
                counts[u, list(rec_ciphers[n])[u]] += 1

        cmax_candidate: list[b] = []

        for u in range(16):
            most_common_byte: b = b(0)
            most_common_byte_count: int = 0
            for t in range(2**8):
                # discard candidate k[u] = t xor v if counts[u][t] is not zero
                if counts[u, t] != 0:
                    if counts[u, t] > most_common_byte_count:
                        most_common_byte = b(t)
                        most_common_byte_count = counts[u, t]
                    try:
                        index = cmin_candidates[u].index(b(t))
                        cmin_candidates[u].pop(index)
                    except ValueError:
                        # Raised if item not found in list (already discarded)
                        pass
            cmax_candidate.append(most_common_byte)

        cmin_guess: list[b] = []
        for i in range(16):
            try:
                cmin_guess.append(cmin_candidates[i][0])
            except IndexError:
                cmin_guess.append(b(0))

        possible_keys: int = 1
        for i in range(16):
            possible_keys *= len(cmin_candidates[i])

        overpresent_count = np.zeros((16, 2**8), dtype=np.uint8)
        for u in range(16):
            try:
                overpresent_count[u, cmax_candidate[u]
                                  ^ cmin_candidates[u][0]] += 1
            except IndexError:
                overpresent_count[u, cmax_candidate[u] ^ b(0)] += 1

        overrepresented_byte = self.overrepresented_byte(overpresent_count)

        # generate cmin_guess while taking fault_guess into account
        cmin_likelyhood_guess = []
        for u in range(16):
            try:
                cmin_likelyhood_guess.append(cmin_candidates[u][0])
                for j in range(len(cmin_candidates[u])):
                    if cmin_candidates[u][j] ^ cmax_candidate[
                            u] == overrepresented_byte:
                        cmin_likelyhood_guess[u] = cmin_candidates[u][j]
            except IndexError:
                cmin_likelyhood_guess.append(b(0))

        return (possible_keys, bytes(cmin_likelyhood_guess),
                overrepresented_byte)

    def find_right_key_hypothesis(self, raw_guess: bytes,
                                  all_ciphers: np.ndarray) -> tuple[int, int]:
        """
        At this stage of the algorithm, a single last key expansion round of the
        key was found from anomalies in the distribution of bytes in the
        ciphers. However, the error needs to be found in order to reverse the
        key expansion back to the key.

        :param raw_guess: guessed K10 key expansion (ex: b'0123456789ABCDEF')
        :type raw_guess: bytes

        :param all_ciphers: target-generated faulted test ciphertexts
        :type all_ciphers: np.array

        :return: A tuple that contains the SBOX faulted byte index and value.
            Returns (-1, -1) if no satisfactory solution was found: either the
            guess is wrong or there were too few or too many test ciphers
        """
        # Guess the correct key
        for i in range(256):
            # Assuming SB'[i] is the faulted byte, fault is SB[i] xor SB'[i]
            # WARNING: `self.test_error_position_hypo` might yield a false
            # positive if an insufficient number of ciphers are provided.
            # It might even be possible that no correct hypothesis is found if
            # too many ciphers are provided as a maximum threshold is used to
            # find the byte of lowest probability (because the key round
            # computation cannot be 100% correct).
            fault = self.test_error_position_hypo(raw_guess,
                                                  np.array(all_ciphers), i)
            if fault != -1:
                # Hypothesis was valid SB'[i] is the faulted byte, thus SB[i] is indeed the missing byte
                # No need to continue checking
                return (i, fault)
        # Return -1 when no hypothesis led to a satisfying result
        return (-1, -1)

    def overrepresented_byte(self,
                             overrepresented_bytes: np.ndarray) -> np.uint8:
        """
        Find the byte value that has the most occurences in the input histogram.

        :param overrepresented_bytes: matrix of shape (16, 256) that contains
            the number of occurences of each possible value of a byte (256
            possibilities) over each possible byte position in a ciphertext (16
            possibilities)
        :type overrepresented_bytes: np.ndarray

        :return: the byte value with the most occurences in the input matrix
        """
        cmax_candidates = []
        for u in range(16):
            cmaxu = 0
            cmaxu_count = 0
            for t in range(2**8):
                if overrepresented_bytes[u, t] > cmaxu_count:
                    cmaxu = t
                    cmaxu_count = overrepresented_bytes[u, t]
            cmax_candidates.append((cmaxu, cmaxu_count))
        cmax = 0
        cmax_count = 0
        for u in range(16):
            cmax_candidate, cmax_candidate_count = cmax_candidates[u]
            if cmax_candidate_count > cmax_count:
                cmax = cmax_candidate
                cmax_count = cmax_candidate_count
        return np.uint8(cmax)

    def test_error_position_hypo(self, raw_k10_guess: bytes,
                                 test_vectors: np.ndarray[Any,
                                                          np.dtype[np.uint8]],
                                 position: int) -> int:
        """
        This method tries to find a statistical anomaly in the distribution of
        byte values in the next-to-last round of the test ciphertexts. The key
        guess is required to compute this next-to-last round from the ciphers.

        :param raw_k10_guess: last AES key expansion round of the guessed key
            (ex: b'0123456789ABCDEF')
        :type raw_k10_guess: bytes

        :param test_vectors: list of ciphertexts generated by the target with a
            faulted SBOX to analyze:
        :type test_vectors: np.ndarray

        :param position: the guessed position of the faulted byte in the SBOX of
            the target

        :return: the faulted byte if found, -1 otherwise
        """
        counts: np.ndarray = np.zeros((2**8), dtype=np.uint64)

        sbox_key = self.ref_sbox[position]
        k10_guess: bytes = bytes(
            [guess_byte ^ sbox_key for guess_byte in raw_k10_guess])

        k9_guess: bytes = self._compute_previous_key_round(k10_guess, 10)

        k10_guess_array = np.array(list(k10_guess), dtype=np.uint8).reshape(
            (4, 4))
        k9_guess_array = np.array(list(k9_guess), dtype=np.uint8).reshape(
            (4, 4))

        c9_vectors: np.ndarray[Any, np.dtype[np.uint8]] = np.zeros(
            test_vectors.shape, dtype=np.uint8)

        # Define a task to be executed in parallel in a thread pool
        def task(test_vector: np.ndarray[Any, np.dtype[np.uint8]]):
            return self._inv_mix_columns(
                self.ref_inv_sbox[self._inv_shift_rows(
                    test_vector.astype(np.uint8) ^ k10_guess_array)]
                ^ k9_guess_array)

        # Parallelize the computation of the c9 vectors with a thread pool
        with ThreadPool(8) as pool:
            for i, result in enumerate(pool.map(task, test_vectors)):
                c9_vectors[i] = result

        for i in range(4):
            for j in range(4):
                for n in range(len(c9_vectors)):
                    counts[c9_vectors[n, i, j]] += 1

        fault: int = 0
        fault_byte_count: int = 0
        for t in range(2**8):
            if counts[t] > fault_byte_count:
                fault = t
                fault_byte_count = counts[t]
            if counts[t] < 20:
                return fault
        return -1

    def inverse_key_expansion(self,
                              last_key_round: bytes,
                              error: np.uint8 = np.uint8(0),
                              error_at: int | None = None) -> list[bytes]:
        """
        Computes the 9th previous key rounds from the 10th.

        :param last_key_round: The last key round (10th) to compute the
            previous ones from. (ex: b'0123456789ABCDEF')
        :type last_key_round: bytes

        :return: [k0, k1, ..., k10] with the same unhexlified format as the
            input round
        """
        # If a SBOX error needs to be simulated
        correct_byte = 0
        if error_at is not None:
            correct_byte = self.ref_sbox[error_at]
            self.ref_sbox[error_at] = error

        key_rounds: list[bytes] = [last_key_round]
        for i in range(10, 0, -1):
            key_rounds.append(
                self._compute_previous_key_round(key_rounds[-1], i))
        key_rounds.reverse()

        # If SBOX error was simulated, restore the SBOX
        if error_at is not None:
            self.ref_sbox[error_at] = correct_byte

        return key_rounds

    def _compute_previous_key_round(self, key_round: bytes,
                                    round_i: int) -> bytes:
        """
        Computes the previous key round from the current one.
        Parameter `round_i` is the round index associated with `key_round`.

        :param key_round: The current key round to compute the previous one
            from. (ex: b'0123456789ABCDEF')
        :type key_round: bytes
        """
        if round_i <= 0:
            raise ValueError("round_i must be >= 0")

        # Current key round as a 4x4 matrix
        key_round_n = np.array(list(key_round), dtype=np.uint8).reshape((4, 4))
        key_round_n = key_round_n.transpose()

        # Previous key round to compute
        key_round_m = np.zeros((4, 4), dtype=np.uint8)

        # The 3 last columns are easy to compute as they only require xoring to column from current key round
        for i in range(1, 4):
            key_round_m[:, i] = key_round_n[:, i] ^ key_round_n[:, i - 1]

        # The first column requires a bit more work
        # Rotate, then substitute last column of previous key round
        trans_last_column: np.ndarray = self.ref_sbox[np.roll(
            key_round_m[:, 3], -1)]
        # Xor first byte with rcon (since other bytes of rcon are 0x00)
        trans_last_column[0] ^= self.ref_rcon[round_i - 1]

        key_round_m[:, 0] = np.bitwise_xor(key_round_n[:, 0],
                                           trans_last_column)
        key_round_m = key_round_m.transpose()

        return bytes(key_round_m.flatten())

    def _inv_shift_rows(self, s):
        s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]
        s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
        s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]
        return s

    def _mix_single_column(self, a):
        t = a[0] ^ a[1] ^ a[2] ^ a[3]
        u = a[0]
        a[0] ^= t ^ self._xtime(a[0] ^ a[1])
        a[1] ^= t ^ self._xtime(a[1] ^ a[2])
        a[2] ^= t ^ self._xtime(a[2] ^ a[3])
        a[3] ^= t ^ self._xtime(a[3] ^ u)

        return a

    def _mix_columns(self, s):
        for i in range(4):
            self._mix_single_column(s[i])
        return s

    def _inv_mix_columns(self, s):
        for i in range(4):
            u = self._xtime(self._xtime(s[i][0] ^ s[i][2]))
            v = self._xtime(self._xtime(s[i][1] ^ s[i][3]))
            s[i][0] ^= u
            s[i][1] ^= v
            s[i][2] ^= u
            s[i][3] ^= v

        return self._mix_columns(s)

    def _xtime(self, a):
        return (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)

    def compute_possibles_keys_from_guess(self, guess: bytes) -> list[bytes]:
        """
        Since the faulted byte in SBOX is unknown, there are initially 256 possible keys.

        :param guess: guessed output (ex: b'0123456789ABCDEF')

        :return: list of remaining possible keys (ex: [b'0123456789ABCDEF'])
        """
        possible_keys: list[bytes] = []
        for i in range(256):
            possible_keys.append(bytes([np.uint8(i) ^ g for g in list(guess)]))
        return possible_keys
