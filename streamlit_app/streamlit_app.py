import streamlit as st
import pandas as pd
import threading
import io
import base64
import subprocess
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st
import smtplib
import time
from jinja2 import Template
from io import BytesIO
import re
import threading
import tracker_server 

st.set_page_config(layout="wide", page_title="Email Automation Dashboard")

st.title("📧 Email Automation - Sales Process Suite")

# === Helper: Start Flask Server ===
def run_flask_server():
    try:
        # Ensure the path is wrapped in quotes to handle spaces
        command = 'start cmd /k "cd C:\\Users\\dell\\3D Objects\\tsak 1\\linkedin_scraper && python tracker_server.py"'
        subprocess.run(command, shell=True, check=True)
    except Exception as e:
        st.error(f"Failed to start Flask server: {str(e)}")

if st.button("🚀 Start Flask Tracker"):
    # run_flask_server()
    threading.Thread(target=run_flask_server, daemon=True).start()
    st.success("✅ Flask tracker started in new CMD window: http://127.0.0.1:5000")
    
# ===== CONFIG =====
subject_template = "Let's connect - quick idea for {company_name}"
template_file = "email_template.html"  # Your email template file
excel_file = "linkedin_companies.xlsx"  # Your Excel file with leads
log_file = "email_log.csv"  # Log file to track email sending status
batch_size = 5  # Number of emails to send in each batch
delay_between_emails = 5  # Delay between sending emails (in seconds)

# === Tabs for 5 Tasks ===
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 1. Scrape LinkedIn",
    "📂 2. Filter Leads",
    "📝 3. Create Email Template",
    "📤 4. Send Campaign",
    "📊 5. Analyze Campaign"
])

# ========== TASK 1: LinkedIn Scraper ==========
with tab1:
    st.header("🔍 Define ICP & Scrape Leads from LinkedIn")

    industry = st.text_input("Industry")
    location = st.text_input("Location")
    company_size = st.selectbox("Company Size", ["Small", "Medium", "Large"])
    num_leads = st.slider("How many leads to scrape?", 5, 50, 10)

    linkedin_email = st.text_input("LinkedIn Email", value="krunalsangani13@gmail.com")
    linkedin_password = st.text_input("LinkedIn Password", type="password", value="krunal@13")

    if st.button("🚀 Scrape LinkedIn Leads"):


        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from openpyxl import load_workbook

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
 
        try:
            driver.get("https://www.linkedin.com/login")
            time.sleep(2)

            username = driver.find_element(By.ID, "username")
            password = driver.find_element(By.ID, "password")
            username.send_keys(linkedin_email)
            password.send_keys(linkedin_password)
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(4)

            query = f"{industry} companies in {location} site:linkedin.com/company"
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(3)

            company_links = []
            results = driver.find_elements(By.XPATH, '//div[@class="MjjYud"]//a')
            for r in results:
                url = r.get_attribute('href')
                if url and "linkedin.com/company" in url:
                    company_links.append(url)
                if len(company_links) >= num_leads:
                    break

            st.success(f"✅ Found {len(company_links)} company URLs.")

            company_data = []
            for idx,url in enumerate(company_links):
                about_url = url.rstrip('/') + '/about'
                driver.get(about_url)
                time.sleep(4)

                try:
                    name = driver.find_element(By.TAG_NAME, 'h1').text
                except:
                    name = "N/A"

                try:
                    about = driver.find_element(By.CSS_SELECTOR, 'div.org-grid__core-rail div.text-body-medium').text
                except:
                    try:
                        about = driver.find_element(By.TAG_NAME, 'p').text
                    except:
                        about = "N/A"

                try:
                    location_element = driver.find_element(By.XPATH, '//div[contains(@class, "org-top-card-summary-info-list")]//li')
                    location_text = location_element.text
                except:
                    location_text = location
                    
                company_data.append({
                    "Company Name": name,
                    "About": about,
                    "Location": location_text,
                    "LinkedIn URL": url,
                    "Industry": industry,
                    "Company Size": company_size
                })

            driver.quit()

            if company_data:
                df = pd.DataFrame(company_data)
                df.to_csv("linkedin_companies.csv", index=False)
                
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False, sheet_name="LinkedIn Companies", engine="openpyxl")
                excel_buffer.seek(0)
                
                st.success("✅ Data scraped and saved.")
                st.dataframe(df)
                st.download_button("📥 Download CSV", df.to_csv(index=False), "linkedin_companies.csv", mime="text/csv")
                st.download_button(
                    "📥 Download Excel",
                    data=excel_buffer,
                    file_name="linkedin_companies.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ No company data extracted.")
        except Exception as e:
            driver.quit()
            st.error(f"❌ Error: {e}")

