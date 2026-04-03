# Nos Tweaks AI Proxy — Deploy Guide

## What this is
A tiny Node.js server that sits between the app and llmapi.dev.
Your API key lives **only** on the server — never in the distributed .exe.

## Deploy FREE on Render.com (recommended)

1. Push this folder to a GitHub repo (e.g. `nostweaks-proxy`)
2. Go to **render.com** → New → Web Service
3. Connect your GitHub repo
4. Settings:
   - Build Command: `npm install`
   - Start Command: `npm start`
   - Environment: `Node`
5. Add environment variable:
   - Key:   `LLMAPI_KEY`
   - Value: `your_llmapi_key_here`
6. Click **Deploy**
7. Copy your URL e.g. `https://nostweaks-proxy.onrender.com`

## Update the app with your URL

Open `NosTweaks/Services/ClaudeAiService.cs` and change line:

```csharp
private const string ProxyUrl = "https://nos-tweaks-ai.onrender.com/chat";
```

to your actual Render URL:

```csharp
private const string ProxyUrl = "https://nostweaks-proxy.onrender.com/chat";
```

Then rebuild with BUILD.bat — done!

## Security
- The app sends `x-app-secret: nostweaks-v1` with every request
- The proxy rejects anything without that header
- Your llmapi key is only in Render's encrypted env vars
- Users cannot extract the key from the .exe

## Free tier limits (Render)
- 750 hours/month free (enough for 24/7)
- Spins down after 15min inactivity (first request is ~30s slower)
- Upgrade to paid ($7/mo) for always-on if needed
