from fastapi import APIRouter


from .meme.views import router as meme_router

router = APIRouter()

router.include_router(meme_router, prefix='/meme', tags=["Meme"])