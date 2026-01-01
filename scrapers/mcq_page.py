from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scrape_course_basic_info(driver, wait):
    """
    Scrapes the basic course information (name, schedule, duration, fees, etc.)
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        Dictionary with basic course information
    """
    basic_info = {}
    
    try:
        # Try to find the course info section
        # This could be in a table, div, or other container
        
        # Method 1: Look for text patterns
        body = driver.find_element(By.TAG_NAME, "body")
        body_text = body.text
        
        # Extract information using text patterns
        lines = body_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if 'Course Name' in line and ':' in line:
                basic_info['course_name'] = line.split(':', 1)[1].strip()
            
            elif 'Batch Schedule' in line and ':' in line:
                basic_info['batch_schedule'] = line.split(':', 1)[1].strip()
            
            elif 'Schedule' in line and ':' in line and 'Batch' not in line:
                basic_info['schedule'] = line.split(':', 1)[1].strip()
            
            elif 'Duration' in line and ':' in line:
                basic_info['duration'] = line.split(':', 1)[1].strip()
            
            elif 'Timings' in line and ':' in line:
                basic_info['timings'] = line.split(':', 1)[1].strip()
            
            elif 'Fees' in line and ':' in line:
                basic_info['fees'] = line.split(':', 1)[1].strip()
        
        # Method 2: Try to find specific elements (if structured in HTML)
        try:
            # Look for table or structured content
            tables = driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        key = cells[0].text.strip().replace(':', '').strip()
                        value = cells[1].text.strip()
                        
                        if 'Course Name' in key:
                            basic_info['course_name'] = value
                        elif 'Batch Schedule' in key:
                            basic_info['batch_schedule'] = value
                        elif 'Schedule' in key and 'Batch' not in key:
                            basic_info['schedule'] = value
                        elif 'Duration' in key:
                            basic_info['duration'] = value
                        elif 'Timings' in key or 'Time' in key:
                            basic_info['timings'] = value
                        elif 'Fees' in key or 'Fee' in key:
                            basic_info['fees'] = value
        except:
            pass
        
        return basic_info
        
    except Exception as e:
        print(f"  Error extracting basic info: {e}")
        return basic_info


def scrape_accordion(driver, wait):
    """
    Reusable function to scrape accordion content from any page.
    Clicks each accordion header and extracts content.
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
    
    Returns:
        List of dictionaries with accordion titles and content
    """
    accordion_data = []
    
    try:
        # Find all accordion headers
        headers = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".panel-title a"))
        )
        
        print(f"  Found {len(headers)} accordion sections\n")
        
        for idx, header in enumerate(headers, 1):
            try:
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", header)
                time.sleep(0.3)
                
                # Get title
                title = header.text.strip()
                
                # Click to open
                header.click()
                time.sleep(0.5)
                
                # Get content from opened panel
                panel = wait.until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, ".panel-collapse.in .panel-body")
                    )
                )
                content = panel.text.strip()
                
                accordion_data.append({
                    "title": title,
                    "content": content
                })
                
                # Print the section
                print(f"    [{idx}] {title}")
                print(f"        {content}\n")
                
            except Exception as e:
                print(f"    Error on accordion {idx}: {e}")
                continue
        
        return accordion_data
        
    except Exception as e:
        print(f"  No accordions found or error: {e}")
        return []


def scrape_mastering_mcqs_page(driver, url):
    """
    Scrapes the Mastering MCQs course page.
    
    Args:
        driver: Selenium WebDriver instance
        url: URL of the Mastering MCQs page
    
    Returns:
        Dictionary with course data
    """
    wait = WebDriverWait(driver, 15)
    
    try:
        print(f"{'='*60}")
        print(f"Scraping: Mastering MCQs")
        print(f"URL: {url}")
        print(f"{'='*60}\n")
        
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        
        # Get page title
        page_title = driver.title
        print(f"Page Title: {page_title}\n")
        
        # Scrape basic course information
        print("Extracting basic course information...")
        basic_info = scrape_course_basic_info(driver, wait)
        
        if basic_info:
            print(f"{'='*60}")
            print("COURSE BASIC INFORMATION:")
            print(f"{'='*60}")
            for key, value in basic_info.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            print(f"{'='*60}\n")
        
        # Scrape accordion content
        print("Extracting accordion sections...")
        accordion_data = scrape_accordion(driver, wait)
        
        print(f"{'='*60}")
        print(f"✓ Total sections scraped: {len(accordion_data)}")
        print(f"{'='*60}\n")
        
        return {
            "course_name": basic_info.get('course_name', 'Mastering MCQs'),
            "page_title": page_title,
            "url": url,
            "basic_info": basic_info,
            "sections": accordion_data
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "course_name": "Mastering MCQs",
            "url": url,
            "error": str(e)
        }


if __name__ == "__main__":
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Create driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "https://www.sunbeaminfo.in/modular-courses.php?mdid=57"
        
        # Scrape the page
        course_data = scrape_mastering_mcqs_page(driver, url)
        
        # Save to JSON
        import json
        with open('mastering_mcqs_data.json', 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'#'*60}")
        print(f"SCRAPING COMPLETE!")
        print(f"{'#'*60}")
        print(f"✓ Course: {course_data['course_name']}")
        print(f"✓ Basic info fields: {len(course_data.get('basic_info', {}))}")
        print(f"✓ Sections scraped: {len(course_data.get('sections', []))}")
        print(f"✓ Data saved to: mastering_mcqs_data.json")
        
    finally:
        driver.quit()