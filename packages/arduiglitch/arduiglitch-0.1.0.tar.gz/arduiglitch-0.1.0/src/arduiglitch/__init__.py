"""
This is an entry point script that runs the main menu of the program.
"""

import sys
from logging import Logger
from blessed import Terminal
from queue import Queue
from time import sleep
from typing import Any
import logging
from .term.synchronization import synchronized
from .term.inputter import Inputter
from .term.selectable import Selectable
from .term.selectable_menu import SelectableMenu
from .term.tab_menu import TabMenu
from .term.tab_text import TabText
from .term.tab_log import TabLog
from .utils.logger import Log
from .term.term_logger_handler import TermLogHandler
from .experiment.target_gui import TargetGUI
from .experiment.glitcher_gui import GlitcherGUI
from .experiment.pfa_campaign import PfaCampaign


def basic_gui(
    log: Logger,
    term: Terminal,
    choices: list[Selectable],
    _: Inputter,
) -> tuple[SelectableMenu, TabMenu]:
    # Build interface

    # Create a help text tab
    help_text: list[str] = [
        "=========== HOW TO USE THIS PROGRAM ===========",
        "Use the arrow keys to navigate the buttons.",
        "Press ENTER to press a button or validate an input.",
        "Some commands require an additional input that is",
        "requested in the input box.",
        "PINs are a decimal number between 0 and 9999.",
        "",
        "----------------------------------------------",
        "AES encyption examples:",
        "with std key: 2b7e151628aed2a6abf7158809cf4f3c",
        "plaintext:    3243f6a8885a308d313198a2e0370734",
        "ciphertext:   3925841D02DC09FBDC118597196A0B32",
        "with key:     000102030405060708090a0b0c0d0e0f",
        "plaintext:    00112233445566778899aabbccddeeff",
        "ciphertext:   69c4e0d86a7b0430d8cdb78070b4c55a",
        "",
        "==============================================",
        "For any complaint email to h.perrin@emse.fr",
    ]
    help_text = "\n".join(help_text)
    help_tab = TabText(term, (53, 2), 80, 30, "HELP", help_text)

    # Create a log tab that displays live `term_log_handler` output.
    # Since `term_log_handler` is connected to the main logger, it will
    # get updated whenever something like
    # `logging.getLogger(__name__).warning("some log")` is called.
    log_tab = TabLog(log.get_logh(), term, (53, 2), 90, 30, "LOG")

    # Create a tab menu to switch between the help and log tabs easily.
    tab_menu: TabMenu = TabMenu([help_tab, log_tab], 1)

    # Default interface buttons
    choices.append(
        Selectable(term, (50, 0), "❌".center(3), animated=False).with_callback(
            lambda a, b: menu.queue_cmd(("exit")), ()))
    choices.append(
        Selectable(term, (51 + 4, 0), "HELP".center(10),
                   animated=False).with_callback(
                       lambda a, b: tab_menu.select(0), ()))
    choices.append(
        Selectable(term, (51 + 4 + 11, 0), "LOG".center(10),
                   animated=False).with_callback(
                       lambda a, b: tab_menu.select(1), ()))
    choices.append(
        Selectable(term, (51 + 4 + 22, 0), "⮝".center(3),
                   animated=False).with_callback(
                       lambda a, b: log_tab.add_scroll(15), ()))
    choices.append(
        Selectable(term, (51 + 4 + 26, 0), "⮟".center(3),
                   animated=False).with_callback(
                       lambda a, b: log_tab.add_scroll(-15), ()))

    # Add buttons to a menu to easily switch between them
    menu: SelectableMenu = SelectableMenu(log, choices, tab_menu)

    log.info("Gui initialized successfully.")
    log.info("Welcome !")

    return (menu, tab_menu)


def sleep_and_print(
        default_duration: float,
        queue: Queue,  # pylint: disable=unused-argument
        user_inputs: dict[str, Any]):
    # default sleep duration
    duration: float = default_duration
    # can be overriden by a user input
    if user_inputs.get("duration (s)"):
        duration = user_inputs["duration (s)"]
    # sleep to simulate a long task
    for i in range(int(duration) * 2):
        sleep(0.5)
        logging.getLogger(__name__).info("Slept 0.5s...%d remains.",
                                         int(duration) * 2 - i - 1)


