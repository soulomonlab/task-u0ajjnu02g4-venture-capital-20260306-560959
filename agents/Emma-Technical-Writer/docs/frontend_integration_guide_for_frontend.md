# Frontend Integration Guide — 확인 요청

요약
- 목적: 프론트엔드가 백엔드 API와 파일 업로드/다운로드 흐름을 정확히 구현하도록 필요한 정보와 확인 항목을 정리합니다.
- 현재 상태: Marcus(백엔드)가 백엔드 확인 문서를 제공(엔드포인트/스키마/인증/파일 URL 정책 포함). 본 문서는 프론트엔드에서 확정해야 할 항목과 구현 예시를 정리합니다.

핵심 백엔드 결정(현재 기준)
- 인증: Bearer JWT (Authorization: "Bearer <token>")
- 파일 업로드/다운로드: presigned URL 사용(기본 만료 시간: 300초)
- CORS: 스토리지(예: S3)에는 프론트엔드 origin을 허용해야 함(정확한 origin 필요)

빠른 구현 예시 (Quickstart)
1) 인증 헤더 예
- 요청 예: GET /api/v1/me
  - 헤더: Authorization: Bearer eyJhbGciOiJI...

2) presign 기반 업로드 (권장)
- 흐름:
  1. 프론트엔드에서 백엔드로 presign 요청: GET /api/v1/uploads/presign?filename=avatar.png&contentType=image/png
  2. 백엔드 반환: presigned URL (PUT 또는 POST) 및(선택적) form 필드
  3. 프론트엔드가 presigned URL로 직접 업로드
  4. 업로드 완료 후 프론트엔드가 백엔드에 메타데이터(파일 키, URL, 크기 등) 저장 요청
- presign 응답 예 (JSON):
  {
    "method": "PUT",
    "url": "https://bucket.s3.amazonaws.com/user-uploads/abcd1234",
    "headers": {
      "Content-Type": "image/png"
    },
    "expires_in": 300
  }
- 업로드 완료 후 백엔드에 보낼 메타데이터 예:
  {
    "fileKey": "user-uploads/abcd1234",
    "fileName": "avatar.png",
    "contentType": "image/png",
    "size": 12345
  }

3) presigned download
- 백엔드가 파일을 직접 서빙하지 않고 presigned GET URL을 반환하는 경우:
  GET /api/v1/uploads/{fileId}/download -> { "url": "https://bucket.s3.amazonaws.com/...?..." , "expires_in": 300 }
- 프론트엔드는 이 URL을 사용해 직접 다운로드(또는 이미지 태그 src에 삽입) 가능

프론트엔드 의사결정(확인 필요)
1) API 필드/타입/enum 확정
   - Marcus가 보낸 백엔드 문서에 정의된 각 엔티티의 필드(이름/타입/nullable 여부/enum 값)를 프론트엔드에서 확인해 주세요.
   - 예: User.profilePicture: { type: string, nullable: true, format: URL }
2) 파일 업로드 선호 방식
   - 옵션 A: presigned direct upload (권장 — 백엔드 비용/성능 이점)
   - 옵션 B: proxy upload via backend (간편성, 인증 제어 유리)
   - 프론트엔드에서 선호하는 방식과 이유(브라우저 제약, CORS, 추적, 리사이징 요구 등)를 알려주세요.
3) 프론트엔드 origin 목록 (CORS)
   - 스토리지에 허용해야 하는 origin 목록(개발/스테이징/프로덕션)을 제공해주세요.
4) Mock endpoints 필요 여부
   - 로컬 개발/스토리북/인터널 QA용 mock endpoint(또는 JSON 스텁) 필요하신가요? 필요하다면 요청하실 엔드포인트 목록을 주세요.
5) 에러 처리/UX 정책
   - 파일 업로드 실패 시 재시도 정책(자동 재시도 횟수), 사용자 알림 방식(토스트/모달) 등 표준을 알려주세요.

Acceptance criteria (프론트엔드에서 응답하면 완료로 간주)
- 각 API 엔티티에 대해 필드 이름/타입/enum 값/nullable 여부를 명시적으로 승인(또는 변경 요청)
- 파일 업로드 방식(presigned vs proxy) 선택 및 이유
- 스토리지에 허용할 프론트엔드 origin 목록(개발/스테이징/프로덕션)
- Mock endpoint 필요 여부 및 필요한 엔드포인트 목록
- 에러 처리/재시도 정책 합의

의존성 및 참고
- Marcus(백엔드)가 제공한 API 스펙(엔드포인트/샘플 JSON/응답 코드) 참고 필요 — 구현 세부 필드 확인 시 Marcus와 동기화 필요

다음 단계
- 프론트엔드 소유자(또는 담당자)가 위의 5개 확인 항목에 대해 회신하면 백엔드와 최종 스키마/정책을 확정하여 문서화하겠습니다.

작성자: Emma (Technical Writer)
상태: 요청 중 — 프론트엔드 확인 필요
