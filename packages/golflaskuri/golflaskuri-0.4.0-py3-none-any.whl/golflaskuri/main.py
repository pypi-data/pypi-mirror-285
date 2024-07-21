from dataclasses import dataclass
from importlib.abc import Traversable
import json
from typing import Optional, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import jinja2
from pathlib import Path
import pkgutil
from importlib import resources
from . import clubs  # type: ignore
import requests


@dataclass
class Player:
    name: str
    hcp: float


@dataclass
class Tee:
    id: str
    name: str
    length: int
    rating_men: float
    slope_men: int


@dataclass
class Course:
    name: str
    tees: List[Tee]
    par: int


def parse_courses(club_name: str, club_data: dict) -> List[Course]:
    courses = []
    for course in club_data:
        tees = [
            Tee(
                t["id"],
                t["name"],
                t["length"],
                t["rating_men"],
                t["slope_men"],
            )
            for t in course["tees"]
        ]
        par = sum([t["hole_par"] for t in course["holes"]])
        name = f"{club_name} - {course['name']}" if course["name"] else club_name
        courses.append(Course(name, tees, par))
        print(f"Added course {name}")
    return courses


def read_courses_from_files(path: Traversable) -> List[Course]:

    courses = []
    for file in path.iterdir():
        with file.open("r") as f:
            course_data = json.load(f)
        courses.extend(parse_courses(file.name.removesuffix(".json"), course_data))
    return courses


def calculate_game_hcps(hcp: float, course: Course) -> List[dict]:
    game_hcps = []
    for tee in course.tees:
        game_hcps.append(
            {
                "tee": tee.name,
                "id": tee.id,
                "length": tee.length,
                "hcp": (((tee.slope_men * hcp) / 113) + tee.rating_men - course.par),
            }
        )
    return sorted(game_hcps, key=lambda t: t["length"])


clubs_dir = resources.files(clubs)
TEMPLATES = Jinja2Templates(
    env=jinja2.Environment(loader=jinja2.PackageLoader(__name__))
)
COURSES = read_courses_from_files(clubs_dir)

app = FastAPI()


def get_default_hcps() -> dict:
    return {
        "max": requests.get(
            "https://golfapiproxy.atk.works/api/1.0/golf/player/?memberno=32819&clubid=55"
        ).json()["rows"][0]["handicapActive"],
        "jesse": requests.get(
            "https://golfapiproxy.atk.works/api/1.0/golf/player/?memberno=2339&clubid=33"
        ).json()["rows"][0]["handicapActive"],
        "panu": requests.get(
            "https://golfapiproxy.atk.works/api/1.0/golf/player/?memberno=4752&clubid=12"
        ).json()["rows"][0]["handicapActive"],
        "tele": requests.get(
            "https://golfapiproxy.atk.works/api/1.0/golf/player/?memberno=33665&clubid=55"
        ).json()["rows"][0]["handicapActive"],
    }


def find_player_by_name(players, name):
    for player in players:
        if player["name"] == name:
            return player
    return None


def find_tee_by_name(tees, name):
    for tee in tees:
        if tee["tee"] == name:
            return tee
    return None


def calculate_scramble_hcp(
    player_datas: List[dict], player1: str, player2: str
) -> float:
    player1_data = find_player_by_name(player_datas, player1)
    player2_data = find_player_by_name(player_datas, player2)
    assert player1_data is not None
    assert player2_data is not None
    player1_game_hcp = find_tee_by_name(
        player1_data["game_hcps"], player1_data["tee_choice"]
    )["hcp"]
    player2_game_hcp = find_tee_by_name(
        player2_data["game_hcps"], player2_data["tee_choice"]
    )["hcp"]
    return min(
        player1_game_hcp,
        player2_game_hcp,
        int((player1_game_hcp + player2_game_hcp) / 4),
    )


