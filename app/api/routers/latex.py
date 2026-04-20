from fastapi import APIRouter
from fastapi.responses import Response

from app.schemas import FullProfile
from app.services.latex_engine import generate_latex_content

router = APIRouter(prefix="/latex", tags=["LaTeX"])

@router.post("/generate")
async def generate_latex(profile: FullProfile):
    tex_content = generate_latex_content(profile)
    return Response(content=tex_content, media_type="application/x-tex", headers={"Content-Disposition": "attachment; filename=profile.tex"})
