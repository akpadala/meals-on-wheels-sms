# Meals on Wheels SMS Intake MVP

**Due:** Monday 11/17 @ 11:59 PM

## Team
- Person 1: Backend + Deployment (YOU)
- Person 2: SMS + AI
- Person 3: Form + Sheets  
- Person 4: Questions + Testing

## Folder Structure
```
routes/         → API endpoints (Person 1, 2, 3)
services/       → Twilio, AI, Sheets code (Person 2, 3)
templates/      → HTML form (Person 3)
static/         → CSS/JS (Person 3)
data/           → Question flow, sessions (Person 4)
tests/          → Testing docs (Person 4)
docs/           → Documentation (Person 4)
```

## Setup (Each Person)
```bash
git clone [git@github.com:username/meals-on-wheels-sms.git]
cd meals-on-wheels-sms
pip install flask twilio openai python-dotenv
python app.py
```


