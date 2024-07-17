from fhirclient.models.condition import Condition
from fhirclient.models.extension import Extension
from fhirclient.models.coding import Coding
from inspqcommun.fhir.visitors.base import BaseVisitor

class ConditionVisitor(BaseVisitor):
    
    AGENT_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/agent"
    ANTIGEN_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/antigen"

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource if fhir_resource else Condition())
    
    def getFhirResource(self) -> Condition:
        return super().getFhirResource()

    def get_code(self) -> Coding:
        if self.getFhirResource().code:
            for coding in self.getFhirResource().code.coding:
                if coding.system == self.DEFAULT_CODING_SYSTEM and coding.version == self.DEFAULT_CODING_VERSION:
                    return coding
        return None

    def get_category(self) -> Coding:
        if self.getFhirResource().category:
            for coding in self.getFhirResource().category.coding:
                if coding.system == self.DEFAULT_CODING_SYSTEM and coding.version == self.DEFAULT_CODING_VERSION:
                    return coding
        return None
    
    def get_agent(self) -> Coding:
        return self.__get_extension_coding(url=self.AGENT_URL, system=self.DEFAULT_CODING_SYSTEM, version=self.DEFAULT_CODING_VERSION)

    def get_antigen(self) -> Coding:
        return self.__get_extension_coding(url=self.ANTIGEN_URL, system=self.DEFAULT_CODING_SYSTEM, version=self.DEFAULT_CODING_VERSION)

    def __get_extension_coding(self, url, system, version) -> Coding:
        if self.getFhirResource().extension is not None:
            extension: Extension
            coding: Coding
            for extension in self.getFhirResource().extension:
                if extension.url == url and extension.valueCodeableConcept is not None:
                    for coding in extension.valueCodeableConcept.coding:
                        if coding.system == system and coding.version == version:
                            return coding
        return None