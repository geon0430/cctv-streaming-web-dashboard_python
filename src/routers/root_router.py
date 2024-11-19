from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

root = APIRouter()

templates = Jinja2Templates(directory="/cctv-streaming-web-dashboard_python/src/web/templates")

@root.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})
