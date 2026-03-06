요약

이 문서는 프론트엔드 Kevin이 만든 frontend component spec에 대해 보안 관점에서 필요한 API 형태(스키마), 인증 방식 결정을 위한 권장안, 파일 다운로드 URL(사인 URL) 정책 및 샘플 응답 템플릿을 정리합니다. Marcus(백엔드)에게 API 필드/타입/enum 확정과 샘플 JSON 또는 mock 엔드포인트 제공을 요청합니다.

핵심 요구(정리)

- API 스키마 확정: 각 엔드포인트의 요청/응답 필드, 타입, enum 값(가능한 값 목록) 제공
- 인증 방식 확정: Bearer JWT vs Cookie 기반 세션 (보안 권고 포함)
- 파일 URL 정책: 업로드/다운로드 흐름(사인 URL 제공 여부, 만료시간, 제한된 메서드 등)
- 샘플 JSON/Mock: 프론트 개발을 위한 가능한 샘플 응답 또는 mock 엔드포인트

MECE 분해(보안 관점)

1) 인증·인가 (Authentication & Authorization)
   - 접근 토큰 형식 및 저장 위치 (Bearer JWT vs Cookie HttpOnly)
   - 토큰 수명, 리프레시 전략(회전, 블랙리스트)
   - 권한 모델(RBAC 또는 scope 기반)과 권한 필드 예시
   - CORS, CSRF, SameSite 설정

2) 파일 업로드/다운로드
   - 업로드: 직접 서버 업로드 vs 프리사인(프론트→S3) 방식
   - 다운로드: 프리사인 URL 사용(만료, method GET 제한)
   - 서명 생성 정책: 생성 권한, 로깅, 만료, 재생 공격 방지
   - 민감 파일 분류(PII 여부) 및 추가 암호화 필요성

3) API 스키마와 응답 모양
   - 엔드포인트 목록 + 요청/응답 필드 제안
   - 오류 모델(공통 에러 포맷, HTTP 상태 코드)
   - 샘플 JSON 페이로드(프론트가 곧바로 사용 가능)

4) 위협 모델 요약(STRIDE 하이라이트)
   - Spoofing: 토큰 탈취 방지
   - Tampering: 사인 URL 변조 방지
   - Information Disclosure: 민감 데이터 노출 방지
   - 기타: DoS, Repudiation 로깅 요구

권장 보안 아키텍처(결론 — 빠르게 적용 권장)

- 인증 방식(권장): 혼합 접근 — Access Token은 짧은 수명의 Bearer JWT(예: 15분), Refresh Token은 HttpOnly Secure SameSite=strict 쿠키로 저장(리프레시 토큰은 7일, 회전 적용).
  - 이유: SPA(프론트)에서 Authorization 헤더로 Bearer 사용하면 CORS에 명확하고 API 게이트웨이/마이크로서비스 간 전달이 쉬움.
  - 쿠키에 리프레시 토큰을 보관하면 XSS로부터 보호(토큰 노출 위험 감소)되고 CSRF는 SameSite/CSRF 토큰으로 추가 방어.
  - 대안(단일 선택): 만약 세션 기반이 선호되면 서버 세션 + HttpOnly 쿠키로 구현하되, 확장성(세션 스토리지) 고려.

- 토큰 관리:
  - Access token 만료: 15분 (권장)
  - Refresh token 만료: 7일
  - Refresh token rotation: 매 리프레시 시 새로운 refresh token 발급하고 이전 토큰을 무효화
  - 즉시 로그아웃/세션 리보크를 위한 단기 블랙리스트(캐시)에 토큰 ID 저장(예: Redis)

- 파일 URL 정책:
  - 업로드: 클라이언트 요청 → 백엔드가 사전 검증(사용자 권한, 파일 메타 검증, 허용된 MIME/확장자/크기) → 스토리지(S3) presigned POST/PUT URL 발급(업로드 전 서버에 파일 메타 저장 및 파일 ID 발행)
  - 업로드 만료시간: 짧게(예: 5분)
  - 다운로드: presigned GET URL 발급(또는 파일 접근을 프록시하여 인증 검증 후 전달)
  - 다운로드 만료시간: 컨텐츠 민감도에 따라 5분~15분 권장
  - presigned URL 제한: method GET/PUT만 허용, IP 제한(가능하면), 서명에 file_id 포함
  - 민감 데이터: S3 서버사이드 암호화(SSE) + 옵션으로 필드 수준 암호화

