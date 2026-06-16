"""
Scoring engine — recalculates everything from scratch on each run.

Scoring rules:
  Group position:  1st=3, 2nd=2, 3rd=1, 4th=0
  Qualify for R32: +1  (auto for 1st/2nd; best-8 3rd-place teams also qualify)
  Knockout win:    +3  (R32, R16, QF, SF)
  Win the Final:   +5
  Giant Killer:    +2 per win against a team ranked 15+ FIFA places higher (better)
  Cinderella:      +5 to owner of lowest-FIFA-ranked team to reach knockouts
  Wooden Spoon:    +5 to owner of worst group-stage team (last of the lasts)
"""

GROUP_STAGE_PTS = {1: 3, 2: 2, 3: 1, 4: 0}
KNOCKOUT_STAGES = {"r32", "r16", "qf", "sf", "final"}


def _normalize(name: str, aliases: dict) -> str:
    return aliases.get(name, name)


# ---------------------------------------------------------------------------
# Group standings
# ---------------------------------------------------------------------------

def build_group_standings(matches: list, aliases: dict, overrides: dict = None) -> dict:
    """
    Calculate group standings from completed group-stage match results.
    Returns {group_letter: [sorted team dicts with position added]}.
    Each team dict: {team, mp, w, d, l, gf, ga, gd, pts, position, complete}

    overrides: {group_letter: {team_name: position}} for fair-play tiebreakers
    that cannot be computed from pts/GD/GF alone.  Only applies when teams are
    genuinely tied on all three statistics; otherwise the computed order wins.
    """
    overrides = overrides or {}
    groups: dict = {}  # letter -> {team_name -> stats}

    for match in matches:
        if match["stage"] != "group" or not match["completed"]:
            continue
        group = match.get("group")
        if not group:
            continue

        home = _normalize(match["home_team"], aliases)
        away = _normalize(match["away_team"], aliases)
        hg, ag = match["home_score"], match["away_score"]

        if group not in groups:
            groups[group] = {}
        for team in (home, away):
            if team not in groups[group]:
                groups[group][team] = {"team": team, "mp": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0}

        groups[group][home]["mp"] += 1
        groups[group][away]["mp"] += 1
        groups[group][home]["gf"] += hg
        groups[group][home]["ga"] += ag
        groups[group][away]["gf"] += ag
        groups[group][away]["ga"] += hg

        if match["winner"]:
            winner = _normalize(match["winner"], aliases)
            loser = _normalize(match["loser"], aliases)
            groups[group][winner]["w"] += 1
            groups[group][loser]["l"] += 1
        else:
            groups[group][home]["d"] += 1
            groups[group][away]["d"] += 1

    GROUP_SIZE = 4  # all WC 2026 groups have 4 teams

    sorted_groups: dict = {}
    for letter, teams_dict in groups.items():
        teams = list(teams_dict.values())
        for t in teams:
            t["pts"] = t["w"] * 3 + t["d"]
            t["gd"] = t["gf"] - t["ga"]

        # Pad with placeholder entries for teams that haven't played yet.
        # A 0-pt team with negative GD (e.g. Senegal) must not get an
        # inflated position just because unplayed teams aren't in the dict yet.
        # Placeholders (0pts/GD/GF) sort naturally above negative-GD teams.
        placeholders = [
            {"team": "", "mp": 0, "w": 0, "d": 0, "l": 0,
             "gf": 0, "ga": 0, "pts": 0, "gd": 0, "_placeholder": True}
            for _ in range(GROUP_SIZE - len(teams))
        ]
        all_entries = teams + placeholders
        group_overrides = overrides.get(letter, {})
        all_entries.sort(key=lambda t: (
            -t["pts"],
            -t["gd"],
            -t["gf"],
            # Fair-play tiebreaker from overrides.json; only decisive when
            # pts/GD/GF are all equal (override has no effect otherwise).
            group_overrides.get(t["team"], 9999),
        ))
        complete = all(t["mp"] >= 3 for t in teams)
        for i, t in enumerate(all_entries):
            t["position"] = i + 1
            t["complete"] = complete
        sorted_groups[letter] = [t for t in all_entries if not t.get("_placeholder")]

    return sorted_groups


# ---------------------------------------------------------------------------
# 3rd-place qualifiers (best 8 of 12 advance to R32)
# ---------------------------------------------------------------------------

