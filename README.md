# deulbada_BE

## 📝 주요 설정 및 변경사항

### 1. 이미지 업로드 용량 제한 (5MB)

이미지 업로드 최대 용량은 5MB로 설정되어 있습니다. 이 설정은 Django와 웹서버(Nginx) 양쪽 모두에 적용해야 합니다.

-   **Django 설정:**
    -   파일: `config/settings.py`
    -   설정: `DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880` (5MB)

-   **Nginx 설정:**
    -   파일: `/etc/nginx/sites-available/default` (또는 프로젝트 설정 파일)
    -   설정: `client_max_body_size 5M;`

### 2. 이미지 URL 절대 경로 반환

API 응답 시 이미지 URL이 상대 경로(`/media/...`)가 아닌 절대 경로(`http://...`)로 반환되도록 설정되었습니다.

-   **Django 설정:**
    -   파일: `uploads/serializers.py`
    -   내용: `ImageSerializer`의 `to_representation` 메소드를 수정하여 요청(request) 정보를 바탕으로 절대 경로를 생성합니다.
