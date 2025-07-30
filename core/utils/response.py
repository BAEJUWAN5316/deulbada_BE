from rest_framework.response import Response

def success_response(message="요청 성공", data=None):
    return Response({
        "success": True,
        "message": message,
        "data": data,
    })

def error_response(message="요청 실패", data=None):
    return Response({
        "success": False,
        "message": message,
        "data": data,
    })
