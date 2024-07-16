from ..functions.api_request import api_request

async def create_bill(client_yaya_account, customer_yaya_account, amount, start_at, due_at, customer_id, bill_id, bill_code, bill_season, cluster, description, phone, email, details):
  payload = {
    "client_yaya_account": client_yaya_account,
    "amount": amount,
    "due_at": due_at,
    "customer_id": customer_id,
    "bill_id": bill_id,
  }

  if customer_yaya_account is not None:
    payload["customer_yaya_account"] = customer_yaya_account
  if start_at is not None:
    payload["start_at"] = start_at
  if bill_code is not None:
    payload["bill_code"] = bill_code
  if bill_season is not None:
    payload["bill_season"] = bill_season
  if cluster is not None:
    payload["cluster"] = cluster
  if description is not None:
    payload["description"] = description
  if phone is not None:
    payload["phone"] = phone
  if email is not None:
    payload["email"] = email
  if details is not None:
    payload["details"] = details
    
  api_response = await api_request("POST", "/bill/create", "", payload)
  return api_response

async def create_bulk_bill(bulkBill):
  api_response = await api_request("POST", "/bulkimport/bills", "", bulkBill)
  return api_response

async def bulk_bill_status():
  api_response = await api_request("GET", "/bulkimport/list", "")
  return api_response

async def update_bill(client_yaya_account, customer_yaya_account, amount, start_at, due_at, customer_id, bill_id, bill_code, bill_season, cluster, description, phone, email, details):
  payload = {
    "client_yaya_account": client_yaya_account,
    "amount": amount,
    "due_at": due_at,
    "customer_id": customer_id,
    "bill_id": bill_id,
  }

  if customer_yaya_account is not None:
    payload["customer_yaya_account"] = customer_yaya_account
  if start_at is not None:
    payload["start_at"] = start_at
  if bill_code is not None:
    payload["bill_code"] = bill_code
  if bill_season is not None:
    payload["bill_season"] = bill_season
  if cluster is not None:
    payload["cluster"] = cluster
  if description is not None:
    payload["description"] = description
  if phone is not None:
    payload["phone"] = phone
  if email is not None:
    payload["email"] = email
  if details is not None:
    payload["details"] = details
  api_response = await api_request("POST", "/bill/update", "", payload)
  return api_response

async def bulk_bill_list(client_yaya_account, param):
  page_number_param = "?p=1"
  if(param != None):
    page_number_param = param
  api_response = await api_request("POST", "/bill/list", page_number_param, {"client_yaya_account": client_yaya_account})
  return api_response

async def bulk_bill_find(client_yaya_account, bill_id):
  api_response = await api_request("POST", "/bill/find", "", {"bill_id": bill_id, "client_yaya_account": client_yaya_account})
  return api_response