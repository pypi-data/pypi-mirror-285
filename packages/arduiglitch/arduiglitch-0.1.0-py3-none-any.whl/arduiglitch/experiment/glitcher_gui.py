"""
`Glitcher` class wrapper that has some knowledge of terminal based gui.
It is also more verbose.
Provides methods for each experiment in the tutorial to be used as callback in
the gui.
"""

from ..arduino.glitcher import Glitcher
from ..utils.logger import Log
from ..utils.result import Ok, Err
from ..experiment.skip_campaign import SkipCampaign
from ..experiment.verify_pin_campaign import VerifyPinCampaign
from ..experiment.skip_max_attempts_campaign import SkipMaxAttemptsCampaign
from ..experiment.target_gui import TargetGUI
from ..experiment.pfa_campaign import PfaCampaign
from ..term.synchronization import synchronized

from queue import Queue
from typing import Any
import logging
import multiprocessing
from flask import Flask, render_template
from flask.logging import default_handler
import flask.cli


class GlitcherGUI(Glitcher):
    """
    `Glitcher` subclass with some wrapper methods to use as callback in the GUI.
    The goal is the make the GUI code as clean as possible. As such, it should
    only be used by the GUI. For dev purposes, check examples in the `term`
    submodule.
    """

    def __init__(self, log: Log, url: str, baudrate: int, timeout_s: float,
                 cooldown_ms: int, target: TargetGUI):
        super().__init__(log, url, baudrate, timeout_s, cooldown_ms)
        # `GlitcherGUI` gets a reference to the target serial com to
        # enable easier campaign management.
        self._target = target

    def open_instruments(self, _: Queue) -> None:
        """
        Try to open communication with the instrument.
        Log result. A queue is taken as argument because of GUI buttons
        interface.
        """
        match self._target.open_instrument():
            case Ok(None):
                self._log.info("Serial com with target opened.")
            case Err(e):
                self._log.error(e)
        match super().open_instrument():
            case Ok(None):
                self._log.info("Serial com with glitcher opened.")
            case Err(e):
                self._log.error(e)

    @staticmethod
    def _create_flask_app() -> Flask:
        app = Flask(__name__, root_path=".", template_folder="templates")
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        logging.getLogger("werkzeug").disabled = True
        app.logger.removeHandler(default_handler)
        flask.cli.show_server_banner = lambda *args: None

        @app.route("/")
        def index():
            return render_template("index.html")

        return app

    @staticmethod
    def _with_flask_server(callback: Any) -> Any:
        """
        Static method to be used as a decorator on methods that start a
        campaign so that a Flask server is run during the campaign (to
        visualize data in a graph in the browser).
        """

        def wrapper(*args, **kwargs):
            app = GlitcherGUI._create_flask_app()

            flask_process = multiprocessing.Process(target=app.run,
                                                    kwargs={"debug": False})
            flask_process.start()

            callback(*args, **kwargs)

            flask_process.terminate()
            flask_process.join()

        return wrapper

    @_with_flask_server
    def skip_campaign(self, csv_filename: str, queue: Queue,
                      user_inputs: dict[str, Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Starts the skip instruction campaign.
        """
        # Create a new campaign
        campaign = SkipCampaign(
            self._log,
            self,
            self._target,
            csv_filename,
            queue,
            user_inputs.get("start delay (tick)", 0),
            user_inputs.get("end delay (tick)", 0),
            user_inputs.get("step delay", 1),
        )
        campaign.run()

    @_with_flask_server
    def verify_pin_campaign(self, csv_filename: str, queue: Queue,
                            user_inputs: dict[str, Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Starts the verify pin campaign.
        """
        # Create a new campaign
        campaign = VerifyPinCampaign(
            self._log,
            self,
            self._target,
            csv_filename,
            queue,
            user_inputs.get("start delay (tick)", 0),
            user_inputs.get("end delay (tick)", 0),
            user_inputs.get("step delay", 1),
        )
        campaign.run()

    @_with_flask_server
    def skip_max_attempts_campaign(self, csv_filename: str, queue: Queue,
                                   user_inputs: dict[str, Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Starts the skip max authentification attempts campaign.
        """
        # Create a new campaign
        campaign = SkipMaxAttemptsCampaign(
            self._log,
            self,
            self._target,
            csv_filename,
            queue,
            user_inputs.get("start delay (tick)", 0),
            user_inputs.get("end delay (tick)", 0),
            user_inputs.get("step delay", 1),
        )
        campaign.run()

    def brute_force_campaign(self, csv_filename: str, queue: Queue,
                             user_inputs: dict[str, Any]) -> None:
        """
        Method designed to be a button callback in the GUI.
        Starts the pin brute force campaign.
        """
        # Create a new campaign
        campaign = SkipMaxAttemptsCampaign(
            self._log,
            self,
            self._target,
            csv_filename,
            queue,
            0,
            0,
            1,
        )

        min_pin = user_inputs.get("start pin", 0)
        max_pin = user_inputs.get("end pin", 9999)
        campaign.brute_force_pin(min_pin, max_pin, verbose=True)

    def pfa_generate_healthy_pairs(
        self,
        pfa_campaign: PfaCampaign,
        queue: Queue,
    ):
        """
        Method designed to be a button callback in the GUI.
        Asks the target to generate a fixed number of healthy
        plaintext/cyphertext pairs.
        """
        with synchronized(pfa_campaign):
            pfa_campaign.set_queue(queue)
            pfa_campaign.generate_healthy_pairs()

    def pfa_sbox_fault_campaign(self, pfa_campaign: PfaCampaign, queue: Queue,
                                user_inputs: dict[str, Any]):
        """
        Method designed to be a button callback in the GUI.
        Starts the persistant fault attack on AES SBOX loading campaign.
        """
        with synchronized(pfa_campaign):
            pfa_campaign.set_queue(queue)
            pfa_campaign.set_delay_sweep(
                user_inputs.get("start delay (tick)", 0),
                user_inputs.get("end delay (tick)", 0),
                user_inputs.get("step delay", 1),
            )
            pfa_campaign.run()

    def pfa_analysis(
        self,
        pfa_campaign: PfaCampaign,
        queue: Queue,
    ):
        """
        Method designed to be a button callback in the GUI.
        Starts the persistant fault attack on AES SBOX data analysis to compute
        the secret key used.
        """
        with synchronized(pfa_campaign):
            pfa_campaign.set_queue(queue)
            pfa_campaign.glitch_function_pfa()
