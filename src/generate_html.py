"""Generates the self-contained docs/index.html leaderboard page."""

RANK_ICONS = {1: "🥇", 2: "🥈", 3: "🥉"}

TEAM_FLAGS = {
    "Morocco": "🇲🇦", "Colombia": "🇨🇴", "Austria": "🇦🇹", "Curacao": "🇨🇼",
    "Argentina": "🇦🇷", "Sweden": "🇸🇪", "South Africa": "🇿🇦", "Haiti": "🇭🇹",
    "Brazil": "🇧🇷", "South Korea": "🇰🇷", "Bosnia & Herzegovina": "🇧🇦", "New Zealand": "🇳🇿",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Türkiye": "🇹🇷", "Paraguay": "🇵🇾", "Tunisia": "🇹🇳",
    "Belgium": "🇧🇪", "Croatia": "🇭🇷", "Iran": "🇮🇷", "Jordan": "🇯🇴",
    "Spain": "🇪🇸", "Egypt": "🇪🇬", "Czechia": "🇨🇿", "DR Congo": "🇨🇩",
    "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Ghana": "🇬🇭", "Qatar": "🇶🇦",
    "Germany": "🇩🇪", "Uruguay": "🇺🇾", "Canada": "🇨🇦", "Uzbekistan": "🇺🇿",
    "France": "🇫🇷", "Ivory Coast": "🇨🇮", "Saudi Arabia": "🇸🇦", "Australia": "🇦🇺",
    "Portugal": "🇵🇹", "Norway": "🇳🇴", "Algeria": "🇩🇿", "Panama": "🇵🇦",
    "Senegal": "🇸🇳", "USA": "🇺🇸", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Iraq": "🇮🇶",
    "Mexico": "🇲🇽", "Switzerland": "🇨🇭", "Ecuador": "🇪🇨", "Cape Verde": "🇨🇻",
}

STAGE_LABELS = {
    "r32": "R32", "r16": "R16", "qf": "QF", "sf": "SF", "final": "Final"
}

CSS = """
:root {
    --bg: #0d1117; --surface: #161b22; --surface2: #21262d;
    --border: #30363d; --text: #e6edf3; --muted: #8b949e;
    --gold: #d4a017; --green: #3fb950; --orange: #f0883e; --red: #f85149;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 1100px; margin: 0 auto; padding: 20px 12px;
}
header { text-align: center; padding: 28px 0 18px; }
header h1 { font-size: 2em; color: var(--gold); letter-spacing: 3px; text-transform: uppercase; }
header .subtitle { color: var(--muted); margin-top: 6px; font-size: 0.88em; }
.awards {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px; margin: 18px 0;
}
.award-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px 16px;
}
.award-card h3 { font-size: 0.78em; text-transform: uppercase; letter-spacing: 1px; color: var(--gold); margin-bottom: 7px; }
.award-card .holder { font-weight: 700; font-size: 1.05em; }
.award-card .team-name { color: var(--muted); font-size: 0.88em; margin-top: 3px; }
.award-card .pending { color: var(--muted); font-style: italic; font-size: 0.9em; }
table { width: 100%; border-collapse: collapse; margin-top: 16px; }
thead tr { background: var(--surface); border-bottom: 2px solid var(--gold); }
th { padding: 10px 8px; text-align: left; color: var(--gold); font-size: 0.75em; text-transform: uppercase; letter-spacing: 1px; }
th.right, td.right { text-align: right; }
th.center, td.center { text-align: center; }
tbody tr { border-bottom: 1px solid var(--border); }
tbody tr:hover { background: var(--surface); }
td { padding: 12px 8px; vertical-align: top; }
.td-rank { font-size: 1.2em; width: 44px; text-align: center; }
.td-name { font-weight: 700; font-size: 1.05em; white-space: nowrap; }
.td-total { font-size: 1.7em; font-weight: 900; color: var(--green); text-align: center; min-width: 55px; }
.team-cell { font-size: 0.82em; min-width: 120px; }
.team-cell .tname { font-weight: 600; }
.team-cell .tpts { color: var(--green); font-weight: 700; font-size: 1em; }
.team-cell .tbreakdown { color: var(--muted); margin-top: 2px; line-height: 1.5; }
.team-cell .tbreakdown .bonus { color: var(--orange); }
.no-data { color: var(--muted); font-style: italic; font-size: 0.8em; }
footer {
    color: var(--muted); font-size: 0.78em; text-align: center;
    margin-top: 30px; border-top: 1px solid var(--border); padding-top: 14px; line-height: 1.8;
}
@media (max-width: 640px) {
    .team-col-3, .team-col-4 { display: none; }
    .td-total { font-size: 1.3em; }
}
"""


