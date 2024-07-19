import argparse
import json
import os
from time import time

import requests

from .colors import C

TRIPS_URL: str = "https://yamtam.nyc/trips.json"
DATA_URL: str = "https://yamtam.nyc/data.json"
TRIPS_FILE: str = "/tmp/trips.json"
DATA_FILE: str = "/tmp/data.json"
ONE_DAY_IN_MINS: int = 24 * 60 * 60


def get_json_feed(url: str) -> dict:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the JSON feed: {e}")
        return {}


def download_json_feed(url: str, file: str):
    data: dict = get_json_feed(url)
    with open(file, "w") as f:
        f.write(json.dumps(data))


def too_old(file: str, minutes: int = 2) -> bool:
    seconds_in_minute: int = 60
    last_mod: int = 0
    if not os.path.exists(file):
        return True
    last_mod = os.path.getmtime(file)
    return False if time() - last_mod < (minutes * seconds_in_minute) - 5 else True


def stop_times(
    trips: dict, stop: str, routes: list[str] = ["ALL"], clock: int = 0
) -> dict:
    if clock == 0:
        clock = time()
    max_mins: int = 40
    if stop.find("MNR") == 0:
        max_mins = 180
    elif stop.find("LIRR") == 0:
        max_mins = 120
    elif stop.find("NJT") == 0:
        max_mins = 60
    block: dict = {}
    mins: int = 0
    if not stop in trips["trips"]:
        return block
    for info in trips["trips"][stop]:
        mins = int((info["arr"] - clock) / 60)
        if (
            mins >= 0
            and mins <= max_mins
            and (routes[0] == "ALL" or info["rt"] in routes)
        ):
            if info["rt"] not in block:
                block[info["rt"]] = {}
            if info["dir"] not in block[info["rt"]]:
                block[info["rt"]][info["dir"]] = {}
            if info["to"] not in block[info["rt"]][info["dir"]]:
                block[info["rt"]][info["dir"]][info["to"]] = []
            block[info["rt"]][info["dir"]][info["to"]].append(mins)
    return block


def parse_stops(data: dict, stops: list[str]) -> list[str]:
    out: list[str] = []
    for gtfs_id, info in data["stations"].items():
        for stop in stops:
            if gtfs_id == stop or stop.lower() in info["name"].lower():
                out.append(gtfs_id)
                continue
    return out


def color_route(route: str) -> str:
    """
    NJT
    AIRTRAIN
    NYCF
    SIF
    """
    cmap: dict[str, str] = {
        "[1]": C.REDBG + C.WHITE,
        "[2]": C.REDBG + C.WHITE,
        "[3]": C.REDBG + C.WHITE,
        "[4]": C.GREENBG + C.BLACK,
        "[5]": C.GREENBG + C.BLACK,
        "[6]": C.GREENBG + C.BLACK,
        "[7]": C.VIOLETBG + C.WHITE,
        "[G]": C.GREENBG2 + C.WHITE,
        "[L]": C.GREYBG + C.WHITE,
        "[S]": C.GREYBG + C.WHITE,
        "[H]": C.GREYBG + C.WHITE,
        "[A]": C.BLUEBG + C.WHITE,
        "[C]": C.BLUEBG + C.WHITE,
        "[E]": C.BLUEBG + C.WHITE,
        "[J]": C.BEIGEBG + C.BLACK,
        "[Z]": C.BEIGEBG + C.BLACK,
        "[F]": C.YELLOWBG2 + C.BLACK,
        "[D]": C.YELLOWBG2 + C.BLACK,
        "[B]": C.YELLOWBG2 + C.BLACK,
        "[M]": C.YELLOWBG2 + C.BLACK,
        "[N]": C.YELLOWBG + C.BLACK,
        "[R]": C.YELLOWBG + C.BLACK,
        "[Q]": C.YELLOWBG + C.BLACK,
        "[W]": C.YELLOWBG + C.BLACK,
        "[LIRR1]": C.GREENBG + C.BLACK,
        "[LIRR2]": C.YELLOWBG + C.BLACK,
        "[LIRR3]": C.GREENBG + C.WHITE,
        "[LIRR4]": C.VIOLETBG + C.WHITE,
        "[LIRR5]": C.BLUEBG + C.WHITE,
        "[LIRR6]": C.REDBG + C.WHITE,
        "[LIRR7]": C.BEIGEBG + C.BLACK,
        "[LIRR8]": C.BLUEBG + C.WHITE,
        "[LIRR9]": C.REDBG + C.WHITE,
        "[LIRR10]": C.BLUEBG + C.WHITE,
        "[LIRR11]": C.VIOLETBG + C.WHITE,
        "[LIRR12]": C.GREYBG + C.WHITE,
        "[MNR1]": C.GREENBG + C.WHITE,
        "[MNR2]": C.BLUEBG + C.WHITE,
        "[MNR3]": C.REDBG + C.WHITE,
        "[MNR4]": C.REDBG + C.WHITE,
        "[MNR5]": C.REDBG + C.WHITE,
        "[MNR6]": C.REDBG + C.WHITE,
    }
    route_list: dict[str, str] = {
        "[LIRR1]": "Babylon",
        "[LIRR2]": "Hempstead",
        "[LIRR3]": "Oyster Bay",
        "[LIRR4]": "Ronkonkoma",
        "[LIRR5]": "Montauk",
        "[LIRR6]": "Long Beach",
        "[LIRR7]": "Far Rockaway",
        "[LIRR8]": "West Hempstead",
        "[LIRR9]": "Port Washington",
        "[LIRR10]": "Port Jefferson",
        "[LIRR11]": "Belmont Park",
        "[LIRR12]": "City Terminal",
        "[MNR1]": "Hudson",
        "[MNR2]": "Harlem",
        "[MNR3]": "New Haven",
        "[MNR4]": "New Canaan",
        "[MNR5]": "Danbury",
        "[MNR6]": "Waterbury",
    }
    color: str = cmap.get(route, "")
    final_route: str = route_list.get(route, route)
    return f"{color}{final_route}{C.X}"


