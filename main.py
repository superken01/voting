from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import starlette.status as status
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

voting_open = True
voting_result = {"red": 0, "blue": 0}
voters = {}


@app.get("/vote")
async def get_vote(request: Request, voter_id: int = Query(1)):
    global voting_open, voting_result, voters
    print('get', voters)
    return templates.TemplateResponse(
        "vote.html", {
            "request": request,
            'voter_id': voter_id,
            'voted_ids': list(voters.keys()),
            'voting_open': voting_open
        })


@app.post("/vote")
async def post_vote(request: Request,
                    voter_id: int = Form(...),
                    red_count: int = Form(...),
                    blue_count: int = Form(...)):
    global voting_open, voting_result, voters
    if voting_open:
        if voter_id not in voters:
            voting_result['red'] += red_count
            voting_result['blue'] += blue_count
            voters[voter_id] = {"red": red_count, "blue": blue_count}
    print('post', voters)
    return RedirectResponse(url=f"/vote?voter_id={voter_id}",
                            status_code=status.HTTP_302_FOUND)


@app.get("/results")
async def get_results(request: Request):
    global voting_open, voting_result, voters
    return templates.TemplateResponse(
        "results.html", {
            "request": request,
            "voting_open": voting_open,
            "voting_result": voting_result,
            "voters": voters
        })


@app.get("/admin")
async def get_admin(request: Request):
    global voting_open, voting_result, voters
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "voting_open": voting_open
    })


@app.post("/admin")
async def post_admin(
        request: Request,
        operation: str = Form(...),
):
    global voting_open, voting_result, voters

    if operation == 'close':
        voting_open = False
    elif operation == 'reset':
        voting_open = True
        voting_result = {"red": 0, "blue": 0}
        voters = {}

    return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
