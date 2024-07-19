from typing import Union

from dependency_injector import containers, providers

from sincpro_siat_soap.shared.logger import logger
from sincpro_siat_soap.shared.soap import ProxySiatServices
from sincpro_siat_soap.shared.UseCaseExecutor import UseCaseExecutor


class FeatureContainer(containers.DeclarativeContainer):
    injected_params = providers.Configuration()
    proxy_siat_services = providers.Singleton(
        ProxySiatServices,
        siat_environment=injected_params.siat_environment,
        token=injected_params.siat_token,
        modality=injected_params.modality,
    )
    commands = providers.Dict({})
    use_case = providers.Factory(UseCaseExecutor)


# ----------------------------------------------------------------------------------------------------------------------
# Decorator for use cases
# this has a strong coupling with the UseCase Abstraction, we need to pass the siat services -> soap services
# ----------------------------------------------------------------------------------------------------------------------
def inject_to_feature_container(container: FeatureContainer, command: Union[str, list]):
    def inner_fn(decorated_class):
        commands = command
        if not isinstance(command, list):
            commands = [command]

        for c in commands:
            logger.info(f"Registering UseCase {decorated_class.__name__}")
            container.commands = providers.Dict(
                {
                    **{
                        c.__name__: providers.Factory(
                            decorated_class,
                            container.proxy_siat_services.provided.siat_services,
                        )
                    },
                    **container.commands.kwargs,
                }
            )
            container.use_case.add_attributes(commands=container.commands)

        return decorated_class

    return inner_fn
