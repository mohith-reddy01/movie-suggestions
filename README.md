Flask Movie Project - Email & Database Setup

Live app: https://movie-suggestion2-production.up.railway.app/

This project uses SQLite for user and feedback storage and can email new registrations and feedback to an admin address using SMTP.

Required environment variables (set these in your OS or a .env file):

- SMTP_SERVER: SMTP server hostname (e.g. smtp.gmail.com)
- SMTP_PORT: SMTP port (usually 587)
- SMTP_USERNAME: SMTP auth username (email address)
- SMTP_PASSWORD: SMTP auth password or app password
- ADMIN_EMAIL: Recipient address for admin notifications
- EMAIL_FROM: Optional `From` address (defaults to SMTP_USERNAME)
- SECRET_KEY: Flask session secret (optional)

Quick test (PowerShell):

$env:SMTP_SERVER = "smtp.example.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "you@example.com"
$env:SMTP_PASSWORD = "yourpassword"
$env:ADMIN_EMAIL = "admin@example.com"
$env:SECRET_KEY = "change-this-secret"

python app.py

Then register a new user or submit feedback while logged in; the app will attempt to email the details to `ADMIN_EMAIL`.

Notes:
- For Gmail, you may need an App Password and to enable "Less secure app access" alternatives.
- Email failures are printed to stdout but do not block the user flow.

Gmail-specific setup
--------------------

If you want to send email using Gmail, follow these steps:

1. Enable 2-Step Verification for your Google account.
2. Create an App Password for "Mail" and the device you choose. Google will give you a 16-character app password — copy it.
3. Set the environment variables using your Gmail address as `SMTP_USERNAME` and the app password as `SMTP_PASSWORD`. Example (PowerShell):

```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USERNAME = "venkatamohithreddy1@gmail.com"
$env:SMTP_PASSWORD = "<your-app-password-here>"
$env:ADMIN_EMAIL = "venkatamohithreddy1@gmail.com"
$env:SECRET_KEY = "change-this-secret"
```

- Use `EMAIL_FROM` if you need a different From address. Do not commit the app password to source control.
- If you don't want to use Gmail, any SMTP provider that supports STARTTLS will work with the same env vars.
