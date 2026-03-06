결론
- API 스키마(필드/타입/enum), 인증 방식 권장(기본), 파일 presigned URL 정책, 그리고 프론트가 바로 쓸 수 있는 5종 샘플 JSON을 아래에 확정하여 제공함.

요약
- 인증: 권장: Bearer JWT (access 15m) + Refresh token as HttpOnly Secure cookie (7d) with rotation 및 DB 저장(권한 취소 가능). 대안: 서버 세션 쿠키(엔터프라이즈 옵션).
- 파일 presigned URL 정책: 업로드 presign TTL=5m(기본), 다운로드 presign TTL=15m(비민감), 민감 파일은 TTL<=1m 또는 서버 스트리밍. 업로드 최대 파일 크기 100MB 기본(추가 정책 가능).
- API 스키마: Ventures 리소스(필드 타입/enum 포함), Upload/Download presign 응답, Auth 응답 등 OpenAPI 형태로 명세 파일을 생성함.

상세: 인증(Auth) 설계
- Access token: JWT (alg=RS256 권장) — 만료: 15분
  - Claims: iss, sub(user_id as uuid), aud, exp, iat, jti, roles: ["admin","editor","viewer"]
- Refresh token: opaque token stored as HttpOnly Secure SameSite=strict cookie, 만료: 7일
  - 구현: 토큰 값은 DB에 해시 형태로 보관 (token_hash, user_id, device_id, jti, expires_at, revoked:boolean)
  - 토큰 교체(rotation): refresh 시 새 refresh 생성, 이전 토큰은 즉시 revoked
- 인증 흐름 요약:
  1) 로그인 -> access token 반환(응답 바디) + refresh cookie 발급
  2) 클라이언트는 API 호출 시 Authorization: Bearer <access_token>
  3) access 만료 시 /auth/refresh 호출(쿠키 자동 전송) -> 새로운 access + refresh
  4) 로그아웃 -> refresh revoke

대체 옵션
- Server-side session cookie (HttpOnly, Secure, SameSite=strict) 사용가능 (장점: 토큰 유출 위험 감소, 단점: 스케일링/CSRF 고려 필요). 만약 세션 사용 시 CSRF 토큰 필요.

RBAC 및 권한
- role enum: ["admin","owner","editor","viewer"]
- Resource permission mapping: ventures: create/read/update/delete mapped by roles (문서화 필요: product to confirm)

파일 Presigned URL 정책
- 분류: public, internal, sensitive
  - public: 예) 공개 썸네일, TTL=15m (download), upload presign TTL=5m
  - internal: 예) 내부문서, TTL=5m (download), upload presign TTL=5m
  - sensitive: 예) PII, 계약서, TTL<=1m (download). 권장: presigned URL 사용 금지, backend streaming 또는 signed cookie 사용
- 업로드 presign (POST form 혹은 PUT): TTL=5분, max_size default=100MB (configurable), allowed content-types 화이트리스트(이미지/pdf/msword, etc.)
- 다운로드 presign (GET): 기본 TTL=15분, sensitive 파일은 60초
- 보안 제어:
  - presign 생성 시 반드시 발급자(user_id), resource_id, purpose, mime_type, max_size, jti를 로깅
  - presign은 단일-use 권장(업로드의 경우 form 필드로 체크) — 업로드 성공 시 backend에서 업로드 완료 콜백으로 presign 무효화
  - S3 설정: server-side encryption (SSE-S3 or SSE-KMS) 권장, 버킷에 public read 금지

API 스키마(핵심 필드)
- UUID 타입: string (uuid)
- Timestamps: string (date-time, ISO8601, UTC)
- Enums:
  - venture.status: ["draft","published","archived"]
  - user.roles: ["admin","owner","editor","viewer"]

샘플 엔드포인트(프론트가 바로 쓸 수 있는 샘플 JSON 응답 5종)
1) Ventures List (pagination)
{
  "meta": {"page": 1, "size": 20, "total": 137},
  "items": [
    {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "name": "Green Energy Fund", "slug":"green-energy-fund", "status":"published", "thumbnail_url":"https://cdn.example.com/thumbs/1.jpg", "owner_id":"8d7f3c4a-...", "tags":["energy","climate"], "created_at":"2026-03-01T12:34:56Z"},
    {"id": "a1b2c3d4-...", "name": "Healthcare Plus", "slug":"healthcare-plus", "status":"draft", "thumbnail_url":null, "owner_id":"...", "tags":[], "created_at":"2026-02-20T09:00:00Z"}
  ]
}

2) Venture Detail
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Green Energy Fund",
  "slug": "green-energy-fund",
  "status": "published",
  "description": "A fund investing in renewable energy projects.",
  "owner_id": "8d7f3c4a-1234-4a6b-9cde-111111111111",
  "tags": ["energy","climate"],
  "thumbnail_url": "https://cdn.example.com/thumbs/1.jpg",
  "files": [
    {"file_id":"f1e2d3c4-1111","name":"pitch-deck.pdf","size":2345678,"content_type":"application/pdf","uploaded_at":"2026-03-01T12:30:00Z","download_presign_expires_in":900}
  ],
  "created_at": "2026-03-01T12:34:56Z",
  "updated_at": "2026-03-02T08:00:00Z"
}

3) Auth Login Success
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 900,
  "user": {"id":"8d7f3c4a-1234-4a6b-9cde-111111111111","email":"alice@example.com","roles":["owner"]}
}

- 추가: 서버는 Set-Cookie: refresh_token=<opaque>; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=604800

4) Upload Presign Response (for PUT or POST form)
{
  "upload_id": "u-12345",
  "method": "PUT",
  "url": "https://s3.amazonaws.com/bucket/uploads/3fa85f64-u-12345",
  "headers": {"Content-Type":"application/pdf","x-amz-server-side-encryption":"AES256"},
  "expires_in": 300
}

(또는 POST 폼일 경우)
{
  "upload_id": "u-12345",
  "method": "POST",
  "url": "https://s3.amazonaws.com/bucket",
  "fields": {"key":"uploads/3fa85f64-u-12345","policy":"<base64>","x-amz-signature":"..."},
  "expires_in": 300
}

5) Download Presign Response
{
  "file_id": "f1e2d3c4-1111",
  "url": "https://s3.amazonaws.com/bucket/uploads/3fa85f64-f1e2d3c4?X-Amz-Algorithm=...",
  "expires_in": 900,
  "content_type": "application/pdf",
  "disposition": "attachment"
}

보안/운영 고려사항(요약)
- 모든 민감한 엔드포인트에 대해 rate limit 적용(유저당 10req/min 기본), 로그에 user_id/jti/purpose 기록
- 토큰 사용시 Revoke 리스트 확인 비용을 최소화하려면 access token은 짧게 하고 refresh로 상태관리
- Presign 생성 API는 반드시 인증(Authorization: Bearer) 필요, 권한 확인 후 발급
- 모니터링: presign 발급 횟수, 실패율, 다운로드 트래픽을 모니터링하여 이상행위 탐지

다음 단계
- OpenAPI 스펙을 생성했음 → output/docs/openapi_ventures.yaml (프론트용)
- 이 문서를 기반으로 프론트는 mock 데이터/컴포넌트를 구현 가능

