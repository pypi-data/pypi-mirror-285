import os
import httpx
from yayawallet_python_sdk.functions.get_time import get_time
from typing import Dict
from django.http import StreamingHttpResponse
from yayawallet_python_sdk.functions.generate_signature import generate_signature
import json

async def api_request(
    method: str,
    path: str,
    params: str,
    data: Dict = None,
):    
    url = os.getenv("YAYA_API_URL") + path + params
    YAYA_API_PATH = os.getenv("YAYA_API_PATH") + path

    unix_time_response = await get_time()
    unix_time = str(unix_time_response['time'])
    json_body = ""
    if(data != None):
        json_body = json.dumps(data)
    signed_payload = generate_signature(unix_time, method, YAYA_API_PATH, json_body)
        
    headers = {
        "Content-Type": "application/json",
        "YAYA-API-KEY": os.getenv("YAYA_API_KEY"),
        "YAYA-API-TIMESTAMP": unix_time,
        "YAYA-API-SIGN": signed_payload,
    }
        
    if(method == "POST"):
        response = httpx.post(url, headers=headers, json=data, timeout=100.0)
        return StreamingHttpResponse(
            response.text,
            content_type=response.headers.get('content-type'),
            status=response.status_code,
            reason=response.reason_phrase
        )
    if(method == "PUT"):
        response = httpx.put(url, headers=headers, data=data, timeout=100.0)
        return StreamingHttpResponse(
            response.text,
            content_type=response.headers.get('content-type'),
            status=response.status_code,
            reason=response.reason_phrase
        )
    if(method == "DELETE"):
        response = httpx.delete(url, headers=headers, timeout=100.0)
        return StreamingHttpResponse(
            response.text,
            content_type=response.headers.get('content-type'),
            status=response.status_code,
            reason=response.reason_phrase
        )
    response = httpx.get(url, headers=headers, timeout=100.0)
    return StreamingHttpResponse(
        response.text,
        content_type=response.headers.get('content-type'),
        status=response.status_code,
        reason=response.reason_phrase
    )



