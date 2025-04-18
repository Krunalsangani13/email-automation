import pandas as pd
import smtplib
import time
import random
import csv
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==== CONFIG =====
# List of sender Gmail addresses & app passwords
senders = [
    {"email": "krunalsangani13@gmail.com", "app_password": "rvpchbeajlwrubbx"},
    {"email": "krunaltechnocomet@gmail.com", "app_password": "ixenbagzosrwyzpd"},
]

# sender_email = "krunaltemp1312@gmail.com"

sender = random.choice(senders)
sender_email = sender["email"]
app_password = sender["app_password"]
# app_password = "tqddaorqjrvwmtld"  # App password from Google
send_to = "madhavkotecha95@gmail.com"

subject_template = "Let's connect - quick idea for {company_name}"
template_file = "email_template.html"
excel_file = "linkedin_companies.xlsx"
log_file = "email_log.csv"
batch_size = 5
delay_between_emails = 10  # seconds

# =================

# Load leads
df = pd.read_excel(excel_file)

# Load HTML template
with open(template_file, "r", encoding="utf-8") as f:
    template = f.read()

# Send emails
for index, row in df.iterrows():
    company_name = row.get("Company Name", "your company")
    recipient_name="Team at "+ company_name
    recipient_email="krunalsangani13@gmail.com";

    sender = random.choice(senders) 

    subject = subject_template.format(company_name=company_name)
   
    # Personalize email
    email_body = template.format(
        # recipient_name="Team at " + recipient_name,
        recipient_name=recipient_name,
        company_name=company_name,
        recipient_email=recipient_email
    )


    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender["email"]
    msg["TO"]=send_to

    msg.attach(MIMEText(email_body, "html"))

    try:       
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
            server.login(sender["email"], sender["app_password"])
            server.sendmail(sender["email"], send_to, msg.as_string())
        
        print(f"✅ Sent to {recipient_email} via {sender['email']}")

         # ✅ Log success
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                index + 1,
                company_name,
                recipient_email,
                subject,
                "Sent",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

    except Exception as e:
        print(f"❌ Failed to send to {recipient_email}: {e}")

         # ❌ Log failure
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                index + 1,
                company_name,
                recipient_email,
                subject,
                "Failed",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

    # Delay to avoid spam filters
    time.sleep(delay_between_emails)

    # Batch pause (optional)
    if (index + 1) % batch_size == 0:
        print("⏳ Batch sent. Pausing for 60 seconds...")
        time.sleep(60)
