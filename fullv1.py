
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
def generate_random_email(domain="Arksbaymarketing.com"):
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
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
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")
#         status, messages = mail.search(None, '(SUBJECT "verification code")')
#         email_ids = messages[0].split()

#         if email_ids:
#             latest_id = email_ids[-1]
#             status, msg_data = mail.fetch(latest_id, "(RFC822)")
#             for response_part in msg_data:
#                 if isinstance(response_part, tuple):
#                     msg = email.message_from_bytes(response_part[1])
#                     subject = clean_subject(msg["Subject"])
#                     sender = msg["From"]
#                     print(f"📨 From: {sender} | Subject: {subject}")

#                     if msg.is_multipart():
#                         for part in msg.walk():
#                             if part.get_content_type() == "text/plain":
#                                 body = part.get_payload(decode=True).decode()
#                                 code = extract_verification_code(body)
#                                 if code:
#                                     print(f"✅ TikTok verification code: {code}")
#                                     return code
#                     else:
#                         body = msg.get_payload(decode=True).decode()
#                         code = extract_verification_code(body)
#                         if code:
#                             print(f"✅ TikTok verification code: {code}")
#                             return code
#         mail.logout()
#         time.sleep(5)
#     raise Exception("❌ Verification email not received within timeout.")

def read_tiktok_email(timeout=60):
    print("⏳ Waiting for TikTok email...")

    # Step 1: connect and count current inbox emails
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    status, initial_messages = mail.search(None, "ALL")
    
    existing_ids = set(initial_messages[0].split())
    mail.logout()

    # Step 2: poll for new message
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(5)
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        status, current_messages = mail.search(None, '(SUBJECT "verification code")')
        current_ids = set(current_messages[0].split())
        new_ids = list(current_ids - existing_ids)

        
        # status, current_messages = mail.search(None, "ALL")
        # current_ids = set(current_messages[0].split())
        # new_ids = list(current_ids - existing_ids)

        if new_ids:
            latest_id = sorted(new_ids)[-1]  # pick the latest of the new ones
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


# ------------------------ MAIN TIKTOK AUTOMATION ------------------------
# def create_tiktok_account():
#     email = generate_random_email()
#     password = generate_random_password()

#     print("Generated Email:", email)
#     print("Generated Password:", password)

#     options = uc.ChromeOptions()
#     options.add_argument("--start-maximized")
#     driver = uc.Chrome(options=options)
#     wait = WebDriverWait(driver, 20)

#     driver.get("https://www.tiktok.com/signup/phone-or-email/email")

#     try:
#         wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

#         # --- DOB Selection ---
#         months = ["January", "February", "March", "April", "May", "June",
#                   "July", "August", "September", "October", "November", "December"]
#         selected_month = random.choice(months)
#         selected_day = str(random.randint(1, 28))
#         selected_year = str(random.randint(1990, 2000))

#         wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Month. Double-tap for more options']"))).click()
#         wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_month}']"))).click()
#         wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Day. Double-tap for more options']"))).click()
#         wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_day}']"))).click()
#         wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Year. Double-tap for more options']"))).click()
#         wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_year}']"))).click()

#         wait.until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(email)
#         wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' and @placeholder='Password']"))).send_keys(password)
#         # wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e='send-code-button']"))).click()

#         send_code_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-e2e='send-code-button']")))
#         driver.execute_script("arguments[0].scrollIntoView(true);", send_code_button)
#         time.sleep(1)  # slight wait after scroll
#         driver.execute_script("arguments[0].click();", send_code_button)
#         print("📤 Clicked 'Send Code' button.")


#         # print("📤 Sent verification code.")

#         sheet.append_row([email, password, time.strftime("%Y-%m-%d %H:%M:%S")])
#         print("📄 Credentials saved to Google Sheet.")

#         # --- Get Verification Code & Enter ---
#         code = read_tiktok_email()


