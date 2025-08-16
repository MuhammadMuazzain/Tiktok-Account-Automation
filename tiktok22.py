import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string


# 🔧 Google Sheets integration imports
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Setup Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 🔧 Open your Google Sheet (adjust names accordingly)
sheet = client.open("Link_to_python").worksheet("Sheet1")  # Change Sheet1 if needed

# 🔧 Generate random email
def generate_random_email(domain="Arksbaymarketing.com"):
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@{domain}"

# 🔧 Generate compliant password
def generate_random_password():
    letters = string.ascii_letters
    digits = string.digits
    special = "!@#$%^&*()-_=+"

    password = [
        random.choice(letters),
        random.choice(digits),
        random.choice(special)
    ]

    remaining_length = random.randint(5, 13)  # Ensure 8-20 total
    all_chars = letters + digits + special
    password += random.choices(all_chars, k=remaining_length)
    random.shuffle(password)

    return ''.join(password)

# ✅ Generate credentials
email = generate_random_email()
password = generate_random_password()

print("Generated Email:", email)
print("Generated Password:", password)

# 🔧 Setup undetected ChromeDriver
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# 🌐 Open TikTok signup email page directly
driver.get("https://www.tiktok.com/signup/phone-or-email/email")

try:
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    #### ✅ Select DOB using div-based dropdowns

    # 🔷 Month
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    selected_month = random.choice(months)

    month_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Month. Double-tap for more options']")))
    month_dropdown.click()
    month_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_month}']")))
    month_option.click()

    # 🔷 Day
    selected_day = str(random.randint(1, 28))
    day_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Day. Double-tap for more options']")))
    day_dropdown.click()
    day_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_day}']")))
    day_option.click()

    # 🔷 Year
    selected_year = str(random.randint(1990, 2000))
    year_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Year. Double-tap for more options']")))
    year_dropdown.click()
    year_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@role='option' and text()='{selected_year}']")))
    year_option.click()

    #### ✅ Input Email
    email_input = wait.until(EC.element_to_be_clickable((By.NAME, "email")))
    email_input.send_keys(email)
    # email_input.send_keys("maziright2345@gmail.com")
    print(f"Entered email: {email}")

    #### ✅ Input Password
    password_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' and @placeholder='Password']")))
    password_input.send_keys(password)
    print(f"Entered password.")

    #### ✅ Click "Send code" button using JS click for reliability
    send_code_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e='send-code-button']")))
    driver.execute_script("arguments[0].click();", send_code_button)
    print("Clicked 'Send code' button.")


    #### ✅ Save to Google Sheet only on successful send code click
    sheet.append_row([email, password, time.strftime("%Y-%m-%d %H:%M:%S")])
    print("Credentials saved to Google Sheet.")

    # 🕒 Hold browser for observation
    input("Press Enter to quit browser...")

except Exception as e:
    print("Error occurred:", e)
    input("Press Enter to quit browser after error...")

finally:
    driver.quit()
