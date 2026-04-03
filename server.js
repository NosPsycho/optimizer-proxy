const express = require("express");
const fetch   = require("node-fetch");

const app = express();
app.use(express.json());

// ── Config ────────────────────────────────────────────────────────────────────
const LLMAPI_KEY  = process.env.LLMAPI_KEY;   // set this in your host's env vars
const APP_SECRET  = "nostweaks-v1";            // must match ClaudeAiService.cs
const MODEL       = "claude-3-5-sonnet";
const PORT        = process.env.PORT || 3000;

// ── Auth middleware ───────────────────────────────────────────────────────────
app.use((req, res, next) => {
  if (req.headers["x-app-secret"] !== APP_SECRET) {
    return res.status(401).json({ error: "Unauthorised" });
  }
  next();
});

// ── Chat endpoint (streaming) ─────────────────────────────────────────────────
app.post("/chat", async (req, res) => {
  const { messages, max_tokens = 1024 } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: "messages array required" });
  }

  try {
    const upstream = await fetch("https://api.llmapi.dev/api/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type":  "application/json",
        "Authorization": `Bearer ${LLMAPI_KEY}`,
      },
      body: JSON.stringify({ model: MODEL, messages, max_tokens, stream: true }),
    });

    if (!upstream.ok) {
      const err = await upstream.text();
      return res.status(upstream.status).json({ error: err });
    }

    // Stream the SSE response straight back to the app
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection",    "keep-alive");

    upstream.body.pipe(res);
    upstream.body.on("error", () => res.end());

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/health", (_, res) => res.json({ status: "ok" }));

app.listen(PORT, () => console.log(`Nos Tweaks AI proxy running on port ${PORT}`));
