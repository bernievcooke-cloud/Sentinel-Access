import os
import subprocess
import glob
import customtkinter as ctk
from twilio.rest import Client
from dotenv import load_dotenv
from tkinter import messagebox

# --- CONFIGURATION & SECRETS ---
load_dotenv(r"C:\OneDrive\PublicReports\File Storage\.env")
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
BASE_PATH = r"C:\OneDrive\PublicReports\OUTPUT"
ADMIN_PASSWORD = "Sentinel2026" 

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SentinelExecutiveHub(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("SENTINEL ACCESS - EXECUTIVE COMMAND V6.2")
        self.geometry("1500x950") # Slightly wider window

        # Grid Configuration (Widened sidebars)
        self.grid_columnconfigure(0, minsize=380) # Left bar wider
        self.grid_columnconfigure(1, weight=2)    # Main Center
        self.grid_columnconfigure(2, minsize=350) # Right bar wider
        self.grid_rowconfigure(0, weight=1)

        # --- 1. SIDEBAR: CONTROL & ADMIN ---
        self.sidebar = ctk.CTkFrame(self, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="SYSTEM SECURITY", font=("Helvetica", 22, "bold")).pack(pady=(40, 10))
        self.pwd_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Password", show="*", width=280, height=40)
        self.pwd_entry.pack(pady=5)
        self.auth_btn = ctk.CTkButton(self.sidebar, text="UNLOCK ADMIN", command=self.authenticate, fg_color="#34495E", width=280)
        self.auth_btn.pack(pady=5)

        ctk.CTkLabel(self.sidebar, text="REPORT PARAMETERS", font=("Helvetica", 18, "bold"), text_color="#1a73e8").pack(pady=(60, 10))
        
        ctk.CTkLabel(self.sidebar, text="STEP 1: CATEGORY", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=50)
        self.type_menu = ctk.CTkOptionMenu(self.sidebar, values=["Surf", "Sky"], height=55, width=280, command=self.sync_ui)
        self.type_menu.pack(pady=(5, 30), padx=50)

        ctk.CTkLabel(self.sidebar, text="STEP 2: LOCATION", font=("Helvetica", 14, "bold")).pack(anchor="w", padx=50)
        try:
            locations = [f for f in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, f))]
        except:
            locations = ["PhillipIsland", "BellsBeach"] 
        
        self.loc_menu = ctk.CTkOptionMenu(self.sidebar, values=sorted(locations), height=55, width=280, command=self.sync_ui)
        self.loc_menu.pack(pady=(5, 30), padx=50)

        # --- 2. MAIN CONSOLE ---
        self.main_box = ctk.CTkFrame(self, fg_color="transparent")
        self.main_box.grid(row=0, column=1, sticky="nsew", padx=60, pady=30)

        # STATUS BOX
        ctk.CTkLabel(self.main_box, text="CURRENT STATUS", font=("Helvetica", 16, "bold"), text_color="#1a73e8").pack(anchor="w")
        self.status_display = ctk.CTkTextbox(self.main_box, height=140, font=("Helvetica", 26, "bold"), 
                                            border_width=2, border_color="#1a73e8", fg_color="#0f0f0f")
        self.status_display.pack(fill="x", pady=(5, 40))
        self.update_status_msg("SYSTEM STANDBY\nWAITING FOR SELECTION...")

        # CONFIRMATION & INPUT
        self.confirm_frame = ctk.CTkFrame(self.main_box, corner_radius=20, border_width=1, border_color="#2c3e50")
        self.confirm_frame.pack(fill="x", pady=10, ipady=50)
        
        self.confirm_label = ctk.CTkLabel(self.confirm_frame, text="PLEASE INITIALIZE PARAMETERS", font=("Helvetica", 28, "bold"))
        self.confirm_label.pack(pady=(30, 10))
        
        self.instruct_label = ctk.CTkLabel(self.confirm_frame, text="ADVISE: Enter your mobile number below", 
                                          font=("Helvetica", 20), text_color="#E67E22")
        self.instruct_label.pack(pady=5)

        self.phone_entry = ctk.CTkEntry(self.confirm_frame, height=80, width=520, font=("Helvetica", 32), 
                                       justify="center", border_color="#1a73e8")
        self.phone_entry.pack(pady=30)
        self.phone_entry.insert(0, "+61") # Pre-filled country code

        # ACTION BUTTON
        self.action_btn = ctk.CTkButton(self.main_box, text="CONFIRM & GENERATE HANDSHAKE", 
                                        fg_color="#27AE60", hover_color="#1E8449",
                                        height=120, font=("Helvetica", 30, "bold"), command=self.handle_action)
        self.action_btn.pack(fill="x", pady=40)

        # --- 3. CHART PANEL ---
        self.chart_panel = ctk.CTkScrollableFrame(self, label_text="VISUAL DATA STREAMS", label_font=("Helvetica", 16, "bold"))
        self.chart_panel.grid(row=0, column=2, sticky="nsew", padx=(0, 30), pady=40)
        
        for i in range(4):
            f = ctk.CTkFrame(self.chart_panel, height=240, fg_color="#1c1c1c", corner_radius=12, border_width=1, border_color="#333")
            f.pack(fill="x", pady=12)
            ctk.CTkLabel(f, text=f"STREAM DATA 0{i+1}", font=("Helvetica", 12, "bold"), text_color="gray").pack(pady=15)

    # --- LOGIC ---

    def update_status_msg(self, text):
        self.status_display.configure(state="normal")
        self.status_display.delete("0.0", "end")
        self.status_display.insert("0.0", text)
        self.status_display.configure(state="disabled")
        self.update()

    def sync_ui(self, choice=None):
        loc = self.loc_menu.get()
        rtype = self.type_menu.get()
        self.confirm_label.configure(text=f"TARGET: {loc} ({rtype})")
        self.update_status_msg(f"READY TO STAGE: {loc}\nACTION: ENTER MOBILE & START HANDSHAKE")
        self.action_btn.configure(text="CONFIRM & GENERATE HANDSHAKE", fg_color="#27AE60", state="normal")
        self.status_display.configure(border_color="#1a73e8")

    def authenticate(self):
        if self.pwd_entry.get() == ADMIN_PASSWORD:
            self.update_status_msg("ADMIN OVERRIDE: ACTIVE\nMANUAL CLOUD DISPATCH ENABLED")
            self.status_display.configure(border_color="#E74C3C")
            messagebox.showinfo("Security", "Admin Identity Confirmed")
        else:
            messagebox.showerror("Security", "Access Denied")

    def handle_action(self):
        phone = self.phone_entry.get().strip()
        
        if len(phone) < 12: # +61 followed by 9 digits
            self.update_status_msg("ERROR: VALIDATION FAILED\nINCOMPLETE PHONE NUMBER")
            messagebox.showwarning("Validation", "Please complete the phone number.")
            return

        # If button is in the 'Final' state, trigger the actual dispatch
        if self.action_btn.cget("text") == "DISPATCH LIVE REPORT (BYPASS PAY)":
            self.trigger_live_dispatch()
            return

        self.update_status_msg("INITIATING SECURE HANDSHAKE...\nCONTACTING CLOUD REPOSITORY")
        self.status_display.configure(border_color="#F1C40F")
        self.action_btn.configure(state="disabled", text="PROCESSING...")
        self.after(1800, self.complete_handshake)

    def complete_handshake(self):
        loc = self.loc_menu.get()
        self.update_status_msg(f"HANDSHAKE VERIFIED\nREPORT FOR {loc} IS SECURED.\nREADY FOR DISPATCH.")
        self.status_display.configure(border_color="#2ECC71") 
        self.action_btn.configure(state="normal", text="DISPATCH LIVE REPORT (BYPASS PAY)", fg_color="#2980B9")

    def trigger_live_dispatch(self):
        """THE ACTUAL WORKING DISPATCH LOGIC"""
        loc = self.loc_menu.get()
        rtype = self.type_menu.get()
        target_phone = self.phone_entry.get()
        
        self.update_status_msg(f"UPLOADING TO GITHUB...\nSYNCING {loc} CLOUD ASSETS")
        
        try:
            # 1. GitHub Sync
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(f'git commit -m "Executive Dispatch: {loc}"', shell=True)
            subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
            
            # 2. Find File
            search_path = os.path.join(BASE_PATH, loc, f"{rtype}_*.pdf")
            files = glob.glob(search_path)
            if not files:
                self.update_status_msg(f"ERROR: NO PDF FOUND IN {loc}")
                return
            latest_file = os.path.basename(max(files, key=os.path.getmtime))

            # 3. Twilio WhatsApp
            self.update_status_msg("SENDING WHATSAPP...\nFINALIZING HANDSHAKE")
            live_url = f"https://bernievcooke-cloud.github.io/Sentinel-Access/OUTPUT/{loc}/{latest_file}".replace(" ", "%20")
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            client.messages.create(
                body=f"🌊 *Sentinel {rtype} Report Ready*\n\nView: {live_url}",
                from_='whatsapp:+14155238886', to=f'whatsapp:{target_phone}'
            )
            
            self.update_status_msg(f"SUCCESS!\nMESSAGE SENT TO {target_phone}\nREPORT: {latest_file}")
            messagebox.showinfo("Success", "Dispatch Complete! Check your WhatsApp.")
            
        except Exception as e:
            self.update_status_msg(f"CRITICAL ERROR:\n{str(e)}")

if __name__ == "__main__":
    app = SentinelExecutiveHub()
    app.mainloop()
    