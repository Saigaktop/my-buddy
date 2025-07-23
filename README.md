# Deployment Guide

Follow these steps to deploy the bot to [Fly.io](https://fly.io).

1. **Install `flyctl`** – the Fly command line utility. Follow the instructions on the [Fly.io website](https://fly.io/docs/getting-started/installing-flyctl/) to install it for your platform.
2. **Run `fly launch`** to generate the `fly.toml` and create the application on Fly. Answer the prompts or supply flags as needed.
3. **Set the required secrets** for the deployment:
   ```bash
   fly secrets set FLY_API_TOKEN=<your-token> \
                  BOT_TOKEN=<telegram-bot-token> \
                  OPENAI_API_KEY=<openai-key> \
                  ADMIN_CHAT_ID=<telegram-id>
   ```
4. **Push to the `main` branch**. A GitHub Actions workflow automatically deploys the app whenever you push to `main`.
