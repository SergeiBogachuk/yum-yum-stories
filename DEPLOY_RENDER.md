# Yum-Yum Stories production deploy

## Recommended setup

- Marketing site: `yumyumstories.com`
- App: `app.yumyumstories.com`
- Hosting: Render web service

This project already reads secrets from either `st.secrets` or environment variables,
so it can run on Render without changing the app code.

## Why move off Streamlit Community Cloud

- A custom `.com` does not make the app faster by itself.
- The bigger improvement comes from moving to a more stable production host.
- Render supports custom domains, HTTPS, and keeps a normal web-service deployment flow.

## Create the service on Render

1. Push this repository to GitHub.
2. In Render, click **New +** -> **Web Service**.
3. Connect the GitHub repository.
4. Render should detect `render.yaml` automatically.
5. Deploy the service.

## Environment variables to add in Render

Add the same values that are currently in `.streamlit/secrets.toml`.

Required values usually include:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_TTS_MODEL`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPPORT_EMAIL`
- `STRIPE_EXTRA_PACK_LINK`
- `STRIPE_STANDARD_LINK`
- `STRIPE_FAMILY_LINK`
- `STRIPE_PORTAL_LINK`
- `ELEVENLABS_API_KEY` if still used
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_DEFAULT_REGION` if still used

For Google TTS on normal hosts, use:

- `GOOGLE_TTS_SERVICE_ACCOUNT_JSON`

This should contain the whole service-account JSON in one environment variable.

## Custom domain

Recommended:

- `app.yumyumstories.com` -> Render service

Later, if you want a full landing site:

- `yumyumstories.com` -> landing page
- `app.yumyumstories.com` -> this Streamlit app

## After deployment

1. Open the Render service settings.
2. Add a custom domain.
3. In your domain registrar or DNS provider, add the DNS records Render asks for.
4. Verify the domain in Render.
5. Test on:
   - iPhone Safari
   - Android Chrome
   - iPad / tablet
   - desktop incognito

## Important note

Do not commit `.streamlit/secrets.toml`.
Only keep `.streamlit/secrets.toml.example` in GitHub.
