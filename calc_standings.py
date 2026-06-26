import re
import json
from collections import defaultdict

GROUPS = {
    "서울1": [
        "서울DTFCU12",
        "서울충암U12",
        "서울FC아쏘",
        "서울화랑U12",
        "서울유석U12",
        "서울K리거강용FC",
    ],
    "서울2": [
        "서울양강초",
        "서울AAFCU12",
        "서울FC서울풀굿코리아U12",
        "서울JCMFCU12",
        "서울FC난우",
        "서울영등포구스포츠클럽U12",
    ],
    "서울3": [
        "서울우이초",
        "서울전농초",
        "서울신답FCU12",
        "서울FC은평U12",
        "서울최강희축구교실",
    ],
    "서울4": [
        "서울NUFCU12",
        "서울JP연세FCU12",
        "서울송파구JD풋볼아카데미",
        "서울송파구FCPS",
        "서울송파구유소년축구단",
        "서울서강초",
    ],
    "서울5": [
        "서울서초MB U-12",
        "서울관악FCU12",
        "서울UKFCU12",
        "서울신용산초",
        "서울FC서울 U-12",
        "서울노원FC한마음U12",
    ],
    "서울6": [
        "서울성동SCU12",
        "서울삼선FCU12",
        "서울대동초",
        "서울위례FCU12",
        "서울이랜드FCU12",
        "서울GWFCU12",
    ],
}


def short_name(team: str) -> str:
    return team.replace("서울", "")


def parse_matches(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f.read().splitlines()]

    matches = []
    i = 0
    while i < len(lines):
        if re.match(r"\d+번경기", lines[i]):
            i += 3  # skip match no, time, stadium
            if i < len(lines) and lines[i]:
                home = lines[i]
                i += 1
                while i < len(lines) and not lines[i]:
                    i += 1
                if i < len(lines):
                    score_line = lines[i]
                    m = re.match(r"(\d+)\s*:\s*(\d+)", score_line)
                    i += 1
                    while i < len(lines) and not lines[i]:
                        i += 1
                    if m and i < len(lines):
                        away = lines[i]
                        matches.append(
                            (home, int(m.group(1)), int(m.group(2)), away)
                        )
                        i += 1
        else:
            i += 1
    return matches


def calc_standings(teams: list, all_matches: list) -> list:
    stats = {
        t: {"played": 0, "won": 0, "drawn": 0, "lost": 0, "gf": 0, "ga": 0, "pts": 0}
        for t in teams
    }

    for home, hg, ag, away in all_matches:
        if home not in stats or away not in stats:
            continue
        stats[home]["played"] += 1
        stats[away]["played"] += 1
        stats[home]["gf"] += hg
        stats[home]["ga"] += ag
        stats[away]["gf"] += ag
        stats[away]["ga"] += hg
        if hg > ag:
            stats[home]["won"] += 1
            stats[home]["pts"] += 3
            stats[away]["lost"] += 1
        elif hg < ag:
            stats[away]["won"] += 1
            stats[away]["pts"] += 3
            stats[home]["lost"] += 1
        else:
            stats[home]["drawn"] += 1
            stats[away]["drawn"] += 1
            stats[home]["pts"] += 1
            stats[away]["pts"] += 1

    rows = []
    for t in teams:
        s = stats[t]
        gd = s["gf"] - s["ga"]
        rows.append(
            (t, s["played"], s["won"], s["drawn"], s["lost"], s["gf"], s["ga"], gd, s["pts"])
        )

    rows.sort(key=lambda x: (-x[8], -x[7], -x[5]))
    return rows


if __name__ == "__main__":
    matches = parse_matches("c:/cursor_ws/empty_app/경기결과_0626.txt")
    result = {}

    for gname, teams in GROUPS.items():
        rows = calc_standings(teams, matches)
        result[gname] = [
            {
                "rank": i + 1,
                "team": short_name(r[0]),
                "played": r[1],
                "won": r[2],
                "drawn": r[3],
                "lost": r[4],
                "gf": r[5],
                "ga": r[6],
                "gd": r[7],
                "pts": r[8],
            }
            for i, r in enumerate(rows)
        ]
        print(gname)
        for row in result[gname]:
            print(
                f"  {row['rank']} {row['team']} {row['pts']}pts "
                f"({row['won']}W {row['drawn']}D {row['lost']}L) {row['gf']}:{row['ga']}"
            )

    with open("c:/cursor_ws/empty_app/standings_data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
