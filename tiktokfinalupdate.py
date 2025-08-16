from selenium.webdriver.chrome.webdriver import WebDriver
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




def human_type(element, text, min_delay=0.1, max_delay=0.3):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

# def get_stealth_chrome_options():
#     mobile_emulation = { "deviceName": "Pixel 5" }
#     options = uc.ChromeOptions()
    
#     # General stealth settings
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     # Spoof language and user-agent
#     options.add_argument("--lang=en-US,en;q=0.9")
#     options.add_argument(
#         "user-agent=Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/114.0.0.0 Safari/537.36"
#     )

#     return options



def get_stealth_chrome_options():
    options = uc.ChromeOptions()

    # ✅ Mobile user-agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Linux; Android 11; Pixel 5 Build/RQ3A.210905.001) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.131 Mobile Safari/537.36"
    )

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US,en;q=0.9")

    options.add_argument("--headless=new")

    return options



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


# def read_tiktok_email(timeout=60):
#     print("⏳ Waiting for TikTok email...")

#     # Step 1: connect and count current inbox emails
#     mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
#     mail.login(EMAIL, PASSWORD)
#     mail.select("inbox")
#     status, initial_messages = mail.search(None, "ALL")
    
#     existing_ids = set(initial_messages[0].split())
#     mail.logout()

#     # Step 2: poll for new message
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         # time.sleep(5)
#         time.sleep(2)
#         mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")

#         status, current_messages = mail.search(None, '(SUBJECT "verification code")')
#         current_ids = set(current_messages[0].split())
#         new_ids = list(current_ids - existing_ids)


#         if new_ids:
#             latest_id = sorted(new_ids)[-1]  # pick the latest of the new ones
#             status, msg_data = mail.fetch(latest_id, "(RFC822)")

#             for response_part in msg_data:
#                 if isinstance(response_part, tuple):
#                     msg = email.message_from_bytes(response_part[1])
#                     subject = clean_subject(msg["Subject"])
#                     sender = msg["From"]
#                     print(f"📨 New Email From: {sender} | Subject: {subject}")

#                     if msg.is_multipart():
#                         for part in msg.walk():
#                             if part.get_content_type() == "text/plain":
#                                 body = part.get_payload(decode=True).decode()
#                                 code = extract_verification_code(body)
#                                 if code:
#                                     print(f"✅ Extracted TikTok Code: {code}")
#                                     mail.logout()
#                                     return code
#                     else:
#                         body = msg.get_payload(decode=True).decode()
#                         code = extract_verification_code(body)
#                         if code:
#                             print(f"✅ Extracted TikTok Code: {code}")
#                             mail.logout()
#                             return code

#         mail.logout()

#     raise Exception("❌ No new TikTok verification email arrived in time.")


def read_tiktok_email(timeout=60):
    print("⏳ Waiting for TikTok email...")

    start_time = time.time()

    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        while time.time() - start_time < timeout:
            time.sleep(1)

            # Search for unseen emails from TikTok
            status, messages = mail.search(None, '(UNSEEN SUBJECT "verification code")')
            message_ids = messages[0].split()

            for msg_id in reversed(message_ids):  # Newest first
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = clean_subject(msg["Subject"])
                        sender = msg.get("From", "")

                        if "tiktok.com" in sender.lower() or "verification code" in subject.lower():
                            print(f"📨 Email from: {sender} | Subject: {subject}")

                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode()
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode()

                            code = extract_verification_code(body)
                            if code:
                                print(f"✅ Verification code: {code}")
                                mail.logout()
                                return code

        mail.logout()
        raise Exception("❌ Verification code not received in time.")

    except Exception as e:
        print("📡 Email fetch error:", e)
        raise









