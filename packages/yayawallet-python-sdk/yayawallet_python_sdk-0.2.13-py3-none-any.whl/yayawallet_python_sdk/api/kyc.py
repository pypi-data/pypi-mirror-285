from ..functions.api_request import api_request

async def request_otp(fin):    
  api_response = await api_request("GET", "/kyc/fayda/request-otp/" + fin, "", None)
  return api_response

async def get_kyc_details(fin, transaction_id, otp):    
  api_response = await api_request("GET", "/kyc/fayda/get-kyc-details/" + fin + "/" + transaction_id + "/" + otp, "", None)
  return api_response

async def find_by_tin(tin):    
  api_response = await api_request("GET", "/kyc/etrade/find-by-tin/" + tin, "", None)
  return api_response

async def find_by_license_number(tin: str, licenseNumber: str):
  api_response = await api_request("POST", "/kyc/etrade/find-by-license-number/" + tin, "", {"licenseNumber": licenseNumber})
  return api_response