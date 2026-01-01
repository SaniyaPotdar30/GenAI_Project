from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scrape_accordion_sections(driver, wait):
    """
    Scrapes all accordion sections from the page.
    Returns list of dictionaries with title and content.
    """
    accordion_data = []
    
    try:
        headers = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".panel-title a"))
        )
        
        print(f"\n{'='*60}")
        print(f"FOUND {len(headers)} ACCORDION SECTIONS")
        print(f"{'='*60}\n")
        
        for idx in range(len(headers)):
            try:
                # Re-find headers to avoid stale element
                headers = driver.find_elements(By.CSS_SELECTOR, ".panel-title a")
                header = headers[idx]
                
                # Scroll to header
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", header)
                time.sleep(0.5)
                
                # Get title
                title = header.text.strip()
                
                # Click using JavaScript to avoid interception
                try:
                    header.click()
                except:
                    driver.execute_script("arguments[0].click();", header)
                
                time.sleep(0.5)
                
                # Get panel body content
                panel_body = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".panel-collapse.in .panel-body")
                    )
                )
                
                content = panel_body.text.strip()
                
                if title and content:
                    accordion_data.append({
                        "title": title,
                        "content": content
                    })
                    
                    print(f"{'='*60}")
                    print(f"[ACCORDION {idx + 1}] {title}")
                    print(f"{'='*60}")
                    print(content)
                    print(f"\n(Content length: {len(content)} characters)\n")
                
            except Exception as e:
                print(f"Error processing accordion {idx + 1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error in scrape_accordion_sections: {e}")
    
    return accordion_data


def scrape_precat_page():
    """
    Main function to scrape the Pre-CAT course page.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        print(f"\n{'#'*60}")
        print("STARTING PRE-CAT PAGE SCRAPING")
        print(f"{'#'*60}\n")
        
        driver.get("https://www.sunbeaminfo.in/pre-cat")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        
        # Get page title BEFORE closing driver
        page_title = driver.title
        print(f"Page Title: {page_title}\n")

        # Get accordion sections (which includes the batch schedule)
        print("\n" + "="*60)
        print("SCRAPING ACCORDION SECTIONS")
        print("="*60)
        accordion_sections = scrape_accordion_sections(driver, wait)

        # Close driver
        driver.quit()

        # Final Summary
        print("\n" + "#"*60)
        print("SCRAPING COMPLETE - FINAL SUMMARY")
        print("#"*60)
        print(f"✓ Page Title: {page_title}")
        print(f"✓ Accordion Sections: {len(accordion_sections)}")
        for idx, section in enumerate(accordion_sections, 1):
            print(f"  {idx}. {section['title']}")
        print("#"*60 + "\n")
        
        return {
            "page_title": page_title,
            "accordion_sections": accordion_sections
        }

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        driver.quit()
        return None


if __name__ == "__main__":
    data = scrape_precat_page()
    
    if data:
        print("="*60)
        print("DATA SUCCESSFULLY SCRAPED!")
        print("="*60)
        
        # Optional: Save to JSON
        import json
        with open('precat_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✓ Data saved to 'precat_data.json'")
