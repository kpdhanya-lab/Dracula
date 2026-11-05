# 🌊 BasinShift: FloodCast Disaster Intelligence Platform

AI-Powered Hydrological Flood Forecasting Command Center & Copilot Engine.

---

## 🚀 One-Click / GitHub Deployment on Vercel

This project is configured with native Vercel serverless functions (`/api/*`) and routing (`vercel.json`), allowing instant deployment without running a continuous background server.

### 1. Import Repository
1. Push your repository to GitHub: `https://github.com/kpdhanya-lab/Dracula.git`.
2. Go to [Vercel Dashboard](https://vercel.com/new).
3. Import the repository. Keep the **Framework Preset** as `Other` and Root Directory as `./`.

### 2. Configure Environment Variables in Vercel
In the Vercel project deployment setup, add the following Environment Variables under **Settings > Environment Variables**:

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | Your Groq Cloud API Key | `gsk_...` |
| `GROQ_MODEL` | LLM model for the Copilot | `openai/gpt-oss-120b` or `llama-3.3-70b-versatile` |
| `SUPABASE_URL` | Your Supabase project URL | `https://kgdyupauslkdqojqcwkw.supabase.co` |
| `SUPABASE_KEY` | Supabase Anon / Service Role Key | `eyJ...` |

### 3. Deploy
Click **Deploy**. Vercel will build and deploy the application across global edge nodes.

---

## 💻 Local Execution

### Option A: Local Unified Python Server
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server on port 3000
python server.py
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### Option B: Vercel CLI (Local Serverless Emulation)
```bash
npm i -g vercel
vercel dev
```
