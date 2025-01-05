from http.server import BaseHTTPRequestHandler

def handler(request, response):
    return {
        "statusCode": 200,
        "body": "Echo Systems Phone Order System - Webhook Handler Running"
    }