#                 # 🕒 Wait until the code input field appears
#         try:
#             code_input = WebDriverWait(driver, 30).until(
#                 EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter 6-digit code']"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", code_input)
#             time.sleep(1)  # give it time to stabilize
#             code_input.send_keys(code)
#             print("✅ Entered verification code.")
#         except Exception as e:
#             print("❌ Failed to find or interact with the verification code input field.")
#             driver.save_screenshot("code_input_error.png")
#             raise e



#         # code_input = wait.until(EC.element_to_be_clickable((By.NAME, "email_verify_code")))
#         # code_input.send_keys(code)
#         # print("✅ Entered verification code.")

#         next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']")
# ))  
#         driver.execute_script("arguments[0].click();", next_button)
#         print("➡️ Clicked Next.")

#         input("Press Enter to quit browser...")

#     except Exception as e:
#         print("⚠️ Error:", e)
#         input("Press Enter to quit browser after error...")
#     finally:
#         driver.quit()
# def generate_valid_username():
#     while True:
#         username = ''.join(random.choices(string.ascii_lowercase, k=1)) + \
#                    ''.join(random.choices(string.ascii_lowercase + string.digits + "_.", k=random.randint(2, 6)))
#         if not username.isdigit():
#             return username

# try:
#     # Wait for username field to appear
#     username_input = WebDriverWait(driver, 30).until(
#         EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
#     )

#     # Generate a valid username
#     username = generate_valid_username()
#     username_input.send_keys(username)
#     print(f"📝 Entered username: {username}")

#     # Wait for sign up button to become enabled
#     signup_button_xpath = "//button[contains(text(), 'Sign up') and not(@disabled)]"
#     signup_button = WebDriverWait(driver, 30).until(
#         EC.element_to_be_clickable((By.XPATH, signup_button_xpath))
#     )

#     driver.execute_script("arguments[0].scrollIntoView(true);", signup_button)
#     time.sleep(1)
#     driver.execute_script("arguments[0].click();", signup_button)

#     print("✅ Clicked 'Sign up' button and completed flow.")

# except Exception as e:
#     print("❌ Failed to create username or click Sign up:", e)
#     driver.save_screenshot("username_signup_error.png")





# ------------------------ MAIN TIKTOK AUTOMATION ------------------------
def create_tiktok_account():
    email = generate_random_email()
    password = generate_random_password()

    print("Generated Email:", email)
    print("Generated Password:", password)

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
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
        print("📄 Credentials saved to Google Sheet.")

        # --- Get Verification Code & Enter ---
        code = read_tiktok_email()

        try:
            code_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter 6-digit code']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", code_input)
            time.sleep(1)
            code_input.send_keys(code)
            print("✅ Entered verification code.")
        except Exception as e:
            print("❌ Failed to find or interact with the verification code input field.")
            driver.save_screenshot("code_input_error.png")
            raise e

        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']")))
        driver.execute_script("arguments[0].click();", next_button)
        print("➡️ Clicked Next.")

        # --- Wait for Username Screen and Complete Signup ---
        def generate_valid_username():
            while True:
                base = ''.join(random.choices(string.ascii_lowercase, k=6))
                suffix = ''.join(random.choices(string.digits + "_.", k=4))
                username = base + suffix
                if not username.isdigit():
                    return username


        try:
            username_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
            )

            username = generate_valid_username()
            username_input.send_keys(username)
            print(f"📝 Entered username: {username}")

            signup_button_xpath = "//button[contains(text(), 'Sign up') and not(@disabled)]"
            signup_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, signup_button_xpath))
            )

            driver.execute_script("arguments[0].scrollIntoView(true);", signup_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", signup_button)

            print("✅ Clicked 'Sign up' button and completed flow.")

        except Exception as e:
            print("❌ Failed to create username or click Sign up:", e)
            driver.save_screenshot("username_signup_error.png")

        input("Press Enter to quit browser...")

    except Exception as e:
        print("⚠️ Error:", e)
        input("Press Enter to quit browser after error...")
    finally:
        driver.quit()




# ------------------------ RUN ------------------------
if __name__ == "__main__":
    create_tiktok_account()



