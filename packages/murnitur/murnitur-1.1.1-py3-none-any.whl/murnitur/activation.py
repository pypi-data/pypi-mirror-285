import os
import json
import openlit as lit
from .util import Util

SECRET_FILE_PATH = os.path.expanduser("~/.murnitur_secret")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def activate_shield():
    try:
        response = Util().authenticate()
        if response.get("authenticated", False):
            try:
                with open(SECRET_FILE_PATH, "w") as file:
                    json.dump(response, file)
                print(f"{GREEN}Shield activation successful.{RESET}")
            except OSError as e:
                print(f"{RED}Error writing to {SECRET_FILE_PATH}: {e}{RESET}")
        else:
            print(
                f"{RED}Activation failed or you are not subscribed to the business plan.{RESET}"
            )
    except Exception as e:
        lit.logger.error(f"{RED}{e}{RESET}")


class ActivationException(Exception):
    """Exception raised for errors in the activation process."""

    def __init__(self, message="Murnitur Shield activation is required"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"ActivationException: {self.message}"
