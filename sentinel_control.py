import subprocess
from twilio.rest import Client

# --- USER CONFIGURATION ---
GITHUB_USER = "bernievcooke-cloud"
REPO_NAME = "Sentinel-Access"

# Twilio Credentials (provided by you)
ACCOUNT_SID = 'AC2e9c9be175911cce282ad3109c53ade5'
AUTH_TOKEN = '0820479e9367a679294fce8a615f11bf'
FROM_WHATSAPP = 'whatsapp:+14155238886'
TO_WHATSAPP = 'whatsapp:+61409139355'

def deploy_and_notify(report_filename):
    """Pushes report to GitHub and sends the WhatsApp link."""
    # 1. GitHub Push (The Automator)
    print(f"🚀 Uploading {report_filename} to the Cloud...")
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Manual Report: {report_filename}"], check=True)
        # We use --force to ensure the user choice always overrides the cloud
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        
        # 2. Build the Live URL
        # Path assumes your PDFs are in an 'OUTPUT' folder within the repo
        live_url = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/OUTPUT/{report_filename}"
        
        # 3. Twilio WhatsApp Dispatch
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message_body = f"🌊 *Sentinel Report Ready*\nLocation: {report_filename.split('.')[0]}\n\nView PDF: {live_url}"
        
        message = client.messages.create(
            body=message_body,
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP
        )
        print(f"✅ WhatsApp Sent! SID: {message.sid}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main_menu():
    while True:
        print("\n--- Sentinel Access: User Selection ---")
        print("1. Bells Beach Report")
        print("2. Jan Juc Report")
        print("3. Exit")
        
        choice = input("Select a report to generate and send (1-3): ")
        
        if choice == '1':
            deploy_and_notify("BellsBeach.pdf")
        elif choice == '2':
            deploy_and_notify("JanJuc.pdf")
        elif choice == '3':
            print("Exiting Sentinel Framework.")
            break
        else:
            print("Invalid choice. Please pick 1, 2, or 3.")

if __name__ == "__main__":
    main_menu()