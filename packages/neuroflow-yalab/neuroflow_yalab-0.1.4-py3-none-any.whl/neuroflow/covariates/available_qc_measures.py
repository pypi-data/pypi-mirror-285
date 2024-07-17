import inspect

from neuroflow.covariates import (
    ParticipantDemographics,
    QualityControl,
    SessionCovariates,
)


def get_class_inputs(cls):
    # Get the __init__ method of the class
    init_method = cls.__init__

    # Use inspect.signature() to get the signature of the __init__ method
    sig = inspect.signature(init_method)

    # Extract the parameters, excluding 'self'
    parameters = [name for name, param in sig.parameters.items() if name != "self"]

    return parameters


def get_available_measures():
    """
    Get the available measures for the participant

    Returns
    -------
    dict
        The available measures for the participant
    """
    results = {}
    for available_measure in [
        ParticipantDemographics,
        SessionCovariates,
        QualityControl,
    ]:
        name = available_measure.COVARIATE_SOURCE
        results[name] = {
            "runner": available_measure,
            "inputs": get_class_inputs(available_measure),
        }
    return results
