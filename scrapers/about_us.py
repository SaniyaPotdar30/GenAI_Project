from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time


def get_main_description(driver):
    """
    Extracts the main description paragraphs from the page.
    Simple approach: Get all paragraphs, filter based on content.
    """
    try:
        # Wait a bit for page to fully load
        time.sleep(1)
        
        # Find all paragraphs on the page
        all_paragraphs = driver.find_elements(By.TAG_NAME, "p")
        
        main_paragraphs = []
        
        for p in all_paragraphs:
            text = p.text.strip()
            
            # Only add paragraphs that:
            # 1. Have substantial text (> 100 chars)
            # 2. Start with specific keywords we know are in the main description
            if len(text) > 100:
                # Check if it's one of the main description paragraphs
                if any(keyword in text for keyword in [
                    "At Sunbeam we believe",
                    "In this scenario",
                    "Sunbeam's proven track record",
                    "Sunbeam Group's expertise"
                ]):
                    main_paragraphs.append(text)
        
        main_desc = "\n\n".join(main_paragraphs)
        
        if main_desc:
            print(f"{'='*60}")
            print("MAIN DESCRIPTION")
            print(f"{'='*60}")
            print(main_desc)
            print(f"\n(Total length: {len(main_desc)} characters)")
            print(f"{'='*60}\n")
        else:
            print("No main description found.")
        
        return main_desc
        
    except Exception as e:
        print(f"Error getting main description: {e}")
        return ""


def scrape_accordion_sections(driver, wait):
    """
    Scrapes accordion sections.
    """
    accordion_sections = []
    
    try:
        headers = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".panel-title a"))
        )
        
        print(f"Found {len(headers)} accordion section(s)\n")

        for idx in range(len(headers)):
            try:
                # Re-find headers to avoid stale element
                headers = driver.find_elements(By.CSS_SELECTOR, ".panel-title a")
                h = headers[idx]
                
                # Scroll to header
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", h)
                time.sleep(0.5)
                
                # Get title before clicking
                title = h.text.strip()
                
                # Click to open
                try:
                    h.click()
                except:
                    driver.execute_script("arguments[0].click();", h)
                
                time.sleep(0.5)

                # Wait for the opened panel body
                panel = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".panel-collapse.in .panel-body")
                    )
                )
                
                content = panel.text.strip()
                
                accordion_sections.append({
                    "title": title,
                    "content": content
                })

                print(f"{'='*60}")
                print(f"[ACCORDION {idx + 1}] {title}")
                print(f"{'='*60}")
                print(content)
                print(f"\n(Content length: {len(content)} characters)\n")
                
            except Exception as e:
                print(f"Error on section {idx + 1}: {e}")
                continue
        
        return accordion_sections
                
    except Exception as e:
        print(f"Error in scrape_accordion_sections: {e}")
        return []


def scrape_aboutus_page(driver, url):
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(url)
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)  # Wait for full page load
        
        page_title = driver.title
        print(f"{'#'*60}")
        print("STARTING ABOUT US PAGE SCRAPING")
        print(f"{'#'*60}\n")
        print("Page Title:", page_title)

        # 1. Get main description
        print("\n" + "="*60)
        print("STEP 1: SCRAPING MAIN DESCRIPTION")
        print("="*60)
        main_description = get_main_description(driver)

        # 2. Get accordion sections
        print("\n" + "="*60)
        print("STEP 2: SCRAPING ACCORDION SECTIONS")
        print("="*60)
        accordion_sections = scrape_accordion_sections(driver, wait)
        
        print("\n" + "#"*60)
        print("SCRAPING COMPLETE - FINAL SUMMARY")
        print("#"*60)
        print(f"✓ Main Description: {'YES' if main_description else 'NO'}")
        print(f"✓ Accordion Sections: {len(accordion_sections)}")
        for idx, section in enumerate(accordion_sections, 1):
            print(f"  {idx}. {section['title']}")
        print("#"*60 + "\n")
        
        return {
            "page_title": page_title,
            "url": url,
            "main_description": main_description,
            "accordion_sections": accordion_sections
        }

    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)

    try:
        url = "https://www.sunbeaminfo.in/about-us"
        data = scrape_aboutus_page(driver, url)
        
        if data:
            # Save to JSON
            with open('about_us_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("="*60)
            print("DATA SUCCESSFULLY SCRAPED!")
            print("="*60)
            print(f"✓ Data saved to 'about_us_data.json'")
            print(f"✓ Main description: {len(data.get('main_description', ''))} characters")
            print(f"✓ Total accordion sections: {len(data['accordion_sections'])}")
    
    finally:
        driver.quit()