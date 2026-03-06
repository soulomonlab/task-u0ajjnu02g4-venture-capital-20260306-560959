from fastapi import FastAPI
from engagement_links import router as engagement_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Investor Engagement API')
app.include_router(engagement_router, prefix='/api/v1')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
async def root():
    return {'status': 'ok'}
