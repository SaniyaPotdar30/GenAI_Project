from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time

chrome_options = Options()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(options=chrome_options)

url = "https://www.sunbeaminfo.in/contact-us"
print(f"Scraping: {url}")
driver.get(url)
time.sleep(3)

page_text = driver.find_element(By.TAG_NAME, 'body').text

import re
emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)))
phones = list(set(re.findall(r'[\+\d][\d\-\(\)\s]{8,}[\d]', page_text)))

contact_data = {
    "page_title": "Contact Us",
    "url": url,
    "full_text": page_text,
    "emails": emails,
    "phones": phones
}

driver.quit()

with open('contact_data.json', 'w', encoding='utf-8') as f:
    json.dump(contact_data, f, indent=2, ensure_ascii=False)

print(f"✓ Emails: {emails}")
print(f"✓ Phones: {phones[:3]}")
print("✓ Saved to contact_data.json")