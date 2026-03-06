요약

이 문서는 프론트엔드-백엔드 통합 시 ML/추론 엔드포인트가 요구하는 명세와 제약을 정리합니다. 목표는 프론트엔드가 서버로 보낼 페이로드(또는 파일 업로드)와 서버가 반환할 응답, 인증, 파일 업로드 방식(사인 URL 등), 성능·검증 기준을 명확히 하여 재작업을 줄이는 것입니다.

핵심 결정(사전 승인된 사항)
- 인증: Bearer JWT 사용 (Authorization: Bearer <token>) — 기존 백엔드 표준과 일관화 필요
- 파일 업로드/다운로드: presigned URL 사용 권장, 기본 만료 300초(필요시 조정) — 프론트엔드에서 직접 S3 등 스토리지로 PUT/POST
- 모델 버전관리: 응답 헤더 혹은 JSON 필드로 model_version 제공 (예: "model_version": "v1.2.0")

요구 사항 (MECE)
1) 입력(Input) 스키마 — 실시간 추론(POST /api/v1/predict)
   - content-type: application/json
   - body fields:
     - request_id: string (uuid, optional but 권장) — 추적용
     - model: string (enum) — 예: ["image_classification", "object_detection"] 또는 default 생략 가능
     - inputs: object — 모델 유형별 구조:
       - image_classification: { "image_url": string | null, "image_base64": string | null }
         - image_url과 image_base64 중 하나 반드시 존재
       - text_classification: { "text": string }
     - metadata: object (optional) — {"user_id": string, "timestamp": ISO8601}
   - validation rules:
     - 이미지 최대 파일 크기(업로드 전): 5MB
     - 텍스트 길이: max 32k chars (truncate, 또는 4000 chars 권장)
     - 허용 이미지 포맷: jpeg, png, webp

2) 파일 업로드 플로우 (이미지/큰 바이너리)
   - 권장: presigned PUT/POST URL 발급 엔드포인트 (POST /api/v1/uploads/presign)
     - request: { "filename": string, "content_type": string, "purpose": string }
     - response: { "upload_url": string, "file_url": string, "expires_in": int }
     - expires_in 기본 300 (초)
   - 대안: 프록시 업로드 엔드포인트 (백엔드가 스트리밍 받아 스토리지에 저장) — 보안/세분화된 권한 필요, 부하 증가
   - 프론트엔드 의사결정 포인트: 직접 업로드 시 CORS 허용 origin 목록 필요

3) 응답(Response) 스키마
   - content-type: application/json
   - common fields:
     - request_id: string (echo) — 추적 일관화
     - model_version: string
     - predictions: object — 모델별 스키마
       - image_classification: [{ "label": string, "score": float }]
       - object_detection: [{ "label": string, "score": float, "bbox": [x1,y1,x2,y2] }]
     - inference_time_ms: int
     - warnings/errors: array (optional)
   - HTTP status codes: 200(성공), 400(잘못된 입력), 401(인증 실패), 413(payload too large), 500(서버 에러)

4) 성능·운영 요구
   - latency target: p95 < 50ms (경량 모델), p95 < 200ms(복잡 모델) — 서비스 수준 합의 필요
   - payload size: 이미지 업로드는 presigned로 제한, API 전달 JSON은 작게 유지
   - 로깅: 요청/응답 메타(사생활 보호 고려) + model_version, model_latency, error_code
   - 모니터링: ML 성능(정확도 지표) + 인프라(호출률, 에러율, latency)

5) 보안/프라이버시
   - 민감 데이터 전송 금지(PII) — 수집할 경우 암호화 및 저장 정책 필요
   - presigned URL은 짧게 만료, purpose 필드로 업로드 용도 구분

샘플 JSON
- 추론 요청 (이미지 presigned flow):
  1) presign 요청: { "filename": "img_123.jpg", "content_type": "image/jpeg", "purpose": "inference_image" }
  2) presign 응답: { "upload_url": "https://...", "file_url": "https://cdn/.../img_123.jpg", "expires_in": 300 }
  3) 업로드 -> 추론 요청:
     POST /api/v1/predict
     body: { "request_id": "uuid-123", "model": "image_classification", "inputs": { "image_url": "https://cdn/.../img_123.jpg" }, "metadata": {"user_id":"u-1"} }

- 직접 base64 전달 예시 (소형 이미지/개발용):
  POST /api/v1/predict
  body: { "request_id": "uuid-123", "model": "image_classification", "inputs": { "image_base64": "..." } }

Acceptance criteria (QA/프론트와 합의 필요)
- API 필드 및 타입이 사양 문서와 일치해야 함
- 인증(Authorization: Bearer <token>)으로 401 처리 테스트
- presigned URL 발급 → 프론트엔드 직접 업로드 성공(HTTP 200/201) 확인
- 예시 이미지(<=5MB)로 전체 플로우(업로드→추론)를 end-to-end로 검증
- 응답에 model_version과 inference_time_ms 포함

프론트엔드에 확인 요청 (구체적 질문)
1) 파일 업로드 방식 우선순위: presigned 직접 업로드 vs 백엔드 프록시 업로드 중 선호는?
2) 프론트엔드 호스트(origin) 목록 — 스토리지 CORS에 추가할 도메인
3) Mock 엔드포인트 필요 여부(예: dev/staging용) 및 원하는 mock 스펙
4) 실시간 응답성 요구(예: p95 < 50ms) 수용 가능 여부 및 UX 타협점
5) 사용자가 업로드하는 파일 최대 크기/포맷 제약 제안

결론 / 차후 작업
- 저는 ML 측 요구사항을 문서화했으며, 백엔드가 API 필드/인증/파일 정책을 확정하면 학습·서빙 파이프라인(모델 버전, 모니터링)과 추론 컨테이너 설정을 준비하겠습니다.

파일 경로: output/docs/ml_inference_integration_requirements.md
