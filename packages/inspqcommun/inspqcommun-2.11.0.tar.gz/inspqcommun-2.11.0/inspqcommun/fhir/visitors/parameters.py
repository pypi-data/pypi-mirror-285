from fhirclient.models.parameters import Parameters, ParametersParameter
from fhirclient.models.resource import Resource
from inspqcommun.fhir.visitors.base import BaseVisitor

class ParametersVisitor(BaseVisitor):

    def __init__(self, fhir_resource=None):
        self.setFhirResource(fhir_resource if fhir_resource is not None else Parameters())

    def getFhirResource(self) -> Parameters:
        return super().getFhirResource()

    def add_parameter(self, valeur : any, name='resource'):
        parameter = ParametersParameter()
        parameter.name=name
        if isinstance(valeur, Resource):
            parameter.resource = valeur
        elif isinstance(valeur, str):
            parameter.valueString = valeur

        if self.getFhirResource().parameter is None:
            self.getFhirResource().parameter = []
        
        self.getFhirResource().parameter.append(parameter)
    
    def find_by_name(self, name='resource') -> ParametersParameter:
        if self.getFhirResource().parameter:
            parameter: ParametersParameter
            for parameter in self.getFhirResource().parameter:
                if parameter.name == name:
                    return parameter
        return None