# email-automation
📧 Email Automation Tool: Scrape LinkedIn 🔍, create HTML email templates 📝, send bulk emails 📬, and track opens/clicks 📊. Auto-tag leads as ❄️ Cold (no engagement) or 🔥 Hot (clicked/opened). Built with Python 🐍, Selenium ⚙️, Flask 🌐 &amp; Streamlit 💻.


# 📧 AI-Powered Email Outreach Automation System

This project automates the process of identifying leads, generating personalized emails, sending campaigns in bulk, tracking engagement, and analyzing results — all through an interactive Streamlit interface.

---

## 🚀 Project Overview

The goal of this automation is to simplify B2B outreach by using AI and Python automation tools to:

- Scrape relevant leads from LinkedIn
- Clean and enrich the dataset
- Generate dynamic, personalized emails
- Send emails in batches using Gmail API/app passwords
- Track email opens and clicks
- Categorize leads into hot, warm, and cold
- Analyze and download performance reports

---

## 🧩 Tasks Breakdown

### ✅ Task 1: Lead Collection (LinkedIn Scraper)
- Technologies: Selenium, BeautifulSoup
- Filters: Industry, Company Size, Location
- Output: Company Name, About, Location, Industry, Size

### ✅ Task 2: Lead Cleaning & Enrichment
- Technologies: Pandas
- Logic: Filter duplicates, fill missing locations via text input
- Output: Cleaned Excel & CSV

### ✅ Task 3: Email Template Creation
- Format: HTML with placeholders like `{company_name}`, `{recipient_name}`
- Preview inside Streamlit with dynamic replacement

### ✅ Task 4: Bulk Email Sending
- Technologies: `smtplib`, `email.mime`, Gmail app passwords
- Features: Sender rotation, batch size control, delay settings
- Output: Log file with success/failure status

### ✅ Task 5: Campaign Analytics
- Technologies: Pandas, Plotly, Streamlit
- Logic: Open/click tracking log comparison
- Output: Engagement metrics, downloadable hot/warm/cold leads

### ✅ Task 6: Streamlit GUI
- Created interactive frontend for uploading templates, running campaigns, and downloading reports

### ✅ Task 7: Documentation (This File)
- Describes steps, tools used, and how to run each part of the project

---

## 🔧 Tools & Libraries Used

| Tool/Library        | Purpose                               |
|---------------------|---------------------------------------|
| `Streamlit`         | UI for the automation system          |
| `Pandas`            | Data cleaning and manipulation        |
| `Selenium`          | Web scraping for LinkedIn             |
| `smtplib/email.mime`| Sending formatted emails              |
| `Plotly`            | Visual analytics                      |
| `openpyxl`          | Reading Excel files                   |
| `BeautifulSoup4`    | HTML parsing during scraping          |

---

## 🧠 AI/Automation Techniques

- Placeholder replacement with company-specific values
- Dynamic rotation of Gmail sender accounts
- Tracking pixels for engagement tracking
- Categorization logic for lead scoring

---

## 💻 How to Run

1. Clone the repo:
   ```bash
   git clone https://github.com/Krunalsangani13/email-automation.git
   cd email-automation