# ========== TASK 2: Export + Filter Leads ==========
with tab2:
    st.header("📂 Export & Filter Leads")
    leads_file = st.file_uploader("Upload Leads CSV (or use scraped_data.csv)", type="csv", key="leads")
    
    try:
        if leads_file:
            df = pd.read_csv(leads_file)
        else:
            df = pd.read_csv("scraped_data.csv")

        st.subheader("📄 Preview of Leads")
        st.write(df.head())

        # Filter Section
        keyword = st.text_input("Filter leads by keyword (title/industry/location)")
        if keyword:
            filtered = df[df.apply(lambda row: keyword.lower() in str(row).lower(), axis=1)]
            st.write("Filtered Leads:")
            st.write(filtered)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name="All Leads", index=False)
                filtered.to_excel(writer, sheet_name="Filtered Leads", index=False)
            buffer.seek(0)

            st.download_button("📥 Download Excel with All & Filtered Leads", 
                               data=buffer, 
                               file_name="leads_exported.xlsx", 
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


            st.download_button("Download Filtered Leads", filtered.to_csv(index=False), "filtered_leads.csv")
        
        # Export
        st.download_button("Download All Leads", df.to_csv(index=False), "leads_exported.csv")

    except FileNotFoundError:
        st.warning("No scraped_data.csv found. Upload leads or scrape them first.")

# ========== TASK 3: Email Template Builder ==========
with tab3:
    st.header("📨 Task 3: Create and Preview Email Template")

    st.markdown("""
    This section allows you to upload or create a dynamic HTML email template for outreach.
    - Use placeholders like `{recipient_name}`, `{company_name}`, and `{recipient_email}`.
    - These will be automatically filled in from your uploaded Excel data.
    """)

    # Example HTML template
    example_html_template = """
    <html>
        <body style="font-family: Arial, sans-serif; line-height:1.6;">
            <p>Hi {recipient_name},</p>
            <p>I came across your company, <b>{company_name}</b>, and I believe we can collaborate on something exciting.</p>
            <p>Would love to connect! Let me know a good time to talk.</p>
            <br>
            <p>Best regards,<br>Your Name</p>
            <p>Email: you@example.com</p>
        </body>
    </html>
    """

    st.subheader("✉️ Subject Line")
    subject_template = st.text_input(
        "Enter Subject Line (supports placeholders)",
        "Exciting Collaboration with {company_name}"
    )

    st.subheader("📄 Upload or Use Example Template")
    html_file = st.file_uploader("Upload HTML Template", type=["html"])

    if html_file:
        html_template = html_file.read().decode("utf-8")
        st.success("✅ Template uploaded successfully!")
    else:
        use_example = st.checkbox("Use example HTML template", value=True)
        html_template = example_html_template if use_example else ""

    # If data exists from Excel
    if "df" in st.session_state:
        df = st.session_state.df

        st.subheader("📋 Select Contact from Your Excel Data")
        email_column = st.selectbox("Select Email Column", df.columns, index=0)
        contact = st.selectbox("Choose a Contact", df[email_column])

        lead_data = df[df[email_column] == contact].iloc[0].to_dict()

        # Preview the template with selected data
        st.subheader("👁️ Email Preview with Selected Contact")
        try:
            rendered_subject = subject_template.format(**lead_data)
            rendered_html = html_template.format(**lead_data)

            st.markdown(f"**📬 Subject Preview:** `{rendered_subject}`")
            st.components.v1.html(rendered_html, height=300, scrolling=True)

            st.subheader("📄 Raw HTML Output")
            st.code(rendered_html, language="html")

        except KeyError as e:
            st.error(f"❌ Template is missing placeholder: {e}")

    else:
        st.subheader("👁️ Preview Template with Sample Data")

        # Sample fallback data
        sample_data = {
            "recipient_name": "Alex from NovaTech",
            "company_name": "NovaTech",
            "recipient_email": "alex@novatech.com"
        }

        if html_template:
            try:
                rendered_subject = subject_template.format(**sample_data)
                rendered_html = html_template.format(**sample_data)

                st.markdown(f"**📬 Subject Preview:** `{rendered_subject}`")
                st.components.v1.html(rendered_html, height=300, scrolling=True)

                # st.subheader("📄 Raw HTML Output")
                # st.code(rendered_html, language="html")

                st.subheader("🛠️ Editable Raw HTML Output")
                edited_html = st.text_area("You can edit the final HTML here:", rendered_html, height=300)

                # Optional: Re-render the edited HTML live
                st.subheader("👁️ Live Preview After Editing")
                # st.components.v1.html(edited_html, height=300, scrolling=True)
                st.components.v1.html(f"<div style='background-color:#fff; color:#000; padding:20px;'>{edited_html}</div>", height=400)

            except KeyError as e:
                st.error(f"❌ Template is missing placeholder: {e}")

            st.markdown("### ⬇️ Download Your Final HTML Template")

            # Prepare file
            b64 = base64.b64encode(edited_html.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="edited_template.html">📥 Download HTML File</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please upload or use the example HTML template.")

# ========== TASK 4: Send Email Campaign ==========

with tab4:
    st.header("📧 Bulk Email Campaign Sender (Excel + HTML Template)")

    st.markdown("Upload your **email HTML template** and **Excel leads file**, and use Gmail app passwords to send personalized emails.")

    # Sender accounts rotation setup
    senders = [
        {"email": "krunalsangani13@gmail.com", "app_password": "rvpchbeajlwrubbx"},
        {"email": "krunaltechnocomet@gmail.com", "app_password": "ixenbagzosrwyzpd"},
        {"email":"krunaltemp1312@gmail.com", "app_password":"tqddaorqjrvwmtld"}
    ]

    # File Uploads
    template_file = st.file_uploader("📄 Upload Email HTML Template", type=["html"])
    leads_file = st.file_uploader("📊 Upload Excel File with Leads", type=["xlsx"])

    # Optional configs
    batch_size = st.number_input("📦 Batch Size (emails per round)", min_value=1, value=5)
    delay_seconds = st.number_input("⏳ Delay Between Emails (in seconds)", min_value=1, value=10)

    if st.button("🚀 Start Sending Emails"):
        if not template_file or not leads_file:
            st.warning("⚠️ Please upload both the template and leads file.")
            st.stop()

        try:
            # Load leads
            df = pd.read_excel(leads_file)
            st.success(f"✅ Loaded {len(df)} leads from Excel.")

            # Load email template
            template = template_file.read().decode("utf-8")

            # Setup log
            log_rows = []

            for index, row in df.iterrows():
                email_body = template
                for column in df.columns:
                    placeholder = f"{{{{{column.lower().replace(' ', '_')}}}}}"
                    value = str(row[column])
                    email_body = email_body.replace(placeholder, value)


                company_name = row.get("Company Name", "your company")
                # recipient_email = row.get("Email", "").strip()
                recipient_email = str(row.get("Email", "")).strip()

                if not recipient_email:
                    recipient_email = "khsangani3344@gmail.com"  # <- Replace with your static email
                    st.info(f"ℹ️ Row {index+1} has no email. Using default: {recipient_email}")

                # Rotate sender
                sender = random.choice(senders)
                sender_email = sender["email"]
                app_password = sender["app_password"]

                # recipient_name = "Team at " + company_name if company_name != "N/A" else "there"
                subject = f"Let's connect - quick idea for {company_name}"

                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = recipient_email
                msg.attach(MIMEText(email_body, "html"))              

                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(sender_email, app_password)
                        server.sendmail(sender_email, recipient_email, msg.as_string())

                    st.success(f"✅ Sent to {recipient_email} via {sender_email}")
                    log_rows.append([
                        index + 1, company_name, recipient_email,
                        subject, "Sent", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])

                except Exception as e:
                    st.error(f"❌ Failed to send to {recipient_email}: {e}")
                    log_rows.append([
                        index + 1, company_name, recipient_email,
                        subject, "Failed", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])

                time.sleep(delay_seconds)

                if (index + 1) % batch_size == 0:
                    st.info("⏳ Batch sent. Pausing for 10 seconds...")
                    time.sleep(10)

            # Show log
            log_df = pd.DataFrame(log_rows, columns=["#", "Company", "Email", "Subject", "Status", "Timestamp"])
            st.dataframe(log_df)
            st.download_button("📥 Download Log CSV", data=log_df.to_csv(index=False), file_name="email_log.csv", mime="text/csv")

            st.success("🎉 Bulk email campaign finished!")

        except Exception as e:
            st.error(f"❌ Error during sending: {e}")

# ========== TASK 5: Campaign Analytics ==========
with tab5:
    st.header("📊 Campaign Analytics")

    email_log = st.file_uploader("📤 Upload Email Log CSV", type=["csv"])
    open_log = st.file_uploader("📤 Upload Open/Click Tracking CSV", type=["csv"])

    if email_log and open_log:
        try:
            # Load files
            emails = pd.read_csv(email_log)
            emails.columns = emails.columns.str.strip().str.lower()
            
            email_col = next((col for col in emails.columns if "email" in col), None)

            if not email_col:
                st.error("❌ Could not find an email column in the uploaded file.")
                st.write("📌 Columns detected:", emails.columns.tolist())
            
            else:
                opens = pd.read_csv(open_log, names=["Email", "Action", "Time"])
                opens["Time"] = pd.to_datetime(opens["Time"])

                # Add LeadStatus column based on opens & clicks
                def categorize_lead(email):
                    engagement = opens[opens["Email"] == email]
                    if engagement.empty:
                        return "Cold"
                    elif "click" in engagement["Action"].values:
                        return "Hot"
                    elif "open" in engagement["Action"].values:
                        return "Warm"
                    else:
                        return "Cold"

                emails["LeadStatus"] = emails["email"].apply(categorize_lead)

                # Save updated analytics
                st.success("✅ Engagement data processed!")
                st.subheader("📈 Summary Metrics")

                total_sent = len(emails)
                hot_leads = emails[emails["LeadStatus"] == "Hot"]
                warm_leads = emails[emails["LeadStatus"] == "Warm"]
                cold_leads = emails[emails["LeadStatus"] == "Cold"]

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📨 Total Sent", total_sent)
                col2.metric("🔥 Hot Leads", len(hot_leads))
                col3.metric("🌤 Warm Leads", len(warm_leads))
                col4.metric("🧊 Cold Leads", len(cold_leads))

                # Pie Chart Visualization
                fig = px.pie(
                    names=["Hot", "Warm", "Cold"],
                    values=[len(hot_leads), len(warm_leads), len(cold_leads)],
                    title="💡 Lead Engagement Distribution",
                    color_discrete_sequence=["#FF6347", "#FFA500", "#87CEEB"]
                )
                st.plotly_chart(fig)

                # Full Log Preview
                st.subheader("📄 Full Email Log with Lead Status")
                st.dataframe(emails)

                # Download Buttons
                st.download_button("📥 Download Full Analytics", data=emails.to_csv(index=False), file_name="analytics_output.csv", mime="text/csv")
                st.download_button("🔥 Download Hot Leads", data=hot_leads.to_csv(index=False), file_name="hot_leads.csv", mime="text/csv")
                st.download_button("🌤 Download Warm Leads", data=warm_leads.to_csv(index=False), file_name="warm_leads.csv", mime="text/csv")
                st.download_button("🧊 Download Cold Leads", data=cold_leads.to_csv(index=False), file_name="cold_leads.csv", mime="text/csv")

        except Exception as e:
            st.error(f"❌ Error while processing analytics: {e}")

    else:
        st.info("ℹ️ Please upload both the Email Log and Tracking Log CSVs to view analytics.")
