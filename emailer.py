import httpx
from config import settings

def send_email(to, subject, body):
  if not settings.PRODUCTION:
    print({to, subject, body})
    return
  
  url = "https://api.resend.com/emails"
  headers = {
      "Authorization": f"Bearer {settings.RESEND_API_KEY}",
      "Content-Type": "application/json",
  }
  data = {
    "from": "onboarding@resend.dev",
    "to": [to],
    "subject": subject,
    "html": body
  }
  with httpx.Client() as client:
    response = client.post(url, headers=headers, json=data)
    response.raise_for_status()