def main():
    # Initialize logging
    log = Log(__name__, level=logging.DEBUG)\
        .with_term_handler(TermLogHandler(10, 2000))\
        .with_file_handler("sandbox.log")

    # Initialize terminal
    term = Terminal()

    # Clear screen
    with synchronized(term):
        print(term.home + term.clear + term.move_y(term.height // 2))

    # Create Arduino target connection
    target = TargetGUI(log, "/dev/ttyACM1", 9600, timeout_s=1.0)
    glitcher = GlitcherGUI(log, "/dev/ttyACM0", 9600, 1.0, 100, target)

    # Create PFA campaign (needs to save data between multiple callbacks)
    pfa_campaign = PfaCampaign(log,
                               glitcher,
                               target,
                               "./static/data/data.csv",
                               batch_size=20)

    # Initialize interface

    # Add user input box
    inputter = Inputter((0, 27), width=50)
    inputter.render(term)

    init_arduino = Selectable(
        term,
        (0, 2),
        "Init. serial comm. with Glitcher and Target".center(50),
        untoggle_after=False,
    ).with_callback(glitcher.open_instruments)

    toggle_led = Selectable(term, (0, 3),
                            "Toggle Led".center(50),
                            untoggle_after=False)
    toggle_led.set_callback(target.toggle_led, toggle_led)

    choices = [
        init_arduino, toggle_led,
        Selectable(term, (0, 4),
                   "Launch function asmcode()".center(50)).with_callback(
                       target.set_asmcode_gui),
        Selectable(
            term, (0, 5),
            "Get arduino registers r16 to r25".center(50)).with_callback(
                target.get_regs_gui),
        Selectable(term, (0, 6), "Set user PIN".center(50)).with_callback(
            target.set_user_pin_gui).with_requirement(("pin", int), inputter),
        Selectable(term, (0, 7), "Read user PIN".center(50)).with_callback(
            target.get_user_pin_gui),
        Selectable(term, (0, 8), "Verify PIN".center(50)).with_callback(
            target.verifypin_gui),
        Selectable(term, (0, 9),
                   "Verify PIN (verifypinasm)".center(50)).with_callback(
                       target.verifypinasm_gui),
        Selectable(term, (0, 10),
                   "Verify PIN (verifypinhardened)".center(50)).with_callback(
                       target.verifypinhardened_gui),
        Selectable(term, (0, 11), "User mode".center(50)).with_callback(
            target.set_noadmin_gui),
        Selectable(term, (0, 12), "Set admin PIN".center(50)).with_callback(
            target.set_admin_pin_gui).with_requirement(("pin", int), inputter),
        Selectable(term, (0, 13),
                   "print g_ptc & g_authenticated".center(50)).with_callback(
                       target.verifypinstatus_gui),
        Selectable(term, (0, 14), "Set g_ptc = 3".center(50)).with_callback(
            target.set_g_ptc_3_gui),
        Selectable(term, (0, 15),
                   "Run AES128 encryption".center(50)).with_callback(
                       target.encrypt_aes128_gui).with_requirement(
                           ("plain", str), inputter),
        Selectable(term, (0, 16),
                   "New AES128 key + roundkeys".center(50)).with_callback(
                       target.key_aes128_gui).with_requirement(("key", str),
                                                               inputter),
        Selectable(term, (0, 18),
                   "INSTRUCTION SKIP CAMPAIGN".center(50)).with_callback(
                       glitcher.skip_campaign,
                       "./static/data/data.csv").with_requirement(
                           ("start delay (tick)", int),
                           inputter).with_requirement(
                               ("end delay (tick)", int),
                               inputter).with_requirement(("step delay", int),
                                                          inputter),
        Selectable(term, (0, 19),
                   "VERIFY PIN CAMPAIGN".center(50)).with_callback(
                       glitcher.verify_pin_campaign,
                       "./static/data/data.csv").with_requirement(
                           ("start delay (tick)", int),
                           inputter).with_requirement(
                               ("end delay (tick)", int),
                               inputter).with_requirement(("step delay", int),
                                                          inputter),
        Selectable(term, (0, 20),
                   "MAX ATTEMPTS BYPASS CAMPAIGN".center(50)).with_callback(
                       glitcher.skip_max_attempts_campaign,
                       "./static/data/data.csv").with_requirement(
                           ("start delay (tick)", int),
                           inputter).with_requirement(
                               ("end delay (tick)", int),
                               inputter).with_requirement(("step delay", int),
                                                          inputter),
        Selectable(term, (0, 21), "TEST PINS".center(50)).with_callback(
            glitcher.brute_force_campaign,
            "./static/data/data.csv").with_requirement(
                ("start pin", int), inputter).with_requirement(
                    ("end pin", int), inputter),
        Selectable(term, (0, 23),
                   "Generate healthy test vectors".center(50)).with_callback(
                       glitcher.pfa_generate_healthy_pairs, pfa_campaign),
        Selectable(term, (0, 24),
                   "SBOX LOAD FAULT CAMPAIGN".center(50)).with_callback(
                       glitcher.pfa_sbox_fault_campaign,
                       pfa_campaign).with_requirement(
                           ("start delay (tick)", int),
                           inputter).with_requirement(
                               ("end delay (tick)", int),
                               inputter).with_requirement(("step delay", int),
                                                          inputter),
        Selectable(term, (0, 25), "PFA analysis".center(50)).with_callback(
            glitcher.pfa_analysis, pfa_campaign)
    ]

    menu, _ = basic_gui(log, term, choices, inputter)

    # Main loop
    menu.main_loop(term)

    # Clear screen before exiting
    with synchronized(term):
        print(term.home + term.clear + term.move_y(term.height // 2))

    target.close_instrument()
    glitcher.close_instrument()
