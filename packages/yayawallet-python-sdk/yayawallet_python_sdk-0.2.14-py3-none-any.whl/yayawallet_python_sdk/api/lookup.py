from ..functions.api_request import api_request

async def gender_lookup():
  api_response = await api_request("GET", "/lookup/gender", "")
  return api_response

async def region_lookup():
  api_response = await api_request("GET", "/lookup/region", "")
  return api_response

async def business_categories_lookup():
  api_response = await api_request("GET", "/lookup/business-categories", "")
  return api_response