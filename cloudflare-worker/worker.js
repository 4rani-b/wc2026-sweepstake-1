// Cloudflare Worker — proxy for triggering the GitHub Actions leaderboard update.
// The GITHUB_TOKEN secret is stored in the Worker environment, never in the repo.
//
// Setup:
//   1. Create a Worker at cloudflare.com (free tier is plenty)
//   2. Paste this script and deploy
//   3. Go to Worker Settings → Variables → add Secret: GITHUB_TOKEN = your classic PAT
//      (needs 'workflow' scope, no expiry recommended)
//   4. Copy your Worker URL (e.g. https://wc2026-refresh.YOUR-NAME.workers.dev)
//   5. Put the URL in data/config.json under "worker_url"
//   6. Push — the next workflow run will bake the URL into the leaderboard page

export default {
  async fetch(request, env) {
    const ALLOWED_ORIGIN = "https://4rani-b.github.io";

    const corsHeaders = {
      "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405, headers: corsHeaders });
    }

    const response = await fetch(
      "https://api.github.com/repos/4rani-b/wc2026-sweepstake-1/actions/workflows/update-leaderboard.yml/dispatches",
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
          "Accept": "application/vnd.github.v3+json",
          "Content-Type": "application/json",
          "User-Agent": "wc2026-sweepstake-worker",
        },
        body: JSON.stringify({ ref: "main" }),
      }
    );

    return new Response(null, {
      status: response.status,
      headers: corsHeaders,
    });
  },
};
