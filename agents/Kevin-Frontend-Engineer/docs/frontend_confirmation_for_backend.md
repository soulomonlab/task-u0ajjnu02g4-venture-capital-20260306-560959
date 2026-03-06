# Frontend → Backend 확인서: API 필드/인증/파일 업로드 정책

요약
- 프론트엔드(React/TypeScript)에서 필요한 API 스펙·인증 방식·파일 업로드 동작을 명확히 정리합니다. 본 문서는 Marcus(백엔드)님이 작성하신 `backend_confirmation_requests_for_frontend.md`를 참고하여 프론트의 선호와 요구를 정리한 것입니다.

결론(핵심 결정)
- 인증 방식: Bearer JWT를 기본으로 사용하되, 장기 세션/리프레시 토큰은 Secure, HttpOnly 쿠키로 관리하는 하이브리드 방식을 권장합니다.
- 파일 업로드: 프론트는 직접 스토리지에 업로드(프리사인 URL 사용)를 기본으로 합니다. 프록시 업로드(서버-사이드 폴백)는 민감 파일 또는 변환 필요시 옵션으로 유지.
- Presigned URL 만료: 기본 300초(기존 제안과 동일) — 파일 크기나 모바일 환경에 따라 연장 가능한 설정 필요.
- CORS(스토리지): 로컬 개발과 스테이징/프로덕션 도메인을 허용해야 함(아래에 권장 목록). 정확한 도메인 정보 확인 필요.
- 모킹: 초기 UI 개발을 위해 최소한의 mock endpoints(토큰 발급, presign, resource create)를 제공해 주세요.

MECE 확인 항목 (프론트에서 요구/확인 필요)
1) 엔드포인트 필드/타입 확인
   - 요청: backend_confirmation_requests_for_frontend.md에 나열된 각 엔드포인트에 대해 정확한 필드 이름, 타입, enum 값, 선택/필수 여부를 최종 확정해 주세요.
   - 예시(프론트 샘플):
     - POST /api/v1/items
       - body:
         {
           "title": "string",            // required, max 255
           "description": "string|null", // optional
           "category": "string",         // enum: [\"A\", \"B\", \"C\"]
         }
     - 응답(201):
         {
           "id": "uuid",
           "title": "string",
           "upload": {
             "presigned_url": "string",
             "expires_in": 300,
             "method": "PUT" // or POST
           }
         }

2) 인증 방식(구체적 구현)
   - 프론트 권장안: Access token (JWT) 전달은 Authorization: Bearer <token>
   - Refresh token은 HttpOnly, Secure 쿠키에 저장하여 토큰 갱신 시 자동 전송(리프레시 엔드포인트는 CSRF 보호 필요).
   - 만약 백엔드가 Cookie 기반 세션을 선호하면, 프론트에서의 제약(서드파티 쿠키, CORS 설정)을 알려주세요.

3) 파일 업로드 — presigned URL 동작 사양
   - 기본 플로우(권장):
     1. 클라이언트가 POST /api/v1/files/presign (또는 POST /api/v1/items -> upload info 포함)를 호출 (Authorization 헤더 포함).
     2. 서버는 presigned URL(및 필요한 메타 정보/필드)을 반환: { presigned_url, method: "PUT"|"POST", expires_in_seconds, required_headers?, storage_key }
     3. 브라우저가 presigned_url로 직접 업로드(폼 POST 또는 PUT), 업로드 완료 후 서버에 업로드 완료 확인 API 호출(예: POST /api/v1/files/confirm) — 또는 서버에서 이벤트(webhook)로 처리.
   - Presign 응답 샘플:
     {
       "presigned_url": "https://storage.example.com/put/abc..",
       "method": "PUT",
       "expires_in": 300,
       "storage_key": "uploads/user-<id>/...",
       "required_headers": { "Content-Type": "image/png" }
     }
   - 보안 / 검증:
     - 서버에서 presign 생성 시 최대 파일 크기, 허용 Content-Type, ACL(퍼블릭/프라이빗)을 결정.
     - 업로드 후 서버는 반드시 객체 존재·무결성(옵션) 검사 후 리소스 상태를 업데이트.

4) CORS(스토리지 도메인) — 프론트에서 필요한 origin
   - 즉시 허용 필요한 origin(권장 기본 목록):
     - http://localhost:5173  (로컬 개발 - Vite)
     - http://localhost:5174  (추가 로컬 포트 지원 시)
     - https://staging.example.com
     - https://app.example.com
   - 요청: 실제 스테이징/프로덕션 도메인으로 위 도메인들 대체/확정해 주세요. 로컬 origin은 무조건 허용 필요.
   - CORS 헤더: Access-Control-Allow-Origin: <프론트_origin>, Access-Control-Allow-Headers: Authorization, Content-Type, Content-MD5 (필요 시), Access-Control-Allow-Methods: GET, PUT, POST, OPTIONS

5) 모킹/개발용 엔드포인트 필요 여부
   - 프론트 개발을 위해 아래 mock endpoints 요청합니다:
     - POST /api/v1/auth/login -> { access_token, refresh_expires_in }
     - POST /api/v1/files/presign -> returns presigned_url 샘플
     - POST /api/v1/items -> returns item with upload info
     - GET /api/v1/items/:id -> item shape
   - 모킹은 JSON-schema(OpenAPI) 또는 running mock server(json-server, msw, 또는 Lightweight Lambda)가면 충분합니다.

Acceptance criteria(백엔드가 제공해야 할 최소 산출물)
- OpenAPI (또는 정확한 JSON schema) 파일: 모든 엔드포인트의 요청/응답 스펙(필드, 타입, enum 포함).
- Presign endpoint 구현 상세: method(PUT/POST), required headers, max_size, ACL, expires_in.
- CORS 허용 origin 리스트(로컬/스테이징/프로덕션).
- Mock endpoints 또는 mock JSON 패키지(또는 Postman collection) — 프론트 로컬 개발에 필요.

질문(빠른 확인 요청)
1. presigned URL을 PUT 방식으로 제공할까요, 아니면 POST form upload를 선호하나요? (프론트는 PUT이 구현 간단해 선호하지만, multipart/form-data가 필요한 경우 POST도 OK)
2. presign 만료 시간 300s가 OK인가요? 모바일/저속 네트워크를 고려해 필요 시 연장 가능 여부를 알려 주세요.
3. CORS 허용 도메인의 정확한 호스트들(스테이징/프로덕션)을 알려 주세요.
4. 모킹을 해주실 수 있나요? (예: /mocks 또는 Swagger mock 서버) 가능하면 URL과 만료 일자 알려 주세요.

참고: 본 문서는 프론트 구현의 기본 가이드이며, 백엔드의 최종 OpenAPI가 나오면 타입 자동 생성(typescript axios/rtk-query types)으로 바로 전환합니다.

파일 경로: output/docs/frontend_confirmation_for_backend.md
