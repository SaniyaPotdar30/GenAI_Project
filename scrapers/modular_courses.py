from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scrape_modular_courses_page(driver, url):
    """
    Scrapes modular courses from Sunbeam's modular courses page.
    
    Args:
        driver: Selenium WebDriver instance
        url: URL of the modular courses page
    
    Returns:
        List of dictionaries containing course information
    """
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        
        # Wait for course container
        container = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.row.modular_courses_home_wrap")
            )
        )
        
        # Small delay to ensure all content is loaded
        time.sleep(1)
        
        # Get all course cards
        course_cards = container.find_elements(By.CSS_SELECTOR, ":scope > div")
        
        courses = []
        
        for idx, card in enumerate(course_cards, 1):
            try:
                # Extract title
                try:
                    title = card.find_element(By.TAG_NAME, "h4").text.strip()
                except:
                    title = "N/A"
                
                # Extract duration and clean it
                try:
                    duration_elem = card.find_element(By.XPATH, ".//*[contains(text(),'Duration')]")
                    duration = duration_elem.text.strip()
                    # Clean up duration text
                    duration = duration.replace("Duration :", "").replace("Duration:", "").strip()
                    duration = duration.replace("..", ".").strip()
                except:
                    duration = "N/A"
                
                # Extract link
                try:
                    link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                except:
                    link = "N/A"
                
                # Only add if we have at least a title
                if title != "N/A":
                    courses.append({
                        "course_name": title,
                        "duration": duration,
                        "link": link
                    })
                    
                    print(f"[{idx}] {title} - {duration}")
                
            except Exception as e:
                print(f"Error processing course card {idx}: {e}")
                continue
        
        print(f"\n✓ Successfully scraped {len(courses)} courses")
        return courses
        
    except Exception as e:
        print(f"Error in scrape_modular_courses_page: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Create driver (passed as parameter - following your project pattern)
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "https://www.sunbeaminfo.in/modular-courses-home"
        print(f"Scraping: {url}\n")
        
        courses = scrape_modular_courses_page(driver, url)
        
        # Display results
        print("\n" + "="*60)
        print("SCRAPED COURSES:")
        print("="*60)
        for idx, course in enumerate(courses, 1):
            print(f"\n{idx}. {course['course_name']}")
            print(f"   Duration: {course['duration']}")
            print(f"   Link: {course['link']}")
        
        # Save to JSON
        import json
        with open('modular_courses_data.json', 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Data saved to 'modular_courses_data.json'")
        
    finally:
        driver.quit()