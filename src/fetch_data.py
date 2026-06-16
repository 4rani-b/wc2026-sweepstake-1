import datetime
import requests

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
TOURNAMENT_START = datetime.date(2026, 6, 11)
TOURNAMENT_END = datetime.date(2026, 7, 19)


def _classify_stage(alt_game_note: str) -> str:
    note = (alt_game_note or "").lower()
    if "round of 32" in note:
        return "r32"
    if "rd of 16" in note or "round of 16" in note:
        return "r16"
    if "quarter" in note:
        return "qf"
    if "3rd" in note or "third" in note:
        return "third_place"
    if "semi" in note:
        return "sf"
    if "final" in note:
        return "final"
    if "group" in note:
        return "group"
    return "unknown"


def _extract_group(alt_game_note: str):
    """Return group letter from 'FIFA World Cup, Group B', else None."""
    for part in (alt_game_note or "").split(","):
        part = part.strip()
        if part.startswith("Group "):
            return part[6:].strip()
    return None


def _parse_event(event: dict):
    competitions = event.get("competitions", [])
    if not competitions:
        return None

    comp = competitions[0]
    status_type = comp.get("status", {}).get("type", {})
    completed = status_type.get("completed", False)

    competitors = comp.get("competitors", [])
    if len(competitors) != 2:
        return None

    home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
    away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])

    home_name = home.get("team", {}).get("displayName", "")
    away_name = away.get("team", {}).get("displayName", "")

    try:
        home_score = int(home.get("score") or 0)
        away_score = int(away.get("score") or 0)
    except (ValueError, TypeError):
        home_score = away_score = 0

    home_wins = home.get("winner", False)
    away_wins = away.get("winner", False)

    alt_note = comp.get("altGameNote") or event.get("altGameNote") or ""
    stage = _classify_stage(alt_note)
    group = _extract_group(alt_note)

    if completed:
        if home_wins:
            winner, loser = home_name, away_name
        elif away_wins:
            winner, loser = away_name, home_name
        else:
            winner = loser = None  # draw
    else:
        winner = loser = None

    return {
        "id": event.get("id", ""),
        "date": event.get("date", ""),
        "home_team": home_name,
        "away_team": away_name,
        "home_score": home_score,
        "away_score": away_score,
        "winner": winner,
        "loser": loser,
        "completed": completed,
        "stage": stage,
        "group": group,
        "alt_note": alt_note,
    }


def fetch_all_matches() -> list:
    """Fetch every match from tournament start through today, deduped by event id."""
    today = datetime.date.today()
    end = min(today, TOURNAMENT_END)

    matches = []
    seen_ids: set = set()
    current = TOURNAMENT_START

    while current <= end:
        date_str = current.strftime("%Y%m%d")
        url = f"{ESPN_BASE}/scoreboard?dates={date_str}"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            for event in resp.json().get("events", []):
                match = _parse_event(event)
                if match and match["id"] not in seen_ids:
                    seen_ids.add(match["id"])
                    matches.append(match)
        except Exception as exc:
            print(f"WARNING: could not fetch scoreboard for {date_str}: {exc}")

        current += datetime.timedelta(days=1)

    print(f"Fetched {len(matches)} matches up to {end}")
    return matches
