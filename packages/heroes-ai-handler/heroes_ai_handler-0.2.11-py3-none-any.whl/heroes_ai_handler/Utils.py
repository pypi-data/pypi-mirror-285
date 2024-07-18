import os
from .Logger import Logger


LOGGER = Logger(
    name='Utils',
    log_to_console=True,
)


class NoEnvironmentVariable(Exception):
    def __init__(self, variable, *args: object) -> None:
        message = f"Variable of name '{variable}' not found"
        super().__init__(message)


class Utils:
    def __init__(self) -> None:
        pass


    def get_env_variable(self, variable_name):
        try:
            return os.environ[variable_name]
        except Exception as e:
            LOGGER.error(
                f"Tried to get env variable '{variable_name}' but it doesn't exist\n{e}"
            )
            raise NoEnvironmentVariable(variable_name)