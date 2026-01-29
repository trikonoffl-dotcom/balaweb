# Final Deployment Instructions

The project is now split-ready.

## 1. Backend (Render)
1. Go to [dashboard.render.com](https://dashboard.render.com) > **Blueprints** > New Blueprint Instance.
2. Connect your `balaweb` repo.
3. It will auto-detect `render.yaml`. Click **Apply**.
4. **Copy the Service URL** (e.g., `https://trikon-backend.onrender.com`).

## 2. Frontend (Cloudflare Pages)
1. Go to Cloudflare Dashboard > **Workers & Pages** > Create Application > Pages > Connect to Git.
2. Select `balaweb`.
3. **Build Settings**:
   - Framework: **Next.js**
   - Build Command: `npm run build` (or `npx @cloudflare/next-on-pages` if using edge runtime, but standard build works for static export if configured)
   - Output Directory: `.next` (or `out` if using static export)
   
   *Recommendation*: For standard Next.js on Pages, just select **Next.js** preset.
   
4. **Environment Variables** (Crucial!):
   - `NEXT_PUBLIC_SUPABASE_URL`: (Your Supabase URL)
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: (Your Public Anon Key)
   - `NEXT_PUBLIC_API_URL`: https://trikon-essential.onrender.com

5. Deploy!
