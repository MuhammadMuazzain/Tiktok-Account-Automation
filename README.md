# TikTok Account Automation  
Automated TikTok Account Creator (Selenium + Undetected-Chrome)

This repository contains a full automation script that creates TikTok personal accounts using:
- **Selenium WebDriver**
- **Undetected-Chromedriver (uc)**
- **Mobile device emulation**
- **Human-like typing simulation**
- **Randomized username & password generation**
- **Automatic email verification using IMAP**
- **Google Sheets logging of created accounts**

This project demonstrates how to safely perform TikTok onboarding flows programmatically while minimizing detection risks.

---

## 🚀 Features

### ✔️ Mobile Device Simulation  
Uses a Pixel-5 mobile user-agent + device metrics to appear as a real mobile device.

### ✔️ Human-Like Interaction  
- Random typing delays  
- Random cursor movements  
- Randomized birthdate, username, and password generation  
- Click events triggered using JS for lower detection

### ✔️ Complete Email Verification Automation  
- Connects to IMAP inbox  
- Detects TikTok verification emails  
- Extracts the 6-digit OTP automatically  
- Inputs the OTP into TikTok signup form

### ✔️ Google Sheets Integration  
Each created account is stored in a Google Sheet:

