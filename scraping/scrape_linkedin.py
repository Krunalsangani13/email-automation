from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from openpyxl import load_workbook
import pandas as pd
import time

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

linkedin_email = "krunalsangani13@gmail.com"      # 🔒 Replace with your LinkedIn email
linkedin_password = "krunal@13"        # 🔒 Replace with your password

driver.get("https://www.linkedin.com/login")
time.sleep(3)

# Fill in login form
username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")
username.send_keys(linkedin_email)
password.send_keys(linkedin_password)

driver.find_element(By.XPATH, '//button[@type="submit"]').click()
time.sleep(5)  # wait for login to complete


# Define Google Search URL based on ICP
query = "IT service companies in Bangalore site:linkedin.com/company"
search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

# Visit Google Search
driver.get(search_url)
time.sleep(3)

# Try to fetch search result links
company_links = []
try:
    results = driver.find_elements(By.XPATH, '//div[@class="MjjYud"]//a')
    for r in results:
        url = r.get_attribute('href')
        if url and "linkedin.com/company" in url:
            company_links.append(url)
except Exception as e:
    print("❌ Error while collecting search results:", e)

print(f"✅ Found {len(company_links)} LinkedIn company URLs.")

company_data = []

# Visit LinkedIn company pages
for url in company_links:
    if not url.endswith('/about'):
        about_url = url.rstrip('/') + '/about'
    else:
        about_url = url

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

# Location (Flexible: look for any location-tag or label)
    try:
        location_element = driver.find_element(By.XPATH, '//div[contains(@class, "org-top-card-summary-info-list")]//li')
        location = location_element.text
    except:
        location = "N/A"

    company_data.append({
        "Company Name": name,
        "About": about,
        "Location": location,
        "LinkedIn URL": url
    })

# Save data
if company_data:
    df = pd.DataFrame(company_data)
    df.to_csv("linkedin_companies.csv", index=False)
    print("✅ Data saved to linkedin_companies.csv")

    excel_file = "linkedin_companies.xlsx"
    df.to_excel(excel_file, index=False, sheet_name="LinkedIn Companies", engine="openpyxl")
    print("✅ Data saved to linkedin_companies.xlsx")

    # Auto-adjust Excel column widths
    wb = load_workbook(excel_file)
    ws = wb.active
    for column_cells in ws.columns:
        max_length = 0
        col_letter = column_cells[0].column_letter
        for cell in column_cells:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        ws.column_dimensions[col_letter].width = max_length + 2
    wb.save(excel_file)
    print("✨ Excel column widths auto-adjusted")
else:
    print("⚠️ No company data extracted!")

driver.quit()

