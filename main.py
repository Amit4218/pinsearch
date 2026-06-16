from typing import Annotated

from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from cron.update_pincode_data import pincode_update_job
from pinsearch_sdk import PinSearch, PincodeData 
from schema.response_schemas import PincodeNotFound, PublicApiResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from settings import settings
from pathlib import Path


scheduler = BackgroundScheduler()
file_path = Path(f"{settings.DOWNLOAD_DIR}/pincode_data.json")
client = PinSearch(pincode_file=file_path)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    if not file_path.exists():
        pincode_update_job()
        
    scheduler.add_job(
        func=pincode_update_job,
        trigger="cron",
        day=1,
        hour=0,
        minute=0,
        id="pincode_update_job",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore[arg-type]


template = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return template.TemplateResponse(
        request=request,
        name="404.html",
        context={"message": "Page not found"},
        status_code=404,
    )


@app.get("/root/health")
async def root():
    return {"status": "ok","data_file_exists": file_path.exists()}

@app.get("/")
async def home(req: Request):
    return template.TemplateResponse(request=req, name="pages/home.html")


@app.get("/api-docs")
async def api_docs(req: Request):
    return template.TemplateResponse(request=req, name="pages/api.html")


@app.get("/sdk-docs")
async def sdk_docs(req: Request):
    return template.TemplateResponse(request=req, name="pages/sdk.html")


@app.get("/api/v1/pincode",response_model=PincodeData | PincodeNotFound,)
@limiter.limit("120/minute")
async def fetch_code_data(
    request:Request,
    q: Annotated[str, Query(pattern=r"^\d{6}$")]
) -> PincodeData | PincodeNotFound:
    
    result = client.get(pincode=q)
    if result:
        return result
    return PincodeNotFound(message="Pincode not found. Please verify the numbers and try searching again.")



@app.get("/api/v1/public", response_model=PublicApiResponse, response_model_exclude_none=True)
@limiter.limit("30/minute;1000/day")
async def fetch_information(
    request:Request,
    code: str | None = None,
    state_name: str | None = None,
    district: str | None = None,
) -> PublicApiResponse:
    
    data = {}

    if code:
        result = client.get(pincode=code)
        if result:
            data["pincode_data"] = result

    if state_name:
        result = client.by_state(state_name=state_name)
        if result:
            data["state_data"] = result

    if district:
        result = client.by_district(district=district)
        if result:
            data["district_data"] = result

    return PublicApiResponse(**data)