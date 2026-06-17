#!/usr/bin/env python3
"""
Entry point. Run with: python src/main.py
Writes docs/index.html with the current leaderboard.
"""

import json
import datetime
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"


def load_json(path: pathlib.Path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    # Strip _note metadata key if present
    if isinstance(raw, dict):
        raw.pop("_note", None)
    return raw


def main():
    print("Loading static data...")
    participants = load_json(DATA / "participants.json")
    fifa_rankings = load_json(DATA / "fifa-rankings.json")
    aliases = load_json(DATA / "team-aliases.json")
    standings_overrides_path = DATA / "standings-overrides.json"
    standings_overrides = load_json(standings_overrides_path) if standings_overrides_path.exists() else {}

    # All teams in the sweepstake (flat list for validation)
    all_sweepstake_teams = {t for teams in participants.values() for t in teams}
    missing = all_sweepstake_teams - set(fifa_rankings.keys())
    if missing:
        print(f"WARNING: teams missing from fifa-rankings.json: {missing}", file=sys.stderr)

    print("Fetching match data from ESPN API...")
    from fetch_data import fetch_all_matches
    matches = fetch_all_matches()

    if not matches:
        print("WARNING: no match data returned — check ESPN API connectivity.", file=sys.stderr)

    print("Calculating standings from match data...")
    from calculate_points import build_group_standings, calculate_all
    group_standings = build_group_standings(matches, aliases, standings_overrides)

    total_groups = len(group_standings)
    total_matches = len([m for m in matches if m["completed"]])
    print(f"  {total_groups} groups · {total_matches} completed matches")

    print("Calculating sweepstake scores...")
    scores, meta = calculate_all(matches, group_standings, fifa_rankings, participants, aliases)

    # Print leaderboard to stdout for CI logs
    ranked = sorted(scores.items(), key=lambda x: -x[1]["total"])
    print("\nCurrent leaderboard:")
    for rank, (person, data) in enumerate(ranked, 1):
        print(f"  {rank:2}. {person:<8} {data['total']:3} pts")

    if meta["cinderella_team"]:
        print(f"\nCinderella: {meta['cinderella_team']} (owner: {meta['cinderella_owner']})")
    if meta["wooden_spoon_team"]:
        print(f"Wooden Spoon: {meta['wooden_spoon_team']} (owner: {meta['wooden_spoon_owner']})")
    if meta["tournament_winner"]:
        print(f"Tournament winner: {meta['tournament_winner']} (owner: {meta['tournament_winner_owner']})")

    print("\nGenerating HTML...")
    from generate_html import generate
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    html = generate(scores, meta, participants, now_utc)

    DOCS.mkdir(exist_ok=True)
    out_path = DOCS / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Written: {out_path}")


if __name__ == "__main__":
    main()
