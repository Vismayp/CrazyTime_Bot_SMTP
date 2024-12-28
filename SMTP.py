from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import smtplib
from email.message import EmailMessage
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "Service is running", 200

def run_http_server():
    app.run(host="0.0.0.0", port=8080)

# Start the HTTP server in a separate thread
threading.Thread(target=run_http_server, daemon=True).start()
# SMTP configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "codebuzz4268@gmail.com"  # Replace with your Gmail address
EMAIL_PASSWORD = "qkzbydgwfzxdlraf"  # Replace with your Gmail app password

# Recipient email addresses
RECIPIENT_EMAILS = ["Ghousmohiuddinahmad@gmail.com"]  # Add your recipient emails

# Websites to monitor
WEBSITES = ["https://tracksino.com/crazytime", "https://tracksino.com/crazytime-a"]

# JavaScript paths to monitor
JS_PATH_RESULT = "#spin-history > tbody > tr:nth-child(1) > td:nth-child(3) > center > i"
JS_PATH_INSTANCE = "#spin-history > tbody > tr:nth-child(1) > td:nth-child(1)"

# Class names to check against
CLASS_NAME_MAPPING = {
    "ico-crazytime-cf": "CoinFlip",
    "ico-crazytime-ch": "CashHunt",
    "ico-crazytime-pa": "Pachinko",
    "ico-crazytime-ct": "CrazyTime"
}

# Store last instance per game to avoid duplicate messages
last_instances = {}

def send_email(subject, body):
    """Send an email to multiple recipients."""
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(RECIPIENT_EMAILS)  # Join all recipients into a single string
    msg["Subject"] = subject
    msg.set_content(body)

    # Send email to all recipients
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Start TLS encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email sent successfully to: {', '.join(RECIPIENT_EMAILS)}.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def monitor_website(url):
    """Monitor the given website and check for game results and instance changes."""
    driver.get(url)
    time.sleep(1)  # Allow time for the page to load
    
    try:
        # Get the game result
        result_element = driver.find_element(By.CSS_SELECTOR, JS_PATH_RESULT)
        class_name = result_element.get_attribute("class").strip()
        game_result = CLASS_NAME_MAPPING.get(class_name)  # Check if result is in CLASS_NAME_MAPPING
        game_name = "CrazyTimeA" if "crazytime-a" in url else "CrazyTime"
        instance_element = driver.find_element(By.CSS_SELECTOR, JS_PATH_INSTANCE)
        instance_value = instance_element.text.strip()
                
        if game_result and game_result!="Unknown":  # Only proceed if the result is valid
            # Get the instance value

            # Determine the game name
            
            unique_key = f"{game_name}:{url}"
            
            # Only proceed if the instance value is new
            if last_instances.get(unique_key) != instance_value:
                last_instances[unique_key] = instance_value
                subject = f"Game Alert: {game_name}"
                body = (
                    f"Game: {game_name},\n"
                    f"Spin Result: {game_result},\n"
                    f"Instance: {instance_value}\n"
                    f"URL: {url}"
                )
                send_email(subject, body)

                print(f"Website: {url}, Game: {game_name}, Result: {game_result}, Instance: {instance_value}")
        
    except Exception as e:
        print(f"Error monitoring {url}: {e}")

# Configure WebDriver for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    while True:
        for website in WEBSITES:
            monitor_website(website)
        time.sleep(1)  # Wait before checking again
finally:
    driver.quit()
