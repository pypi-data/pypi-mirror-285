from ..functions.api_request import api_request

from rest_framework import status

from django.http import StreamingHttpResponse

from ..serializers.payout_serializers import ClusterPayoutSerializer, GetPayoutSerializer

import json

async def cluster_payout(data):
  serializer = ClusterPayoutSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/payout-method/create", "", validated_data)
      return api_response
  else:
      errors = serializer.errors
      json_errors = json.dumps(errors)

      def error_generator():
          yield json_errors

      return StreamingHttpResponse(
        error_generator(),
        content_type='application/json',
        status=status.HTTP_400_BAD_REQUEST,
      )
  
async def bulk_cluster_payout(data_list):
  payload = []
  for data in data_list:
    serializer = ClusterPayoutSerializer(data=data)

    if serializer.is_valid():
        validated_data = serializer.validated_data
        payload.append(validated_data)
    else:
        errors = serializer.errors
        json_errors = json.dumps(errors)

        def error_generator():
            yield json_errors

        return StreamingHttpResponse(
          error_generator(),
          content_type='application/json',
          status=status.HTTP_400_BAD_REQUEST,
        )
    
  api_response = await api_request("POST", "/bulkimport/payout-methods", "", payload)
  return api_response

async def get_payout(data):
  serializer = GetPayoutSerializer(data=data)

  if serializer.is_valid():
      validated_data = serializer.validated_data
      api_response = await api_request("POST", "/payout-method/list", "", validated_data)
      return api_response
  else:
      errors = serializer.errors
      json_errors = json.dumps(errors)

      def error_generator():
          yield json_errors

      return StreamingHttpResponse(
        error_generator(),
        content_type='application/json',
        status=status.HTTP_400_BAD_REQUEST,
      )

async def delete_payout(id):
  api_response = await api_request("DELETE", "/payout-method/delete/" + id, "", None)
  return api_response