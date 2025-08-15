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

### 2. 이미지 URL 절대 경로 반환 (상품 이미지)

API 응답 시 상품 이미지 URL이 상대 경로(`/media/...`)가 아닌 절대 경로(`http://...`)로 반환되도록 설정되었습니다.

-   **Django 설정:**
    -   파일: `uploads/serializers.py`
    -   내용: `ImageSerializer`의 `to_representation` 메소드를 수정하여 요청(request) 정보를 바탕으로 절대 경로를 생성합니다.

---

### 3. 이미지 업로드 개수 (상품)

상품당 이미지 업로드 개수는 **1장**으로 제한됩니다.

-   **Django 설정:**
    -   파일: `products/serializers.py`
    -   내용: `validate_image_urls` 함수를 제거하여 단일 URL만 허용하도록 변경되었습니다.
    -   파일: `products/models.py`
    -   내용: `image_urls` 필드의 `default=list`가 제거되어 `URLField`의 기본 동작(빈 문자열)을 따릅니다.
-   **프론트엔드 유의사항:** `image_urls` 필드에 **반드시 단일 URL 문자열**을 보내야 합니다. (예: `"http://yourdomain.com/path/to/image.jpg"`, 리스트 형태 `["..."]`는 오류 발생)

### 4. 사용자 프로필 이미지 URL 절대 경로 반환

사용자 프로필 이미지(`profile_image`)도 API 응답 시 절대 경로로 반환되도록 설정되었습니다.

-   **Django 설정:**
    -   파일: `users/models.py`
    -   내용: `User` 모델에 `get_profile_image_url` 메서드가 추가되었습니다.
    -   파일: `users/serializers.py`
    -   내용: `SimpleUserSerializer`, `UserSerializer`, `UserSearchSerializer`, `ProfilePageSerializer`의 `profile_image` 필드가 `SerializerMethodField`로 변경되어 `get_profile_image_url`을 호출합니다.

### 5. Nginx 설정 및 HTTPS 적용

서버 활성화 및 HTTPS 적용 과정에서 발생했던 주요 설정 변경 및 문제 해결 내용입니다.

-   **Nginx `server_name` 설정:**
    -   `config/settings.py`의 `ALLOWED_HOSTS`에는 스킴(`http://`, `https://`) 없이 호스트 이름(도메인 또는 IP)만 포함해야 합니다.
    -   `CORS_ALLOWED_ORIGINS`에는 스킴을 포함한 완전한 출처를 명시해야 합니다.
-   **HTTPS 적용 (Let's Encrypt & Certbot):**
    -   **필수:** 서버 IP를 가리키는 도메인(예: `deulbada.duckdns.org`)이 필요합니다. DuckDNS 같은 무료 서브도메인 서비스를 활용할 수 있습니다.
    -   **`https://deulbada.duckdns.org/` 설정 완료!**
    -   **Nginx 설정:** `server_name`에 도메인과 IP를 모두 명시해야 합니다 (예: `server_name deulbada.duckdns.org 43.201.70.73;`).
    -   **Certbot 실행:** `sudo certbot --nginx -d your_domain.com` 명령으로 인증서를 발급받고 Nginx에 적용합니다. 이때 HTTP를 HTTPS로 리다이렉트하는 옵션(`2`)을 선택하는 것이 권장됩니다.
    -   **`ngrok`:** 임시 테스트용으로 편리하지만, 실제 운영 환경에는 적합하지 않습니다. `ngrok` 재시작 시 URL이 변경됩니다.
-   **Nginx 설정 오류 (`proxy_set_set_header`):**
    -   `proxy_set_set_header`는 `proxy_set_header`의 오타입니다. Nginx 설정 파일에서 이 오타를 수정해야 합니다.
-   **`systemctl daemon-reload` 경고:**
    -   Nginx 설정 파일 변경 후 `systemctl reload nginx` 시 나타나는 경고는 `systemd`가 자신의 내부 설정을 갱신해야 한다는 의미입니다. `sudo systemctl daemon-reload`를 실행하여 해결합니다.

### 6. 카테고리 리팩토링 및 상품 API 개선

`Product` 모델의 카테고리 필드를 `ForeignKey`로 변경하고, 관련 API 및 Admin 기능을 개선했습니다.

-   **모델 변경:**
    -   파일: `products/models.py`
    -   내용: `Product.category` 필드가 `CharField`에서 `ForeignKey('categories.Category')`로 변경되었습니다.
-   **데이터베이스 마이그레이션:**
    -   모델 변경 후 `makemigrations` 및 `migrate`가 필요합니다.
    -   **주의:** 마이그레이션 충돌 발생 시, `db.sqlite3` 파일 삭제 후 `migrate`를 재실행하여 데이터베이스를 초기화하는 방법이 개발 환경에서 가장 빠릅니다. (이때 모든 데이터가 삭제됩니다.)
    -   `products` 앱의 마이그레이션 기록이 꼬였을 경우, `products/migrations` 폴더의 마이그레이션 파일들을 삭제하고, `django_migrations` 테이블에서 `products` 앱의 기록을 삭제한 후 (`DELETE FROM django_migrations WHERE app = 'products';`), `makemigrations products`로 새 마이그레이션을 만들고 `migrate --fake products`로 '가짜' 적용하여 해결했습니다.
-   **API 응답 형식 변경:**
    -   파일: `products/serializers.py`
    -   내용: `ProductSerializer` 및 `ProductUpdateSerializer`에서 `category` 객체 대신 `category_type` (1차 카테고리 이름)과 `category_name` (2차 카테고리 이름) 필드가 분리되어 반환되도록 변경되었습니다.
    -   상품 생성/수정 시에는 `category_id` 필드에 2차 카테고리의 ID를 보내야 합니다.
-   **상품 필터링 개선:**
    -   파일: `products/filters.py`
    -   내용: `ProductFilter`에 `category__type` 필터가 추가되어 1차 카테고리(`type`)로 상품 목록을 필터링할 수 있습니다. (예: `/api/products/?category__type=agricultural`)
-   **Admin 카테고리 드롭다운 개선:**
    -   파일: `categories/models.py`
    -   내용: `Category` 모델의 `__str__` 메서드가 `"{1차 카테고리} - {2차 카테고리}"` 형식으로 표시되도록 변경되어 admin 드롭다운에서 카테고리 선택이 명확해졌습니다.
    -   **참고:** admin에서 1차/2차 카테고리를 분리된 드롭다운으로 만드는 것은 복잡한 커스터마이징이 필요하며, 현재는 하나의 드롭다운으로 명확하게 선택 가능합니다.
-   **카테고리 데이터 채우기:**
    -   데이터베이스 초기화 후 카테고리 데이터가 사라졌을 때, `python manage.py populate_categories` 커스텀 관리 명령어를 사용하여 쉽게 데이터를 다시 채울 수 있도록 구현했습니다.

### 7. `sales_link` 필드 추가

`ProductSerializer` 및 `ProductUpdateSerializer`의 `fields` 목록에 `sales_link` 필드가 추가되어 API를 통해 해당 데이터를 주고받을 수 있습니다.

---

## 8. HTTPS 적용 상세 가이드

`https://deulbada.duckdns.org/`와 같이 안전한 연결을 설정하기 위한 상세 가이드입니다.

#### 8.1. 도메인 준비 (무료 DuckDNS 활용)

Let's Encrypt는 IP 주소에 직접 인증서를 발급하지 않으므로, 서버 IP를 가리키는 도메인이 필수입니다. 무료 서브도메인 서비스인 DuckDNS를 활용할 수 있습니다.

1.  **DuckDNS 사이트 접속:** [https://www.duckdns.org/](https://www.duckdns.org/) 에 접속하여 Google/Github 계정으로 로그인합니다.
2.  **도메인 생성:** `sub domain` 필드에 원하는 이름(예: `deulbada-backend`)을 입력하고, `current ip`에 서버의 IPv4 주소(`43.201.70.73`)가 맞는지 확인 후 `add domain` 버튼을 클릭합니다. (IPv6 주소가 없다면 비워둡니다.)
3.  **도메인 확인:** `deulbada-backend.duckdns.org`와 같은 도메인이 생성되었는지 확인합니다.

#### 8.2. Nginx 설정 파일 수정

Nginx가 도메인과 IP 주소 모두에 응답하고, HTTPS 요청을 처리할 준비를 합니다.

1.  **Nginx 설정 파일 열기:** 서버에 SSH로 접속하여 다음 명령어로 파일을 엽니다.
    ```bash
    sudo nano /etc/nginx/sites-available/default
    ```
2.  **`server_name` 수정:** `server { ... }` 블록 내의 `server_name` 지시어를 찾아 도메인과 IP 주소를 모두 포함하도록 수정합니다. (예시: `deulbada.duckdns.org`를 본인의 DuckDNS 도메인으로 변경)
    ```nginx
    server_name deulbada.duckdns.org 43.201.70.73;
    ```
3.  **Nginx 설정 문법 테스트 및 적용:**
    ```bash
    sudo nginx -t
    sudo systemctl reload nginx
    ```
    *   **오류 발생 시 (`proxy_set_set_header`):** `proxy_set_set_header`는 `proxy_set_header`의 오타입니다. 해당 라인을 찾아 수정해야 합니다.
    *   **`systemctl daemon-reload` 경고:** Nginx 설정 파일 변경 후 `systemctl reload nginx` 시 나타나는 경고는 `systemd`가 자신의 내부 설정을 갱신해야 한다는 의미입니다. `sudo systemctl daemon-reload`를 실행하여 해결합니다.

#### 8.3. Certbot 설치 및 SSL 인증서 발급

Let's Encrypt를 통해 무료 SSL 인증서를 발급받고 Nginx에 자동으로 적용합니다.

1.  **Certbot 설치:**
    ```bash
    sudo apt update
    sudo apt install certbot python3-certbot-nginx
    ```
2.  **Certbot 실행:** `your_domain.com` 대신 **본인의 DuckDNS 도메인**을 사용합니다.
    ```bash
    sudo certbot --nginx -d deulbada.duckdns.org
    ```
3.  **Certbot 질문에 답변:**
    *   **Enter email address:** 이메일 주소 입력 (인증서 만료 알림용)
    *   **Terms of Service:** 약관 동의 (`A` 입력)
    *   **Share email with EFF:** 이메일 공유 동의 여부 (`Y` 또는 `N`)
    *   **Redirect HTTP to HTTPS:** **`2`를 선택하여 HTTP 요청을 HTTPS로 자동 리다이렉트하도록 설정합니다.** (권장)

#### 8.4. HTTPS 설정 확인

1.  **브라우저 확인:** `https://deulbada.duckdns.org`로 접속하여 자물쇠 아이콘이 표시되는지 확인합니다.
2.  **프론트엔드 업데이트:** 프론트엔드에서 백엔드 API 호출 주소를 `https://deulbada.duckdns.org`로 변경합니다.

#### 8.5. `ngrok` (임시 테스트용)

`ngrok`은 임시 테스트용으로 편리하지만, 실제 운영 환경에는 적합하지 않습니다. `ngrok` 무료 버전은 터널 재시작 시 URL이 변경됩니다.