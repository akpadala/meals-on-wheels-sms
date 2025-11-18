# Meals on Wheels SMS Intake MVP

A conversational SMS intake system for Meals on Wheels Orange County that uses AI to collect client information and automatically stores it in Google Sheets.

## Features

- **SMS Conversation Flow**: AI-powered conversational intake via SMS
- **Google Sheets Integration**: Automatic data storage and retrieval
- **Web Form Submission**: Alternative intake method via web form
- **Validation**: Comprehensive input validation (email, phone, age, zip code, etc.)
- **Session Management**: Persistent conversation state across messages

## Folder Structure
```
routes/         → API endpoints
services/       → Twilio, AI, Sheets code
templates/      → HTML form
static/         → CSS/JS
data/           → Session storage
tests/          → Testing docs
docs/           → Documentation
```

## Prerequisites

Before deploying, ensure you have:

1. **Twilio Account**
   - Account SID and Auth Token
   - A Twilio phone number with SMS capability

2. **Google Cloud Project**
   - Service account with Google Sheets API enabled
   - Service account JSON credentials
   - A Google Sheet with "Main Validation Sheet" worksheet

3. **OpenAI Account**
   - OpenAI API key (for AI conversation)

4. **Python 3.8+** installed

## Local Development Setup

### 1. Clone and install dependencies
```bash
git clone https://github.com/username/meals-on-wheels-sms.git
cd meals-on-wheels-sms
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# Google Sheets
SPREADSHEET_ID=your_google_sheet_id_here
GOOGLE_CREDENTIALS={"type":"service_account","project_id":"..."}

# Twilio SMS
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI
OPENAI_API_KEY=sk-your_openai_api_key

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Run the server locally
```bash
python main.py
```

Visit `http://localhost:8000/docs` to test the API endpoints.

## Deployment

### Option 1: Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Add environment variables in Railway dashboard or via CLI:
```bash
railway variables set SPREADSHEET_ID="your_value"
railway variables set TWILIO_ACCOUNT_SID="your_value"
# ... add all other variables from .env
```

4. Deploy:
```bash
railway up
```

5. Get your deployment URL and configure Twilio webhook (see below).

### Option 2: Render

1. Create a new Web Service on [Render](https://render.com)

2. Connect your GitHub repository

3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. Add environment variables in Render dashboard (all variables from `.env`)

5. Deploy and get your service URL

### Option 3: Heroku

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create app:
```bash
heroku create your-app-name
```

3. Add environment variables:
```bash
heroku config:set SPREADSHEET_ID="your_value"
heroku config:set TWILIO_ACCOUNT_SID="your_value"
# ... add all other variables
```

4. Create `Procfile` in project root:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. Deploy:
```bash
git push heroku main
```

## Configuring Twilio Webhook

After deployment, configure your Twilio phone number:

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to Phone Numbers → Manage → Active Numbers
3. Select your phone number
4. Under "Messaging Configuration":
   - **A MESSAGE COMES IN**: Webhook
   - **URL**: `https://your-deployment-url.com/sms-webhook`
   - **HTTP Method**: POST
5. Save

## How to Use

### SMS Intake Flow

1. **User texts "START"** to your Twilio number
2. System welcomes them and asks the first question
3. User responds with their information
4. System validates and asks the next question
5. Process continues until all information is collected
6. Data is automatically saved to Google Sheets

**Example Conversation:**
```
User: START

Bot: Welcome to Meals on Wheels Orange County! I'm here to help you
     get started. What is your full name? (Please provide Last Name, First Name)

User: Smith, John

Bot: Thank you, John! How old are you?

User: 72

Bot: Got it! What is your email address?

[continues through all questions...]
```

### Web Form Submission

1. Navigate to `https://your-deployment-url.com/`
2. Fill out the intake form
3. Submit
4. Data is saved to Google Sheets and user receives welcome SMS

## API Endpoints

### Health Check
```
GET /health
```
Returns service status

### Create Client
```
POST /api/clients/create
Content-Type: application/json

{
  "full_name": "Doe, John",
  "age": 75,
  "phone_number": "9195551234",
  "email": "john@example.com",
  ...
}
```

### Get Client
```
GET /api/clients/{email}
```
Retrieves client data by email

### Update Client
```
PUT /api/clients/update
Content-Type: application/json

{
  "email": "john@example.com",
  "phone_number": "9195551234",
  "updates": {
    "eligibility_status": "approved",
    "notes": "Ready for delivery"
  }
}
```

### SMS Webhook (Twilio)
```
POST /sms-webhook
```
Receives SMS messages from Twilio (configured in Twilio dashboard)

## Google Sheets Structure

Your Google Sheet "Main Validation Sheet" should have these columns:

1. Timestamp
2. Full Name
3. Age
4. Phone Number
5. Email
6. Street Address
7. Apt/Unit/Secondary
8. City
9. State
10. Zip Code
11. Referral Source
12. Request Reason
13. Has Pets
14. Pet Details
15. Has Weapons
16. Emergency Contact Name
17. Emergency Contact Phone
18. Language Preference
19. Eligibility Status
20. Notes
21. Conversation Stage

## Troubleshooting

### SMS not being received

- Check Twilio webhook URL is correct
- Verify webhook is set to POST method
- Check Twilio console logs for errors
- Ensure deployment URL is accessible

### Google Sheets not updating

- Verify SPREADSHEET_ID is correct
- Check service account has edit permissions on the sheet
- Ensure worksheet name is exactly "Main Validation Sheet"
- Check logs for Google API errors

### AI responses not working

- Verify OPENAI_API_KEY is valid
- Check OpenAI account has available credits
- System falls back to simple responses if OpenAI fails

### Sessions not persisting

- Ensure `data/` directory exists
- Check file permissions
- Review logs for session save errors

## Development Notes

- Sessions are stored in `data/sessions.json` (file-based, not suitable for high traffic)
- CORS configuration should be updated for production (not `*`)
- Consider adding rate limiting for production use
- Add authentication for API endpoints in production

## Support

For issues or questions, please open an issue on GitHub.