def _team_cell(team: str, breakdown: dict) -> str:
    flag = TEAM_FLAGS.get(team, "")
    total = breakdown["total"]

    parts = []
    if breakdown["group"] > 0:
        pos_label = {1: "1st", 2: "2nd", 3: "3rd"}.get(breakdown["position"], "")
        parts.append(f"Grp {pos_label}: {breakdown['group']}")
    elif breakdown["complete"]:
        parts.append("4th: 0")
    else:
        parts.append("Group stage")

    if breakdown["qualify_r32"]:
        parts.append(f"R32 qual: +1")
    if breakdown["knockout_wins"]:
        n = breakdown["knockout_wins"] // 3
        parts.append(f"{n} KO win{'s' if n > 1 else ''}: +{breakdown['knockout_wins']}")
    if breakdown["win_final"]:
        parts.append(f"Won Final: +5")

    bonus_parts = []
    if breakdown["giant_killer"]:
        bonus_parts.append(f"Giant Killer: +{breakdown['giant_killer']}")
    if breakdown["cinderella"]:
        bonus_parts.append("Cinderella: +5")
    if breakdown["wooden_spoon"]:
        bonus_parts.append("Wooden Spoon: +5")

    regular_html = "<br>".join(parts) if parts else ""
    bonus_html = ""
    if bonus_parts:
        bonus_html = "<br>" + "<br>".join(f'<span class="bonus">{b}</span>' for b in bonus_parts)

    if not breakdown["mp"] and not breakdown["complete"]:
        breakdown_html = '<span class="no-data">No matches yet</span>'
    else:
        breakdown_html = f'<span class="tbreakdown">{regular_html}{bonus_html}</span>'

    return (
        f'<div class="team-cell">'
        f'<span class="tname">{flag} {team}</span><br>'
        f'<span class="tpts">{total} pts</span><br>'
        f'{breakdown_html}'
        f'</div>'
    )


def _award_card(title: str, holder: str, team: str, description: str = "") -> str:
    body = (
        f'<div class="holder">{holder}</div>'
        f'<div class="team-name">{team}</div>'
        if holder else
        f'<div class="pending">{description}</div>'
    )
    return f'<div class="award-card"><h3>{title}</h3>{body}</div>'


def generate(scores: dict, meta: dict, participants: dict, last_updated: str) -> str:
    # Sort participants by total points desc
    ranked = sorted(scores.items(), key=lambda x: -x[1]["total"])

    # --- Award cards ---
    cinderella_card = _award_card(
        "⭐ Cinderella Award (+5pts)",
        holder=meta["cinderella_owner"],
        team=f"{TEAM_FLAGS.get(meta['cinderella_team'], '')} {meta['cinderella_team']}" if meta["cinderella_team"] else "",
        description="Lowest FIFA-ranked team to reach Round of 32 — TBD",
    )
    wooden_card = _award_card(
        "🪵 Wooden Spoon (+5pts)",
        holder=meta["wooden_spoon_owner"],
        team=f"{TEAM_FLAGS.get(meta['wooden_spoon_team'], '')} {meta['wooden_spoon_team']}" if meta["wooden_spoon_team"] else "",
        description="Worst group-stage team — TBD (group stage not yet complete)",
    )
    winner_card = _award_card(
        "🏆 World Cup Winner",
        holder=meta["tournament_winner_owner"],
        team=f"{TEAM_FLAGS.get(meta['tournament_winner'], '')} {meta['tournament_winner']}" if meta["tournament_winner"] else "",
        description="Champion — TBD",
    )

    awards_html = f'<div class="awards">{cinderella_card}{wooden_card}{winner_card}</div>'

    # --- Table header ---
    header_cells = (
        '<th class="center">#</th>'
        '<th>Name</th>'
        '<th class="center">Pts</th>'
    )
    # Team columns — label by position (Team 1–4) in header, actual name in cell
    for i in range(1, 5):
        cls = f"team-col-{i}"
        header_cells += f'<th class="{cls}">Team {i}</th>'

    # --- Table rows ---
    rows_html = ""
    for rank, (person, data) in enumerate(ranked, 1):
        rank_display = RANK_ICONS.get(rank, str(rank))
        teams = participants[person]
        team_cells = ""
        for i, team in enumerate(teams, 1):
            breakdown = data["teams"].get(team, {})
            team_cells += f'<td class="team-col-{i}">{_team_cell(team, breakdown)}</td>'

        rows_html += (
            f'<tr>'
            f'<td class="td-rank">{rank_display}</td>'
            f'<td class="td-name">{person}</td>'
            f'<td class="td-total">{data["total"]}</td>'
            f'{team_cells}'
            f'</tr>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WC2026 Sweepstake Leaderboard</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>⚽ WC2026 Sweepstake</h1>
  <p class="subtitle">Last updated: {last_updated} &nbsp;·&nbsp; Recalculated daily at 08:00 UTC</p>
</header>
{awards_html}
<table>
  <thead><tr>{header_cells}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
<footer>
  <p><strong>Scoring:</strong> Win Group 3pts · 2nd 2pts · 3rd 1pt · Qualify R32 +1pt · Knockout Win 3pts · Win Final 5pts</p>
  <p>Giant Killer +2pts (beat team 15+ FIFA places above you) · Cinderella Award +5pts · Wooden Spoon +5pts</p>
  <p>R16 wins also count for 3pts · Points recalculated fresh each day (not cumulative)</p>
</footer>
</body>
</html>"""
