from fhirclient.models.valueset import ValueSet
from inspqcommun.fhir.visitors.parameters import ParametersVisitor
from inspqcommun.fhir.clients.base_client import BaseClient
from requests import Response
import requests, json
import logging

log = logging.getLogger(__name__)

class ValueSetClient(BaseClient):

    valueset_endpoint = "{base_url}/ValueSet"
    valueset_vocabulary_domain_endpoint = valueset_endpoint + "/{domain}"
    valueset_city_endpoint = valueset_endpoint + "/$search-city"
    valueset_province_endpoint = valueset_endpoint + "/$provinces-by-country"

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def get_valueset_by_domain(self, domain):
        response = requests.get(
            url=self.valueset_vocabulary_domain_endpoint.format(base_url=self.get_fhir_url(), domain=domain),
            headers=self.headers,
            verify=self.validate_certs
        )
        log.info("GET ValueSet/{} : {}".format(domain, response.status_code))
        return response
    
    def get_gender(self):
        return self.get_valueset_by_domain(domain="gender")

    def get_administrationsite(self):
        return self.get_valueset_by_domain(domain="administrationsite")
    
    def get_identifiertype(self):
        return self.get_valueset_by_domain(domain="identifiertype")
    
    def get_country(self):
        return self.get_valueset_by_domain(domain='country')
    
    def get_contacttype(self):
        return self.get_valueset_by_domain(domain='contacttype')
    
    def get_agent(self):
        return self.get_valueset_by_domain(domain='agent')
    
    def get_dosageunit(self):
        return self.get_valueset_by_domain(domain='dosageunit')
    
    def get_administrationroute(self):
        return self.get_valueset_by_domain(domain='administrationroute')
    
    def get_administrationreason(self):
        return self.get_valueset_by_domain(domain='administrationreason')
    
    def get_city_by_name(self, name: str, province_code:str='QC'):
        visitor = ParametersVisitor()
        if name:
            visitor.add_parameter(name, "city-name")
        if province_code:
            visitor.add_parameter(province_code, "province-code")
        
        response = requests.post(
            url=self.valueset_city_endpoint.format(base_url=self.get_fhir_url()),
            headers=self.headers,
            data=json.dumps(visitor.getFhirResource().as_json()),
            verify=self.validate_certs)
        log.info("POST ValueSet/$search-city - city-name={}&province-code={}: {}".format(name, province_code, response.status_code))
        return response        
    
    def get_provinces(self, country_code:str='CA'):
        visitor = ParametersVisitor()
        if country_code:
            visitor.add_parameter(country_code, 'country-code')
        
        response = requests.post(
            url=self.valueset_province_endpoint.format(base_url=self.get_fhir_url()),
            headers=self.headers,
            data=json.dumps(visitor.getFhirResource().as_json()),
            verify=self.validate_certs)
        log.info("POST ValueSet/$provinces-by-country - country-code={}: {}".format(country_code, response.status_code))
        return response
    
    def extract_value_set_from_response(self, valueset_response: Response) -> ValueSet:
        if valueset_response.status_code == 200:
            content_dict = json.loads(valueset_response.content)
            return ValueSet(jsondict=content_dict)
        else:
            return None