def create_tiktok_account():

    # def enable_mobile_emulation(driver: WebDriver):
    #     driver.execute_cdp_cmd('Emulation.setUserAgentOverride', {
    #         "userAgent": "Mozilla/5.0 (Linux; Android 11; Pixel 5 Build/RQ3A.210905.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.131 Mobile Safari/537.36",
    #         "platform": "Android"
    #     })
    #     driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
    #         "width": 412,
    #         "height": 915,
    #         "deviceScaleFactor": 3.0,
    #         "mobile": True
    #     })


    email = generate_random_email()
    password = generate_random_password()

    print("Generated Email:", email)
    print("Generated Password:", password)

    options = get_stealth_chrome_options()
    # options = uc.ChromeOptions()
    # options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    # enable_mobile_emulation(driver)

    wait = WebDriverWait(driver, 20)

    driver.get("https://www.tiktok.com/signup/phone-or-email/email")

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # --- DOB Selection ---
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        selected_month = random.choice(months)
        selected_day = str(random.randint(1, 28))
        selected_year = str(random.randint(1990, 2000))

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Month. Double-tap for more options']"))).click()
        time.sleep(random.uniform(0.5, 1.2))

        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_month}']"))).click()

        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Day. Double-tap for more options']"))).click()
        time.sleep(random.uniform(0.3, 0.8))
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_day}']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Year. Double-tap for more options']"))).click()
        time.sleep(random.uniform(0.1, 0.3))
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_year}']"))).click()


        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        human_type(email_input, email)


        ActionChains(driver).move_by_offset(random.randint(5, 100), random.randint(5, 100)).perform()
        time.sleep(1)

        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' and @placeholder='Password']")))
        human_type(password_input, password)

        ActionChains(driver).move_by_offset(random.randint(5, 100), random.randint(5, 100)).perform()
        time.sleep(1)


        # wait.until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(email)
        # wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' and @placeholder='Password']"))).send_keys(password)

        send_code_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-e2e='send-code-button']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", send_code_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", send_code_button)
        print("📤 Clicked 'Send Code' button.")

        # sheet.append_row([email, password, time.strftime("%Y-%m-%d %H:%M:%S")])
        

        # --- Get Verification Code & Enter ---
        code = read_tiktok_email()

        try:
            code_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter 6-digit code']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", code_input)
            time.sleep(1)
            human_type(code_input, code)

            print("✅ Entered verification code.")
        except Exception as e:
            print("❌ Failed to find or interact with the verification code input field.")
            driver.save_screenshot("code_input_error.png")
            raise e

        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']")))
        driver.execute_script("arguments[0].click();", next_button)
        print("➡️ Clicked Next.")

    ## --- Wait for Username Screen and Complete Signup ---
        def generate_fake_word(syllables=3):
            consonants = "bcdfghjklmnpqrstvwxyz"
            vowels = "aeiou"
            word = ""
            for _ in range(syllables):
             word += random.choice(consonants) + random.choice(vowels)
            return word

        def generate_valid_username():
            base = generate_fake_word(syllables=random.randint(2, 4))  # e.g., "zubora"
            suffix = ''.join(random.choices(string.digits + string.ascii_lowercase, k=random.randint(2, 4)))  # e.g., "q9"
            return base + suffix
        
        
        try:
            username_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
            )
            final_username = generate_valid_username()
            human_type(username_input, final_username)
            print(f"🔤 Typed final username: {final_username}")

            time.sleep(1)  # Short delay before clicking Sign Up

            signup_button_xpath = "//button[contains(text(), 'Sign up') and not(@disabled)]"
            signup_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, signup_button_xpath))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", signup_button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", signup_button)
            print("✅ Clicked 'Sign up' button.")

            sheet.append_row([email, password, final_username, time.strftime("%Y-%m-%d %H:%M:%S")])
            print("📄 Credentials saved to Google Sheet.")

        except Exception as e:
            print("❌ Failed to enter username or sign up:", e)
            driver.save_screenshot("username_error.png")

    except Exception as e:
        print("⚠️ Error:", e)
        input("Press Enter to quit browser after error...")
    finally:
        time.sleep(3)
        driver.quit()


# ------------------------ RUN ------------------------
if __name__ == "__main__":
    for i in range(100):
        print(f"\n🚀 Creating Account {i+1}/100...\n")
        try:
            create_tiktok_account()
        except Exception as e:
            print(f"⚠️ Error on account {i+1}: {e}")
        print("⏳ Waiting before next attempt...\n")
        time.sleep(random.uniform(2, 4))  # Small delay between accounts




# ------------------------ RUN ------------------------
# if __name__ == "__main__":
#     create_tiktok_account()



