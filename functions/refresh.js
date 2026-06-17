const ALLOWED_ORIGIN = "https://4rani-b.github.io";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export async function onRequestOptions() {
  return new Response(null, { headers: CORS_HEADERS });
}

export async function onRequestPost(context) {
  const response = await fetch(
    "https://api.github.com/repos/4rani-b/wc2026-sweepstake-1/actions/workflows/update-leaderboard.yml/dispatches",
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${context.env.GITHUB_TOKEN}`,
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "wc2026-sweepstake-pages",
      },
      body: JSON.stringify({ ref: "main" }),
    }
  );

  return new Response(null, {
    status: response.status,
    headers: CORS_HEADERS,
  });
}