@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    max_hcp: Optional[float] = None,
    jesse_hcp: Optional[float] = None,
    panu_hcp: Optional[float] = None,
    tele_hcp: Optional[float] = None,
    course_name: Optional[str] = None,
    max_tee: Optional[str] = None,
    jesse_tee: Optional[str] = None,
    panu_tee: Optional[str] = None,
    tele_tee: Optional[str] = None,
):
    default_hcps = {}
    if max_hcp is None or jesse_hcp is None or panu_hcp is None or tele_hcp is None:
        default_hcps = get_default_hcps()
    else:
        default_hcps = {
            "max": max_hcp,
            "jesse": jesse_hcp,
            "panu": panu_hcp,
            "tele": tele_hcp,
        }
    hcp_query = f"max_hcp={max_hcp or default_hcps['max']}&jesse_hcp={jesse_hcp or default_hcps['jesse']}&panu_hcp={panu_hcp or default_hcps['panu']}&tele_hcp={tele_hcp or default_hcps['tele']}"
    if course_name is None:
        player_datas = [
            {
                "name": "max",
                "hcp": max_hcp if max_hcp is not None else default_hcps["max"],
            },
            {
                "name": "jesse",
                "hcp": jesse_hcp if jesse_hcp is not None else default_hcps["jesse"],
            },
            {
                "name": "panu",
                "hcp": panu_hcp if panu_hcp is not None else default_hcps["panu"],
            },
            {
                "name": "tele",
                "hcp": tele_hcp if tele_hcp is not None else default_hcps["tele"],
            },
        ]
        return TEMPLATES.TemplateResponse(
            request=request,
            name="course_select.html",
            context={
                "courses": COURSES,
                "players": player_datas,
            },
        )

    course = next((c for c in COURSES if c.name == course_name), None)
    if course is None:
        return RedirectResponse(url="/?{hcp_query}")
    player_datas = [
        {
            "name": "max",
            "hcp": max_hcp if max_hcp is not None else default_hcps["max"],
            "game_hcps": calculate_game_hcps(
                max_hcp if max_hcp is not None else default_hcps["max"], course
            ),
            "tee_choice": max_tee,
        },
        {
            "name": "jesse",
            "hcp": jesse_hcp if jesse_hcp is not None else default_hcps["jesse"],
            "game_hcps": calculate_game_hcps(
                jesse_hcp if jesse_hcp is not None else default_hcps["jesse"], course
            ),
            "tee_choice": jesse_tee,
        },
        {
            "name": "panu",
            "hcp": panu_hcp if panu_hcp is not None else default_hcps["panu"],
            "game_hcps": calculate_game_hcps(
                panu_hcp if panu_hcp is not None else default_hcps["panu"], course
            ),
            "tee_choice": panu_tee,
        },
        {
            "name": "tele",
            "hcp": tele_hcp if tele_hcp is not None else default_hcps["tele"],
            "game_hcps": calculate_game_hcps(
                tele_hcp if tele_hcp is not None else default_hcps["tele"], course
            ),
            "tee_choice": tele_tee,
        },
    ]

    scramble_hcps: Optional[List[dict]] = None

    if (
        max_tee is not None
        and jesse_tee is not None
        and panu_tee is not None
        and tele_tee is not None
    ):
        scramble_hcps = [
            {
                "teams": ["Max & Jesse", "Panu & Tele"],
                "hcps": [
                    calculate_scramble_hcp(player_datas, "max", "jesse"),
                    calculate_scramble_hcp(player_datas, "panu", "tele"),
                ],
            },
            {
                "teams": ["Max & Panu", "Jesse & Tele"],
                "hcps": [
                    calculate_scramble_hcp(player_datas, "max", "panu"),
                    calculate_scramble_hcp(player_datas, "jesse", "tele"),
                ],
            },
            {
                "teams": ["Max & Tele", "Jesse & Panu"],
                "hcps": [
                    calculate_scramble_hcp(player_datas, "max", "tele"),
                    calculate_scramble_hcp(player_datas, "jesse", "panu"),
                ],
            },
        ]

    return TEMPLATES.TemplateResponse(
        request=request,
        name="handicaps.html",
        context={
            "course": course,
            "players": player_datas,
            "hcp_query": hcp_query,
            "scramble_hcps": scramble_hcps,
        },
    )
