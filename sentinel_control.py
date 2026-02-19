import os
import subprocess
import glob
from twilio.rest import Client
from dotenv import load_dotenv 

# 1. Load the "Secret Lockbox" from your specific path
load_dotenv(r"C:\OneDrive\PublicReports\File Storage\.env")

# 2. Assign the keys from the lockbox (No hardcoded tokens here!)
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# 3. System Configuration
GITHUB_USER = "bernievcooke-cloud"
REPO_NAME = "Sentinel-Access"
BASE_PATH = r"C:\OneDrive\PublicReports\OUTPUT"
FROM_WHATSAPP = 'whatsapp:+14155238886'
TO_WHATSAPP = 'whatsapp:+61409139355'

def get_latest_report(location):
    """Finds the most recent PDF in the subfolder."""
    search_path = os.path.join(BASE_PATH, location, "*.pdf")
    files = glob.glob(search_path)
    return max(files, key=os.path.getmtime) if files else None

def deploy_and_notify(location):
    report_path = get_latest_report(location)
    if not report_path:
        print(f"❌ No PDF found in OUTPUT/{location}")
        return

    filename = os.path.basename(report_path)
    print(f"🚀 Processing: {filename}")

    try:
        # 1. GitHub Sync
        subprocess.run(["git", "add", "."], check=True)
        # We use shell=True and a simple string to prevent 'nothing to commit' from crashing the script
        subprocess.run(f'git commit -m "Auto-Sync: {filename}"', shell=True) 
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        
        # 2. Build URL (Ensuring spaces are handled for web)
        live_url = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/OUTPUT/{location}/{filename}".replace(" ", "%20")
        
        # 3. Primary WhatsApp Dispatch
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=f"🌊 *Sentinel Report Ready*\nLocation: {location}\n\nView: {live_url}",
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP
        )
        print(f"✅ WhatsApp Sent! SID: {message.sid}")
        
    except Exception as e:
        print(f"⚠️ Sync/Twilio Note: {e}")
        print("🔄 Attempting fallback WhatsApp dispatch...")
        send_only_whatsapp(location, filename)

def send_only_whatsapp(location, filename):
    """Fallback method if the main sync loop hits a snag."""
    live_url = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/OUTPUT/{location}/{filename}".replace(" ", "%20")
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        client.messages.create(
            body=f"🌊 *Sentinel Report Ready*\nLocation: {location}\n\nView: {live_url}",
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP
        )
        print("✅ WhatsApp sent successfully using existing cloud file.")
    except Exception as e:
        print(f"❌ Twilio still failing: {e}")
        print(f"🔗 IMPORTANT: Your file is likely live at: {live_url}")

def main_menu():
    while True:
        print("\n--- Sentinel Access: User Selection ---")
        print("1. Phillip Island (Latest)")
        print("2. Bells Beach (Latest)")
        print("3. Exit")
        choice = input("Select (1-3): ")
        
        if choice == '1': 
            deploy_and_notify("PhillipIsland")
        elif choice == '2': 
            deploy_and_notify("BellsBeach")
        elif choice == '3': 
            print("Exiting Sentinel Control.")
            break

if __name__ == "__main__":
    main_menu()