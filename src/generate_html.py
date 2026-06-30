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
    max-width: 1200px; margin: 0 auto; padding: 20px 12px;
}
header { text-align: center; padding: 28px 0 18px; }
header h1 { font-size: 2em; color: var(--gold); letter-spacing: 3px; text-transform: uppercase; }
.subtitle {
    color: var(--muted); margin-top: 8px; font-size: 0.88em;
    display: flex; align-items: center; justify-content: center; gap: 10px; flex-wrap: wrap;
}
.refresh-btn {
    background: var(--surface2); border: 1px solid var(--border);
    color: var(--text); padding: 5px 14px; border-radius: 6px;
    cursor: pointer; font-size: 0.85em; transition: background 0.15s;
}
.refresh-btn:hover { background: var(--border); }
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

/* ----- Table ----- */
table { width: 100%; border-collapse: collapse; margin-top: 16px; }
thead tr { background: var(--surface); border-bottom: 2px solid var(--gold); }
th { padding: 10px 8px; text-align: left; color: var(--gold); font-size: 0.75em; text-transform: uppercase; letter-spacing: 1px; }
th.center { text-align: center; }
tbody tr { border-bottom: 1px solid var(--border); }
tbody tr:hover { background: var(--surface); }
td { padding: 10px 8px; vertical-align: top; }
.td-rank { font-size: 1.2em; width: 44px; text-align: center; }
.td-name { font-weight: 700; font-size: 1.05em; white-space: nowrap; }
.td-total { font-size: 1.7em; font-weight: 900; color: var(--green); text-align: center; min-width: 55px; }
.td-teams { padding: 8px 6px; }

/* All 4 teams in a responsive grid inside a single cell */
.teams-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }

/* ----- Team cell ----- */
.team-cell { font-size: 0.82em; min-width: 0; }
.team-cell .tname { font-weight: 600; }
.team-cell .tpts { color: var(--green); font-weight: 700; font-size: 1em; }
.team-cell .tbreakdown { color: var(--muted); margin-top: 2px; line-height: 1.5; display: block; }
.team-cell .tbreakdown .bonus { color: var(--orange); }
.no-data { color: var(--muted); font-style: italic; font-size: 0.8em; }
.team-cell.eliminated { background: rgba(248, 81, 73, 0.08); border: 1px solid rgba(248, 81, 73, 0.25); }
.team-cell.eliminated .tname { color: var(--muted); }
.team-cell.eliminated .tpts { color: var(--muted); }

footer {
    color: var(--muted); font-size: 0.78em; text-align: center;
    margin-top: 30px; border-top: 1px solid var(--border); padding-top: 14px; line-height: 1.8;
}

/* ----- Tablet: 2-column team grid ----- */
@media (max-width: 960px) {
    .teams-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ----- Mobile: card layout ----- */
@media (max-width: 600px) {
    table, tbody { display: block; }
    thead { display: none; }

    /* Each row becomes a card */
    tbody tr {
        display: grid;
        grid-template-areas: "rank name pts" "teams teams teams";
        grid-template-columns: 44px 1fr auto;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        margin-bottom: 10px;
        overflow: hidden;
    }
    tbody tr:hover { background: var(--surface2); }

    .td-rank  { grid-area: rank;  display: block; text-align: center; align-self: center; padding: 10px 6px; font-size: 1em; width: auto; }
    .td-name  { grid-area: name;  display: block; align-self: center; padding: 10px 6px; font-size: 1em; }
    .td-total { grid-area: pts;   display: block; align-self: center; padding: 10px 12px; font-size: 1.3em; text-align: right; min-width: auto; }
    .td-teams { grid-area: teams; display: block; border-top: 1px solid var(--border); padding: 8px; }

    .teams-grid { grid-template-columns: repeat(2, 1fr); gap: 6px; }

    /* Card-style team cells on mobile */
    .team-cell {
        background: var(--bg); border: 1px solid var(--border);
        border-radius: 6px; padding: 6px 8px;
    }

    header h1 { font-size: 1.5em; }
    .subtitle { font-size: 0.82em; }
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

    if not breakdown["mp"] and not breakdown["complete"]:
        breakdown_html = '<span class="no-data">No matches yet</span>'
    else:
        breakdown_html = f'<span class="tbreakdown">{"<br>".join(parts)}</span>'

    eliminated_class = " eliminated" if breakdown.get("eliminated") else ""
    return (
        f'<div class="team-cell{eliminated_class}">'
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


def generate(scores: dict, meta: dict, participants: dict, last_updated: str, worker_url: str = "", refresh_token: str = "") -> str:
    # Sort participants by total points desc
    ranked = sorted(scores.items(), key=lambda x: -x[1]["total"])

    # --- Award cards ---
    winner_card = _award_card(
        "🏆 World Cup Winner",
        holder=meta["tournament_winner_owner"],
        team=f"{TEAM_FLAGS.get(meta['tournament_winner'], '')} {meta['tournament_winner']}" if meta["tournament_winner"] else "",
        description="Champion — TBD",
    )

    awards_html = f'<div class="awards">{winner_card}</div>'

    # --- Table header ---
    header_cells = (
        '<th class="center">#</th>'
        '<th>Name</th>'
        '<th class="center">Pts</th>'
        '<th>Teams</th>'
    )

    # --- Table rows ---
    rows_html = ""
    for rank, (person, data) in enumerate(ranked, 1):
        rank_display = RANK_ICONS.get(rank, str(rank))
        teams = participants[person]
        team_divs = "".join(
            _team_cell(team, data["teams"].get(team, {})) for team in teams
        )
        rows_html += (
            f'<tr>'
            f'<td class="td-rank">{rank_display}</td>'
            f'<td class="td-name">{person}</td>'
            f'<td class="td-total">{data["total"]}</td>'
            f'<td class="td-teams"><div class="teams-grid">{team_divs}</div></td>'
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
  <p class="subtitle">
    <span>Last updated: {last_updated}</span>
    <span>·</span>
    <span>Recalculated daily at 08:00 UTC</span>
    <button class="refresh-btn" id="refresh-btn" onclick="triggerRefresh()">↻ Refresh</button>
  </p>
</header>
{awards_html}
<table>
  <thead><tr>{header_cells}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>
<footer>
  <p><strong>Scoring:</strong> Win Group 3pts · 2nd 2pts · 3rd 1pt · Qualify R32 +1pt · Knockout Win 3pts · Win Final 5pts</p>
  <p>Points recalculated fresh each day (not cumulative)</p>
</footer>
<script>
var WORKER_URL = "{worker_url}";
function triggerRefresh() {{
  var btn = document.getElementById("refresh-btn");
  if (!WORKER_URL) {{
    location.href = location.pathname + "?t=" + Date.now();
    return;
  }}
  btn.disabled = true;
  btn.textContent = "Triggering...";
  fetch(WORKER_URL, {{
    method: "POST",
    headers: {{"Content-Type": "application/json"}}
  }}).then(function(r) {{
    if (r.status === 204) {{
      var secs = 55;
      btn.textContent = "Updating… " + secs + "s";
      var iv = setInterval(function() {{
        secs--;
        btn.textContent = "Updating… " + secs + "s";
        if (secs <= 0) {{ clearInterval(iv); location.reload(); }}
      }}, 1000);
    }} else {{
      btn.textContent = "Error " + r.status;
      setTimeout(function() {{ btn.textContent = "↻ Refresh"; btn.disabled = false; }}, 3000);
    }}
  }}).catch(function() {{
    btn.textContent = "↻ Refresh";
    btn.disabled = false;
  }});
}}
</script>
</body>
</html>"""
