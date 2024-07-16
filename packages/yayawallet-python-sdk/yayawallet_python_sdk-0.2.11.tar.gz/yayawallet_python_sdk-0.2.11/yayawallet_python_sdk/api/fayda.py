from ..functions.api_request import api_request

async def get_fayda_otp(fin):    
  api_response = await api_request("GET", "/kyc/fayda/request-otp/" + fin, "", None)
  return api_response

async def get_fayda_kyc(fin, transaction_id, otp):    
  api_response = await api_request("GET", "/kyc/fayda/get-kyc-details/" + fin + "/" + transaction_id + "/" + otp, "", None)
  return api_response