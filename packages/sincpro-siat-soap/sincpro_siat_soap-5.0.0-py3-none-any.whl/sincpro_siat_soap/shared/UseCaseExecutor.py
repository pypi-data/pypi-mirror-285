from typing import Any, Union

from .core_exceptions import SIATException
from .logger import logger
from .UseCase import UseCase


class CommandIsAlreadyRegistered(Exception):
    pass


class UseCaseError(Exception):
    pass


class UseCaseExecutor:
    def __init__(self):
        self.commands = dict()

    def register(self, use_case: UseCase, command) -> bool:
        if command.__name__ in self.commands:
            raise CommandIsAlreadyRegistered(
                f"Command {command.__name__} is already registered"
            )

        logger.info(
            f"Add use case: [{use_case.__class__.__name__}] command [{command.__name__}]"
        )
        self.commands[command.__name__] = use_case

        return True

    def execute(self, command: object) -> Union[Any, None]:
        logger.info(f"Executing command: [{command.__class__.__name__}]")
        logger.debug(f"{command}")

        try:
            response = self.commands[command.__class__.__name__].execute(command)
            if (
                hasattr(response, "raw_response")
                and response.raw_response["transaccion"] is False
            ):
                logger.error(
                    f"Use case was not able to execute the transaction for the command [{command.__class__.__name__}]"
                )
                logger.error(f"Command with error: \n {command}")
                logger.error(f"response: \n{response}")
            else:
                logger.debug(f"response: \n{response}")
            return response

        except SIATException as error:
            logger.error(str(error), exc_info=True)
            raise error

        except Exception as error:
            logger.error(f"Error in command: [{command.__class__.__name__}]", exc_info=True)
            raise UseCaseError(
                f"The use case: [{self.commands[command.__class__.__name__].__class__.__name__}] was not able to execute sucessfully"
            ) from error
