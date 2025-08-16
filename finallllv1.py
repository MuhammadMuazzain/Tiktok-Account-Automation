
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string
import os
import imaplib
import email
from email.header import decode_header
import re
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# ---------- Load proxies from file ----------
def load_proxies(file_path="proxies.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# ---------- Start Chrome with a specific proxy ----------
def start_browser_with_proxy(proxy_string):
    ip, port, user, pwd = proxy_string.split(":")
    proxy = f"http://{user}:{pwd}@{ip}:{port}"

    options = uc.ChromeOptions()
    options.add_argument(f'--proxy-server={proxy}')
    options.add_argument('--start-maximized')

    driver = uc.Chrome(options=options)
    return driver


# ------------------------ CONFIGURATION ------------------------
load_dotenv()
EMAIL = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER")
IMAP_PORT = int(os.getenv("IMAP_PORT"))

# ------------------------ GOOGLE SHEETS SETUP ------------------------
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Link_to_python").worksheet("Sheet1")

# ------------------------ EMAIL & PASSWORD GENERATION ------------------------
def generate_random_email(domain="arksbaymarketing.com"):
    username = 'im' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{username}@{domain}"

def generate_random_password():
    letters = string.ascii_letters
    digits = string.digits
    special = "!@#$%^&*()-_=+"
    password = [random.choice(letters), random.choice(digits), random.choice(special)]
    remaining_length = random.randint(5, 13)
    all_chars = letters + digits + special
    password += random.choices(all_chars, k=remaining_length)
    random.shuffle(password)
    return ''.join(password)

# ------------------------ EMAIL READING ------------------------
def clean_subject(subject):
    decoded, charset = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or 'utf-8')
    return decoded

def extract_verification_code(text):
    matches = re.findall(r"\b\d{6}\b", text)
    return matches[0] if matches else None

def read_tiktok_email(timeout=60):
    print("⏳ Waiting for TikTok email...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    status, initial_messages = mail.search(None, "ALL")
    existing_ids = set(initial_messages[0].split())
    mail.logout()

    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(5)
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        status, current_messages = mail.search(None, '(SUBJECT "verification code")')
        current_ids = set(current_messages[0].split())
        new_ids = list(current_ids - existing_ids)

        if new_ids:
            latest_id = sorted(new_ids)[-1]
            status, msg_data = mail.fetch(latest_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = clean_subject(msg["Subject"])
                    sender = msg["From"]
                    print(f"📨 New Email From: {sender} | Subject: {subject}")

                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                code = extract_verification_code(body)
                                if code:
                                    print(f"✅ Extracted TikTok Code: {code}")
                                    mail.logout()
                                    return code
                    else:
                        body = msg.get_payload(decode=True).decode()
                        code = extract_verification_code(body)
                        if code:
                            print(f"✅ Extracted TikTok Code: {code}")
                            mail.logout()
                            return code

        mail.logout()

    raise Exception("❌ No new TikTok verification email arrived in time.")

# ------------------------ MAIN ------------------------
def create_tiktok_account(driver):
    wait = WebDriverWait(driver, 20)

    email = generate_random_email()
    password = generate_random_password()
    print("Generated Email:", email)
    print("Generated Password:", password)

    driver.get("https://www.tiktok.com/signup/phone-or-email/email")

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    selected_month = random.choice(months)
    selected_day = str(random.randint(1, 28))
    selected_year = str(random.randint(1990, 2000))

    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Month. Double-tap for more options']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_month}']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Day. Double-tap for more options']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_day}']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Year. Double-tap for more options']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_year}']"))).click()

    wait.until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(email)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' and @placeholder='Password']"))).send_keys(password)
    send_code_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-e2e='send-code-button']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", send_code_button)
    time.sleep(1)
    driver.execute_script("arguments[0].click();", send_code_button)
    print("📤 Clicked 'Send Code' button.")

    sheet.append_row([email, password, time.strftime("%Y-%m-%d %H:%M:%S")])
    print("📄 Saved basic info to Google Sheet.")

    code = read_tiktok_email()

    code_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter 6-digit code']")))
    code_input.send_keys(code)
    print("✅ Entered verification code.")

    next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']")))
    driver.execute_script("arguments[0].click();", next_button)
    print("➡️ Clicked Next.")

    # Username stage
    def generate_valid_username():
        return ''.join(random.choices(string.ascii_lowercase, k=1)) + ''.join(random.choices(string.ascii_lowercase + string.digits + "_.", k=5))

    username_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    partial = ''.join(random.choices(string.ascii_lowercase, k=5))
    username_input.send_keys(partial)
    print(f"🔤 Typed base username: {partial}")
    time.sleep(2)

    final_username = partial
    try:
        suggestion = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'UlList')]//li[1]")))
        final_username = suggestion.text
        suggestion.click()
        print(f"✅ Selected suggested username: {final_username}")
    except:
        print("⚠️ No suggestions — using typed username.")

    signup_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign up') and not(@disabled)]")))
    driver.execute_script("arguments[0].click();", signup_button)
    print("✅ Finished Signup.")

    sheet.append_row([email, password, final_username, time.strftime("%Y-%m-%d %H:%M:%S")])
    print("📄 Saved full credentials to Google Sheet.")

# ------------------------ DRIVER LOOP ------------------------
if __name__ == "__main__":
    proxies = load_proxies("proxies.txt")
    for proxy in proxies:
        print(f"🔄 Using proxy: {proxy}")
        try:
            driver = start_browser_with_proxy(proxy)
            create_tiktok_account(driver)
            input("✅ Done. Press Enter to continue...")
            driver.quit()
        except Exception as e:
            print(f"❌ Error with proxy {proxy}: {e}")
            try:
                driver.quit()
            except:
                pass