- 로그·감사:
  - 사인 URL 생성/사용 이벤트 로깅(누가, 언제, 어떤 파일 ID, 소스 IP)
  - 토큰 발급/리프레시/리보크 로그

API 엔드포인트 제안(샘플)

1) 인증
- POST /api/v1/auth/login
  - 요청: { "email": string, "password": string }
  - 응답: {
      "access_token": "<jwt>",
      "token_type": "Bearer",
      "expires_in": 900,
      "user": { "id": "uuid", "email": "...", "roles": ["..." ] }
    }
  - 보안: 로그인 성공 시 refresh token은 HttpOnly cookie로 설정(Set-Cookie)

- POST /api/v1/auth/refresh
  - 요청: (쿠키로 refresh token 전달)
  - 응답: { "access_token": "<jwt>", "expires_in": 900 }

- POST /api/v1/auth/logout
  - 요청: (쿠키 포함)
  - 응답: 204 No Content (서버에서 refresh token 무효화)

2) 벤처 데이터
- GET /api/v1/ventures
  - 요청: Authorization: Bearer <token>
  - 응답: { "items": [ { "id": "uuid", "name": "string", "stage": "SEED|SERIES_A|...", "logo_url": "https://..." } ], "meta": { "page":1, "per_page":20 } }

- GET /api/v1/ventures/{id}
  - 응답: { "id": "uuid", "name": "string", "description": "string", "industry": "enum", "attachments": [{"id":"uuid","type":"image|pdf","download_url": "https://..." }] }

3) 파일 업로드/다운로드
- POST /api/v1/ventures/{id}/attachments/request-upload
  - 요청: { "filename": "string", "content_type": "image/png", "size": 12345 }
  - 응답: { "file_id": "uuid", "upload_url": "https://s3....?X-Amz-Signature=..", "expires_at": "ISO8601" }
  - 보안: 백엔드에서 사용자 권한 및 파일 메타 검증 후 발급

- GET /api/v1/attachments/{file_id}/request-download
  - 요청: Authorization: Bearer <token>
  - 응답: { "file_id": "uuid", "download_url": "https://s3....?X-Amz-Signature=..", "expires_at": "ISO8601" }

오류 포맷(공통)
- { "error": { "code": "invalid_credentials", "message": "...", "status": 401 } }

위협 모델(요약)
- Spoofing: 토큰 탈취 -> HTTPS 강제화, HttpOnly refresh cookie, short-lived access token
- Tampering: presigned URL 변조 -> 서명 검증(스토리지 제공자), URL 만료, 메서드 제한
- Info disclosure: 민감파일 CDN 캐시 정책, SSE 적용
- Repudiation: 주요 이벤트(발급/리프레시/사인URL생성/사용) 감사로그

결정 품질 메모(Trade-offs)
- Bearer JWT in localStorage: 쉬운 사용성, 하지만 XSS에 취약. 그래서 권장하지 않음.
- Access token in memory + refresh cookie: XSS 위험 ↓, CSRF 위험은 남음 → CSRF 토큰 적용 또는 SameSite=strict 권장.
- 완전 서버세션 방식: 보안성 높으나 확장성(세션 스토어 필요)과 API 게이트웨이 전달이 번거로움.

요청사항(Marcus에게)
1) API 스키마 확정: 위 샘플 엔드포인트의 정확한 필드/타입/enum 값(특히 venture.stage, industry 등) 제공
2) 인증 방식 확정: 위 권장안(Access JWT 15m + Refresh HttpOnly cookie)을 수용할지, 또는 Cookie 세션을 선택할지 회신
3) 파일 URL 정책 확정: presigned 사용 여부, 업로드/download 만료 시간, 민감도 분류 기준
4) 샘플 JSON/Mock 엔드포인트: 프론트가 바로 사용 가능한 최소 5개 샘플 응답(ventures 목록, venture detail, upload request 응답, download request 응답, auth login 성공)

우선 순위: P1 (프론트 개발 블로킹 요소)

참고(보안 체크리스트 요약)
- 모든 토큰/쿠키는 Secure + HttpOnly(가능한 경우) 설정
- HTTPS 강제(redirect/ HSTS)
- CSP, X-Content-Type-Options, X-Frame-Options 헤더 적용
- 입력값 검증 및 업로드 파일 유형/크기 제한
- S3 presigned URL은 최소 권한(생성 권한만) 발급
- 감사 로그 보존 정책(예: 90일) 및 모니터링 알림

파일 위치
- 이 문서: output/specs/security_auth_and_fileurl_spec.md

