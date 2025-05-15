import time
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired
from getpass import getpass

# ---------------- CONFIG ----------------
OWNER_USERNAMES = ["owner_username1", "owner_username2"]  # Replace with real usernames
REPLY_DELAY = 0.5  # seconds
REPLY_TEXT = "𝕆𝕀 𝕄𝕊𝔾 𝕄𝕋 𝕂ℝ 𝕍ℝℕ𝔸 𝕋𝔼ℝ𝕀 𝕄𝔸𝔸 𝕏ℍ𝕆𝔻 𝔻𝕌ℕ𝔾𝔸 😆🤣"

# ---------------- MAIN BOT ----------------
cl = Client()
owner_ids = []
last_message_ids = {}

def ask_credentials():
    username = input("Enter your Instagram username: ")
    password = getpass("Enter your Instagram password: ")
    return username, password

def handle_challenge(username):
    print("[*] Login triggered a challenge. Trying to send code to email...")
    try:
        cl.challenge_resolve(auto=True)
        code = input("[?] Enter the security code sent to your email: ").strip()
        cl.challenge_send_security_code(code)
    except Exception as e:
        print("[-] Failed to resolve challenge:", e)
        exit()

def login_flow():
    username, password = ask_credentials()
    try:
        cl.login(username, password)
    except ChallengeRequired:
        handle_challenge(username)
    except Exception as e:
        print("[-] Login failed:", e)
        exit()
    
    print(f"[+] Logged in as {username}")
    return cl.user_id_from_username(username)

def resolve_owner_ids():
    for uname in OWNER_USERNAMES:
        try:
            uid = cl.user_id_from_username(uname)
            owner_ids.append(uid)
        except:
            print(f"[-] Failed to get user ID for owner '{uname}'")

def monitor_groups(self_id):
    print("[✓] Monitoring group chats...")

    while True:
        threads = cl.direct_threads()
        for thread in threads:
            if len(thread.users) <= 1:
                continue  # Skip if not a group

            thread_id = thread.id
            messages = cl.direct_messages(thread_id, amount=5)
            messages.reverse()

            if thread_id not in last_message_ids:
                last_message_ids[thread_id] = []

            for msg in messages:
                msg_id = msg.id
                if msg_id in last_message_ids[thread_id]:
                    continue

                last_message_ids[thread_id].append(msg_id)
                if len(last_message_ids[thread_id]) > 5:
                    last_message_ids[thread_id].pop(0)

                sender_id = msg.user_id
                if sender_id in owner_ids or sender_id == self_id:
                    continue

                sender_username = cl.user_info(sender_id).username
                reply = f"@{sender_username} {REPLY_TEXT}"
                cl.direct_send(reply, thread_ids=[thread_id])
                print(f"[✓] Replied to @{sender_username} in thread {thread_id}")
                time.sleep(REPLY_DELAY)

        time.sleep(1)

# ---------------- START ----------------
if __name__ == "__main__":
    self_user_id = login_flow()
    resolve_owner_ids()
    monitor_groups(self_user_id)
