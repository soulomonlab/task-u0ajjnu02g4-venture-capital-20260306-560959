결론
- 프론트용으로 확정한 핵심 API 요약(엔드포인트, 필드/타입, 인증 방식)과 샘플 JSON mock 파일을 생성함.

세부
- Auth: Bearer JWT access(15m) + Refresh HttpOnly cookie(7d, rotation). 로그인 응답은 access token + Set-Cookie refresh.
- File presign: upload TTL=300s, download TTL=900s (민감도에 따라 축소). 민감 파일은 presign 금지 권장.
- Ventures 엔드포인트: /api/v1/ventures (GET), /api/v1/ventures/{id} (GET)

파일 생성 위치
- API 스펙: output/docs/openapi_ventures.yaml
- 보안/정책 확인 문서: output/specs/security_auth_and_fileurl_backend_confirm.md
- 샘플 mock JSON: output/docs/mock_responses_ventures.json

프론트에 필요한 추가 설명
- 모든 요청은 Authorization: Bearer <access_token> 필요(로그인 후 헤더 설정).
- 로그인은 /api/v1/auth/login, 응답 바디에 access_token, refresh cookie가 Set-Cookie로 내려옴.
- presign 흐름: 1) POST /api/v1/files/upload-presign (file meta) -> 2) S3로 PUT/POST -> 3) 콜백 또는 검증 API로 업로드 완료 확인

다음 단계
- #ai-frontend (Kevin)에게 mock 파일과 OpenAPI 제공. 구현 중 추가 필드/에러케이스 요청 시 바로 대응.

