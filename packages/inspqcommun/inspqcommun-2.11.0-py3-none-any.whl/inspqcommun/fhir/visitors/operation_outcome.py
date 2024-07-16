from fhirclient.models.operationoutcome import OperationOutcome
from fhirclient.models.coding import Coding
from inspqcommun.fhir.visitors.base import BaseVisitor

class OperationOutcomeVisitor(BaseVisitor):

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource if fhir_resource else OperationOutcome())

    def getFhirResource(self) -> OperationOutcome:
        return super().getFhirResource()

    def get_issue_count(self):
        return len(self.getFhirResource().issue)

    def get_issue_code(self, index=0):
        return self.getFhirResource().issue[index].code

    def get_issue_severity(self, index=0):
        return self.getFhirResource().issue[index].severity

    def get_issue_details(self, index=0) -> Coding:
        details = self._get_coding_par_system(self.getFhirResource().issue[index].details)
        return details if details else self.getFhirResource().issue[index].details[0]