import logging

import launchpad_py as launchpad


class Launchpad:
    def __init__(self):
        self.lp = launchpad.Launchpad()
        if self.lp.Check(0):
            self.lp = launchpad.LaunchpadPro()
            if self.lp.Open(0):
                logging.info("Launchpad Pro Initialized")
            else:
                raise Exception(message="ERROR: Failed to initialize launchpad")
