from ..functions.api_request import api_request

async def create(account_number: str, amount: str, reason: str, recurring: str, start_at: str, meta_data):
  api_response = await api_request("POST", "/scheduled-payment/create", "", {"account_number": account_number, "amount": amount, "reason": reason, "recurring": recurring, "start_at": start_at, "meta_data": meta_data})
  return api_response

async def get_list():
  api_response = await api_request("GET", "/scheduled-payment/list", "", None)
  return api_response

async def archive(id):
  api_response = await api_request("GET", "/scheduled-payment/archive/" + id, "", None)
  return api_response