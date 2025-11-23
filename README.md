# Meals on Wheels SMS Intake System

An AI-powered SMS intake system for Meals on Wheels Orange County. Clients text in, answer a few questions through natural conversation, and their info is automatically saved to Google Sheets.

## What It Does

- Clients text **START** to begin the intake process
- AI guides them through questions (name, age, address, emergency contact, etc.)
- Validates responses in real-time with friendly error messages
- Saves completed intakes to Google Sheets automatically
- Also works via web form at the root URL

## Quick Start

### 1. Clone and install
```bash
git clone https://github.com/your-repo/meals-on-wheels-sms.git
cd meals-on-wheels-sms
pip install -r requirements.txt
```

### 2. Set up your .env file
```bash
cp .env.example .env
```

Fill in your credentials:
- **Google Sheets**: Spreadsheet ID + service account JSON
- **Twilio**: Account SID, Auth Token, Phone Number
- **OpenAI**: API key for AI conversations

### 3. Run locally
```bash
python main.py
```

Server starts at `http://localhost:8000`

---

## Deploy to Production

### Railway (Recommended)

1. Push your code to GitHub

2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub

3. Add your environment variables in the **Variables** tab:
   - Click **Raw Editor**
   - Paste all your .env variables
   - Set `ENV=production`

4. Railway gives you a URL like `https://your-app.up.railway.app`

5. Update Twilio webhook (see below)

### Other Platforms

**Render**: Connect GitHub, it auto-detects the Dockerfile

**Heroku**: `git push heroku main` (needs Heroku CLI)

---

## Configure Twilio Webhook

After deploying:

1. Go to [Twilio Console](https://console.twilio.com)
2. Phone Numbers → Your number
3. Under Messaging, set webhook URL to:
   ```
   https://your-app-url.com/sms-webhook
   ```
4. Method: POST
5. Save

Now texts to your Twilio number will hit your app!

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SPREADSHEET_ID` | Your Google Sheet ID (from the URL) |
| `GOOGLE_CREDENTIALS` | Full service account JSON |
| `TWILIO_ACCOUNT_SID` | From Twilio Console |
| `TWILIO_AUTH_TOKEN` | From Twilio Console |
| `TWILIO_PHONE_NUMBER` | Your Twilio number (+1...) |
| `OPENAI_API_KEY` | From OpenAI dashboard |
| `API_KEY` | Your API key for protected endpoints |
| `ENV` | `development` or `production` |
| `CORS_ORIGINS` | Allowed origins (use `*` for dev) |
| `PORT` | Server port (default: 8000) |

---

## API Endpoints

### Public
- `GET /` - Web intake form
- `GET /health` - Health check with service status

### Protected (require `X-API-Key` header)
- `POST /api/clients/create` - Create new client
- `GET /api/clients/{email}` - Get client by email
- `PUT /api/clients/update` - Update client info

### Webhooks
- `POST /sms-webhook` - Twilio SMS webhook

---

## Security Features

- **API Key Authentication** - Protected endpoints require `X-API-Key` header
- **Rate Limiting** - 100 requests per minute by default
- **Twilio Signature Verification** - Validates webhooks in production
- **Security Headers** - XSS protection, clickjacking prevention, etc.
- **Environment Validation** - Checks all required vars on startup

---

## Project Structure

```
├── main.py              # FastAPI app and routes
├── config.py            # Environment validation
├── middleware.py        # Auth, rate limiting, security
├── services/
│   ├── twilio_service.py    # SMS sending
│   ├── ai_conversation.py   # AI chat flow
│   └── session_manager.py   # Conversation state
├── templates/           # Web form HTML
├── tests/               # Unit tests
├── Dockerfile           # Container config
└── requirements.txt     # Dependencies
```

---

## Testing

Run the test suite:
```bash
pytest
```

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

---

## Example SMS Conversation

```
User: START

Bot: Welcome to Meals on Wheels Orange County! I'm here to help
     you get started. What is your full name? (Last Name, First Name)

User: Smith, John

Bot: Nice to meet you, John! How old are you?

User: 72

Bot: Got it! What is your email address?

User: john@email.com

Bot: Thanks! What is your street address?

... continues through all questions ...

Bot: Thank you! I've collected all the information. We'll review
     your application and get back to you soon.
```

---

## Troubleshooting

**SMS not working?**
- Check Twilio webhook URL matches your deployment
- Look at Twilio Console logs for errors

**Google Sheets not updating?**
- Verify service account has edit access to the sheet
- Check that worksheet is named "Main Validation Sheet"

**AI responses not working?**
- Check OpenAI API key is valid
- System falls back to simple responses if AI fails

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a PR

---

Built for Meals on Wheels Orange County
