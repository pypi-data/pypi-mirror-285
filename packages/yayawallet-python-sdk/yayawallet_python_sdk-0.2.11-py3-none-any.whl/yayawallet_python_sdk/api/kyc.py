from ..functions.api_request import api_request

async def get_licenses_by_tin(tin):    
  api_response = await api_request("GET", "/kyc/etrade/find-by-tin/" + tin, "", None)
  return api_response

async def get_business_details(tin: str, licenseNumber: str):
  api_response = await api_request("POST", "/kyc/etrade/find-by-license-number/" + tin, "", {"licenseNumber": licenseNumber})
  return api_response