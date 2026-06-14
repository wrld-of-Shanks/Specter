# Email Setup for Lawyer Contact Feature

The lawyer contact feature sends consultation requests to `shankardarur0@gmail.com`.

## Option 1: Gmail SMTP (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Lawman App"
   - Copy the 16-character password

3. **Add to `.env` file**:
```bash
SMTP_EMAIL=shankardarur0@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```

## Option 2: No Email (Fallback)

If SMTP is not configured, the system will:
- Log all requests to the console
- Still show success message to users
- You can check backend logs for requests

## Testing

1. Fill out the contact form at `/contact`
2. Check your email inbox for the formatted request
3. Or check backend console logs if SMTP not configured

## Email Format

You'll receive:
- Client name, email, phone
- Lawyer type requested
- Budget range
- Case description
- Formatted HTML email with all details
