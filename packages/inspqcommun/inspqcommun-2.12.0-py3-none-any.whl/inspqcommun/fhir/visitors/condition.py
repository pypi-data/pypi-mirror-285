from fhirclient.models.condition import Condition
from fhirclient.models.extension import Extension
from fhirclient.models.coding import Coding
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.reference import Reference
from inspqcommun.fhir.visitors.base import BaseVisitor

class ConditionVisitor(BaseVisitor):
    LOCATION_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/location'
    AGENT_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/agent"
    ANTIGEN_URL = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/antigen"

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource if fhir_resource else Condition())
    
    def getFhirResource(self) -> Condition:
        return super().getFhirResource()

    def get_id(self) -> int:
        return self.getFhirResource().id
    
    def set_id(self, id: str) -> None:
        self.getFhirResource().id = id

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

    def set_agent(self, coding: Coding) -> None:
        extension = Extension()
        extension.url = self.AGENT_URL
        extension.valueCodeableConcept = CodeableConcept()
        extension.valueCodeableConcept.coding = [coding]
        self.getFhirResource().extension = self.add_or_update_extension_to_extensions(
            extension=extension,
            extensions=self.getFhirResource().extension)

    def get_antigen(self) -> Coding:
        return self.__get_extension_coding(url=self.ANTIGEN_URL, system=self.DEFAULT_CODING_SYSTEM, version=self.DEFAULT_CODING_VERSION)

    def get_location(self) -> str:
        if self.getFhirResource().extension:
            for extension in self.getFhirResource().extension:
                if extension.url == self.LOCATION_URL and extension.valueString:
                    return extension.valueString
        return None
    
    def set_location(self, location_id: str) -> None:
        extension = Extension()
        extension.url = self.LOCATION_URL
        extension.valueString = location_id
        self.getFhirResource().extension = self.add_or_update_extension_to_extensions(
            extension=extension,
            extensions=self.getFhirResource().extension)
    
    def get_patient_id(self) -> str:
        return self.getFhirResource().patient.reference
    
    def set_patient_id(self, id: str) -> None:
        ref = Reference()
        ref.reference = id
        self.set_patient(patient_ref=ref)

    def get_patient(self) -> Reference:
        return self.getFhirResource().patient
    
    def set_patient(self, patient_ref: Reference) -> None:
        self.getFhirResource().patient = patient_ref

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