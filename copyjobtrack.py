import requests
import pandas as pd
from datetime import datetime, timedelta
import os

# ---------------- CONFIG ----------------
API_KEY = "2be76dd991mshed2056c0843d960p103d1ejsn0b7e976cb8a2"  # Your RapidAPI Key
KEYWORDS = [
    "AWS Fresher", "Azure Fresher", "GCP Fresher", "Cloud Engineer Fresher",
    "DevOps Engineer Fresher", "DevOps Trainee", "SRE Intern", "CI/CD Fresher",
    "Docker Intern", "Kubernetes Trainee", "Jenkins Fresher", "Terraform Intern",
    "Walk-in", "Intern", "Trainee", "Fresher"
]
LOCATIONS = ["Bengaluru"]  # Add more cities if needed
OUTPUT_FILE = "job_tracker.xlsx"
DAYS_TO_KEEP = 2  # Only keep jobs from the last 2 days
# -----------------------------------------

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

def fetch_jobs(keyword, location):
    url = "https://jsearch.p.rapidapi.com/search"
    querystring = {"query": f"{keyword} in {location}", "num_pages": "1"}
    response = requests.get(url, headers=HEADERS, params=querystring)
    data = response.json()
    jobs = []

    for job in data.get("data", []):
        title = job.get("job_title", "")
        if any(word.lower() in title.lower() for word in ["fresher", "walk-in", "intern", "trainee"]):
            jobs.append({
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Job Title": title,
                "Company": job.get("employer_name", ""),
                "Location": job.get("job_city") or location,
                "Source": job.get("job_publisher", ""),
                "Apply Link": job.get("job_apply_link", ""),
                "Keyword": keyword
            })
    return jobs

def main():
    all_jobs = []

    for location in LOCATIONS:
        for keyword in KEYWORDS:
            print(f"🔍 Fetching '{keyword}' jobs in {location}...")
            try:
                jobs = fetch_jobs(keyword, location)
                all_jobs.extend(jobs)
            except Exception as e:
                print("Error:", e)

    if not all_jobs:
        print("⚠️ No jobs found today.")
        return

    df_new = pd.DataFrame(all_jobs)
    df_new.drop_duplicates(subset=["Apply Link"], inplace=True)

    # Load existing jobs and remove outdated ones
    if os.path.exists(OUTPUT_FILE):
        df_old = pd.read_excel(OUTPUT_FILE)
        df_old['Date'] = pd.to_datetime(df_old['Date'])
        cutoff = datetime.now() - timedelta(days=DAYS_TO_KEEP)
        df_old = df_old[df_old['Date'] >= cutoff]  # Keep only recent jobs
        df_combined = pd.concat([df_old, df_new], ignore_index=True)
        df_combined.drop_duplicates(subset=["Apply Link"], inplace=True)
    else:
        df_combined = df_new

    df_combined.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ Saved {len(df_new)} new jobs. Total tracked (last {DAYS_TO_KEEP} days): {len(df_combined)}")
    print(f"📁 File: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

