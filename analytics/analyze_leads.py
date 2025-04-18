import pandas as pd

log_file = "email_log.csv"
open_log = "open_logs.csv"

# Load logs
emails = pd.read_csv(log_file)
opens = pd.read_csv(open_log, names=["Email", "Action", "Time"])

# Add engagement column
emails["LeadStatus"] = "Cold"

for i, row in emails.iterrows():
    email = row["Email"]
    engagement = opens[opens["Email"] == email]
    if not engagement.empty:
        if "click" in engagement["Action"].values:
            status = "Hot"
        elif "open" in engagement["Action"].values:
            status = "Warm"
        else:
            status = "Cold"
        emails.at[i, "LeadStatus"] = status

# Save updated CSV
emails.to_csv("analytics_output.csv", index=False)
print("✅ Categorized leads and saved to analytics_output.csv")

# Print summary
print("📊 Campaign Summary:")
print("Total Sent:", len(emails))
print("Hot Leads:", len(emails[emails["LeadStatus"] == "Hot"]))
print("Warm Leads:", len(emails[emails["LeadStatus"] == "Warm"]))
print("Cold Leads:", len(emails[emails["LeadStatus"] == "Cold"]))
