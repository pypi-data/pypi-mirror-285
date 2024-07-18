from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from starlette.responses import JSONResponse
from qg_toolkit.cf_turnstile.cf_turnstile import CFTurnstileSolver
class CaptchaRequest(BaseModel):
    site_key: str
    target_url: str
    headless: bool

class CFTurnstileSolverFastAPIClient:

    def __init__(self):
        # self.cf_solve = CFTurnstileSolver(site_key, target_url, headless=headless, proxy=proxy)
        self.app = FastAPI()
        self.add_routes()

    def add_routes(self):
        @self.app.get("/")
        def index():
            return {"message": "QGX"}

        @self.app.post("/solve")
        async def solve(background_tasks: BackgroundTasks, captcha_req: CaptchaRequest):
            site_key = captcha_req.site_key
            target_url = captcha_req.target_url
            headless = captcha_req.headless
            cf_token = await solve_captcha(site_key, target_url, headless)
            return {"status": "success", "token": cf_token}

        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request, exc):
            return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})

    def start(self, port=5555):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=port)


async def solve_captcha(site_key: str, target_url: str, headless: bool) -> str:
    print(f"[CF_TOKEN]开始破解: site_key={site_key}, target_url={target_url},headless={headless}")
    cf_solve = CFTurnstileSolver(site_key, target_url, headless=headless, proxy=None)
    cf_token = await cf_solve.solve()
    print(f"[CF_TOKEN]破解成功: {cf_token}")
    await cf_solve.close_browser()
    return cf_token


if __name__ == "__main__":
    fastapi_client = CFTurnstileSolverFastAPIClient()
    fastapi_client.start(port=5555)