def render(
    data: dict,
    trips: dict,
    systems: list[str] = [],
    stops: list[str] = [],
    routes: list[str] = [],
):
    if len(routes) == 0:
        routes = ["ALL"]

    times: dict = {}
    for stop in stops:
        times[stop] = stop_times(trips=trips, stop=stop, routes=routes)

    for stop, info in times.items():
        stop_name = data["stations"][stop]["name"]
        print(f"-- Times for: {stop} / {stop_name} --")
        for route, info2 in info.items():
            colored = color_route(f"[{route}]")
            for dxn, info3 in info2.items():
                seen_times: list = []
                for dest, times in info3.items():
                    a_times: list[int] = times[0:5]
                    a_times.sort()
                    dest_name = data["stations"][dest]["name"]
                    print(f"{colored: <17}", end="")
                    if len(colored) > 18 and len(colored) < 22:
                        print("\t", end="")
                    print(f"\t{dest_name: <30}", end="")
                    for a_time in a_times:
                        if a_time in seen_times:
                            continue
                        seen_times.append(a_time)
                        if a_time > 0:
                            if a_time < 3:
                                print(f"{C.GREEN}0{a_time}m{C.X} ", end="")
                            else:
                                print(
                                    ("0" if a_time < 10 else "") + f"{a_time}m ", end=""
                                )
                        else:
                            print(f"{C.YELLOW}0{a_time}m{C.X} ", end="")
                    print("")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rt", action="append", type=str, help="Repeated optional routes"
    )
    parser.add_argument(
        "--stop", action="append", type=str, help="Repeated optional stops"
    )
    parser.add_argument(
        "--system", action="append", type=str, help="Repeated optional systems"
    )
    args = parser.parse_args()

    if too_old(file=DATA_FILE, minutes=ONE_DAY_IN_MINS):
        download_json_feed(url=DATA_URL, file=DATA_FILE)
    if too_old(file=TRIPS_FILE):
        download_json_feed(url=TRIPS_URL, file=TRIPS_FILE)

    with open(DATA_FILE) as f:
        data: dict = json.loads(f.read())
    with open(TRIPS_FILE) as f:
        trips: dict = json.loads(f.read())

    routes: list[str] = ["ALL"]
    if args.rt is not None:
        routes = args.rt
    stops: list[str] = []
    if args.stop is not None:
        stops = parse_stops(data=data, stops=args.stop)
    systems: list[str] = ["subway"]
    if args.system is not None:
        systems = args.system

    render(
        data=data,
        trips=trips,
        systems=systems,
        stops=stops,
        routes=routes,
    )

if __name__ == "__main__":
    main()
