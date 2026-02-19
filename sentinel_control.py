import os
import subprocess
import glob
from twilio.rest import Client

# --- CONFIG ---
GITHUB_USER = "bernievcooke-cloud"
REPO_NAME = "Sentinel-Access"
BASE_PATH = r"C:\OneDrive\PublicReports\OUTPUT"

# Twilio Credentials
ACCOUNT_SID = 'AC2e9c9be175911cce282ad3109c53ade5'
AUTH_TOKEN = '0820479e9367a679294fce8a615f11bf' # Ensure this is fresh from Console
FROM_WHATSAPP = 'whatsapp:+14155238886'
TO_WHATSAPP = 'whatsapp:+61409139355'

def get_latest_report(location):
    """Finds the newest PDF in the specific location folder."""
    search_path = os.path.join(BASE_PATH, location, "*.pdf")
    files = glob.glob(search_path)
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def deploy_and_notify(location):
    report_path = get_latest_report(location)
    
    if not report_path:
        print(f"❌ No PDF found in OUTPUT/{location}")
        return

    filename = os.path.basename(report_path)
    print(f"🚀 Found latest report: {filename}")

    try:
        # 1. Sync to GitHub
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-Sync: {filename}"], check=True)
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        
        # 2. Build URL (Note: GitHub URLs are case-sensitive)
        live_url = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/OUTPUT/{location}/{filename}".replace(" ", "%20")
        
        # 3. WhatsApp Dispatch
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=f"🌊 *Sentinel Report Ready*\nLocation: {location}\nFile: {filename}\n\nView: {live_url}",
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP
        )
        print(f"✅ WhatsApp Sent! SID: {message.sid}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main_menu():
    while True:
        print("\n--- Sentinel Access: User Selection ---")
        print("1. Phillip Island (Latest)")
        print("2. Bells Beach (Latest)")
        print("3. Exit")
        choice = input("Select (1-3): ")
        
        if choice == '1': deploy_and_notify("PhillipIsland")
        elif choice == '2': deploy_and_notify("BellsBeach")
        elif choice == '3': break

if __name__ == "__main__":
    main_menu()