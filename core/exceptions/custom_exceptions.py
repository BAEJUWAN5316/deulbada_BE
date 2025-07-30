from rest_framework.exceptions import APIException

class CustomAPIException(APIException):
    status_code = 400
    default_detail = "잘못된 요청입니다."
