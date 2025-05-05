import os
import resend
import markdown2

# Load Resend API key
resend.api_key = os.environ["RESEND_API_KEY"]

# Load markdown content
with open("newsletter.md", "r") as file:
    markdown_text = file.read()

# Convert to HTML
html_content = markdown2.markdown(markdown_text)

# Prepare and send email
params = {
    "from": "Ethereum Weekly <your@verifieddomain.com>",  # Must be verified
    "to": [os.environ["NEWSLETTER_RECIPIENT"]],
    "subject": "🚀 Weekly Ethereum Newsletter",
    "html": html_content,
}

res = resend.Emails.send(params)
print("✅ Sent! Response:", res)
