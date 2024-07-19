from functools import partial

from sincpro_siat_soap.shared.inversion_of_control import (
    FeatureContainer,
    inject_to_feature_container,
)

# ----------------------------------------------------------------------------------------------------------------------
# The Registry module will instance all the dependency injection with the proper containers
# ----------------------------------------------------------------------------------------------------------------------
container = FeatureContainer()
feature = partial(inject_to_feature_container, container)
setup_dict = container.injected_params.from_dict
factory_use_case = container.use_case
factory_siat_services = container.proxy_siat_services
