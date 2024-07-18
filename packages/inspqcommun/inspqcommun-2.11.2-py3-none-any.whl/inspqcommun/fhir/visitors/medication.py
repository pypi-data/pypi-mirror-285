from fhirclient.models.medication import Medication, MedicationProduct
from inspqcommun.fhir.visitors.base import BaseVisitor

class MedicationVisitor(BaseVisitor):
    
    DEFAULT_QUANTITY_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#medication/defaultquantity'
    DEFAULT_ROUTE_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#medication/defaultroute'
    EXPIRED_URL = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#medication/expired'

    def __init__(self, fhir_resource=None) -> None:
        self.setFhirResource(fhir_resource=fhir_resource if fhir_resource else Medication())

    def getFhirResource(self) -> Medication:
        return super().getFhirResource()

    def get_batches(self):
        if type(self.getFhirResource().product) is MedicationProduct and type(self.getFhirResource().product.batch) is list:
            return self.getFhirResource().product.batch
        return []

    def get_default_quantity_for_batch(self, batch=None):
        quantity = None
        if batch is not None:
            for ext in batch.extension:
                if ext.url == self.DEFAULT_QUANTITY_URL:
                    quantity = ext.valueQuantity
        return quantity
    
    def get_default_route_for_batch(self, batch=None):
        route = None
        if batch is not None:
            for ext in batch.extension:
                if ext.url == self.DEFAULT_ROUTE_URL:
                    route = ext.valueCodeableConcept
        return route

    def is_batch_expired(self, batch=None):
        expired = False
        if batch is not None:
            for ext in batch.extension:
                if ext.url == self.EXPIRED_URL:
                    expired = ext.valueBoolean
        return expired
    
    def exists_lot_id_in_lots(self, lot_id: int) -> bool:
        if self.getFhirResource() and self.getFhirResource().product and self.getFhirResource().product.batch:
            for batch in self.getFhirResource().product.batch:
                if batch.id == str(lot_id):
                    return True
        return False

    def exists_lot_number_in_lots(self, lot_number: str) -> bool:
        if self.getFhirResource() and self.getFhirResource().product and self.getFhirResource().product.batch:
            for batch in self.getFhirResource().product.batch:
                if batch.lotNumber == lot_number:
                    return True
        return False