def find_third_place_qualifiers(group_standings: dict) -> set:
    thirds = []
    for teams in group_standings.values():
        if not all(t["complete"] for t in teams):
            continue
        third = next((t for t in teams if t["position"] == 3), None)
        if third:
            thirds.append(third)
    thirds.sort(key=lambda t: (-t["pts"], -t["gd"], -t["gf"]))
    return {t["team"] for t in thirds[:8]}


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def calculate_all(
    matches: list,
    group_standings: dict,
    fifa_rankings: dict,
    participants: dict,
    aliases: dict,
) -> tuple:
    """
    Returns (scores_dict, meta_dict).

    scores_dict: {person: {total, teams: {team: breakdown_dict}}}
    meta_dict: {cinderella_team, cinderella_owner, wooden_spoon_team,
                wooden_spoon_owner, tournament_winner, tournament_winner_owner}
    """
    # Flat lookup: team_name -> stats dict
    team_stats: dict = {}
    for teams in group_standings.values():
        for t in teams:
            team_stats[t["team"]] = t

    third_qualifiers = find_third_place_qualifiers(group_standings)

    # ---- Build knockout picture from match data ----
    teams_in_knockout: set = set()
    knockout_wins: dict = {}   # team -> [(loser, stage)]

    for match in matches:
        if match["stage"] not in KNOCKOUT_STAGES or not match["completed"]:
            continue
        home = _normalize(match["home_team"], aliases)
        away = _normalize(match["away_team"], aliases)
        teams_in_knockout.add(home)
        teams_in_knockout.add(away)
        if match["winner"]:
            w = _normalize(match["winner"], aliases)
            l = _normalize(match["loser"], aliases)
            knockout_wins.setdefault(w, []).append((l, match["stage"]))

    # Confirmed R32 qualifiers (includes teams that haven't played yet but group is done)
    confirmed_r32: set = set(teams_in_knockout)
    for team, stats in team_stats.items():
        if not stats["complete"]:
            continue
        pos = stats["position"]
        if pos in (1, 2):
            confirmed_r32.add(team)
        elif pos == 3 and team in third_qualifiers:
            confirmed_r32.add(team)

    # ---- Giant Killer: pre-compute for every team ----
    # Applies to ALL matches (group + knockout), any win where winner is ranked 15+ places worse
    giant_killer_pts: dict = {}
    for match in matches:
        if not match["completed"] or not match["winner"]:
            continue
        w = _normalize(match["winner"], aliases)
        l = _normalize(match["loser"], aliases)
        w_rank = fifa_rankings.get(w, 999)
        l_rank = fifa_rankings.get(l, 999)
        if w_rank - l_rank >= 15:
            giant_killer_pts[w] = giant_killer_pts.get(w, 0) + 2

    # ---- Cinderella: lowest FIFA-ranked team in confirmed R32 ----
    cinderella_team = None
    if confirmed_r32:
        ranked = [t for t in confirmed_r32 if t in fifa_rankings]
        if ranked:
            cinderella_team = max(ranked, key=lambda t: fifa_rankings[t])

    # ---- Wooden Spoon: team currently performing worst by sweepstake points ----
    # Calculated AFTER base points are known (no circular dependency — ws excluded from base)
    # Only teams that have played at least 1 match are eligible.
    # Tiebreak: worst FIFA ranking (highest rank number).
    all_sweepstake_teams = [t for teams in participants.values() for t in teams]
    active_teams = [t for t in all_sweepstake_teams if team_stats.get(t, {}).get("mp", 0) > 0]

    def _base_pts(team: str) -> int:
        stats = team_stats.get(team)
        pos = stats["position"] if stats else 4
        gp = GROUP_STAGE_PTS[pos]
        r32 = 1 if team in confirmed_r32 else 0
        wins = knockout_wins.get(team, [])
        ko = len([w for w in wins if w[1] != "final"]) * 3
        fin = 5 if any(w[1] == "final" for w in wins) else 0
        gk = giant_killer_pts.get(team, 0)
        cin = 5 if team == cinderella_team else 0
        return gp + r32 + ko + fin + gk + cin

    wooden_spoon_team = None
    if active_teams:
        min_pts = min(_base_pts(t) for t in active_teams)
        candidates = [t for t in active_teams if _base_pts(t) == min_pts]
        # Tiebreak: worst GD (most negative), then most goals conceded
        def _worst_key(team):
            stats = team_stats.get(team, {})
            return (stats.get("gd", 0), -stats.get("ga", 0))
        wooden_spoon_team = min(candidates, key=_worst_key)

    # ---- Tournament winner ----
    tournament_winner = None
    for w_team, wins in knockout_wins.items():
        for (_, stage) in wins:
            if stage == "final":
                tournament_winner = w_team

    # ---- Per-team points ----
    def _team_breakdown(team: str) -> dict:
        stats = team_stats.get(team)
        position = stats["position"] if stats else 4

        # Group position points
        group_pts = GROUP_STAGE_PTS[position]

        # Qualify for R32
        r32_pts = 1 if team in confirmed_r32 else 0

        # Knockout wins (excluding the Final which has its own bucket)
        wins = knockout_wins.get(team, [])
        ko_wins = [w for w in wins if w[1] != "final"]
        ko_pts = len(ko_wins) * 3

        # Win the Final
        final_pts = 5 if any(w[1] == "final" for w in wins) else 0

        # Giant Killer
        gk_pts = giant_killer_pts.get(team, 0)

        # Cinderella Award
        cinderella_pts = 5 if team == cinderella_team else 0

        # Wooden Spoon
        ws_pts = 5 if team == wooden_spoon_team else 0

        total = group_pts + r32_pts + ko_pts + final_pts + gk_pts + cinderella_pts + ws_pts

        return {
            "group": group_pts,
            "qualify_r32": r32_pts,
            "knockout_wins": ko_pts,
            "win_final": final_pts,
            "giant_killer": gk_pts,
            "cinderella": cinderella_pts,
            "wooden_spoon": ws_pts,
            "total": total,
            "position": position,
            "complete": stats["complete"] if stats else False,
            "mp": stats["mp"] if stats else 0,
        }

    # ---- Aggregate per participant ----
    scores: dict = {}
    for person, teams in participants.items():
        team_breakdowns = {t: _team_breakdown(t) for t in teams}
        total = sum(b["total"] for b in team_breakdowns.values())
        scores[person] = {"total": total, "teams": team_breakdowns}

    # Resolve owners of special awards
    def _owner_of(team):
        if team is None:
            return None
        for person, data in participants.items():
            if team in data:
                return person
        return None

    meta = {
        "cinderella_team": cinderella_team,
        "cinderella_owner": _owner_of(cinderella_team),
        "wooden_spoon_team": wooden_spoon_team,
        "wooden_spoon_owner": _owner_of(wooden_spoon_team),
        "tournament_winner": tournament_winner,
        "tournament_winner_owner": _owner_of(tournament_winner),
    }

    return scores, meta
