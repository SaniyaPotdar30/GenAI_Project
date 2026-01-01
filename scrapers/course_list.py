from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


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
                
                # Print full content (not truncated)
                print(f"    [{idx}] {title}")
                print(f"        {content}")
                print()
                
            except Exception as e:
                print(f"    Error on accordion {idx}: {e}")
                continue
        
        return accordion_data
        
    except Exception as e:
        print(f"  No accordions found or error: {e}")
        return []


def scrape_course_page(driver, url, course_name):
    """
    Scrapes a single course page.
    
    Args:
        driver: Selenium WebDriver instance
        url: Course page URL
        course_name: Name of the course
    
    Returns:
        Dictionary with course data
    """
    wait = WebDriverWait(driver, 15)
    
    try:
        print(f"\nScraping: {course_name}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        
        # Scrape accordion content
        accordion_data = scrape_accordion(driver, wait)
        
        print(f"  ✓ Scraped {len(accordion_data)} sections\n")
        
        return {
            "course_name": course_name,
            "url": url,
            "sections": accordion_data
        }
        
    except Exception as e:
        print(f"  Error: {e}")
        return {
            "course_name": course_name,
            "url": url,
            "error": str(e)
        }


def scrape_all_courses(driver):
    """
    Main function to scrape all modular courses.
    """
    # List of all course URLs
    course_links = [
        {
            "name": "Apache Spark Mastery - Data Engineering With PySpark",
            "url": "https://www.sunbeaminfo.in/modular-courses/apache-spark-mastery-data-engineering-pyspark"
        },
        {
            "name": "Aptitude",
            "url": "https://www.sunbeaminfo.in/modular-courses/aptitude-course-in-pune"
        },
        {
            "name": "C++",
            "url": "https://www.sunbeaminfo.in/modular-courses/cpp-classes"
        },
        {
            "name": "Core Java",
            "url": "https://www.sunbeaminfo.in/modular-courses/core-java-classes"
        },
        {
            "name": "Data Structures And Algorithms",
            "url": "https://www.sunbeaminfo.in/modular-courses/data-structure-algorithms-using-java"
        },
        {
            "name": "Dev Ops",
            "url": "https://www.sunbeaminfo.in/modular-courses/Devops-training-institute"
        },
        {
            "name": "Dream LLM",
            "url": "https://www.sunbeaminfo.in/modular-courses/dreamllm-training-institute-pune"
        },
        {
            "name": "Machine Learning",
            "url": "https://www.sunbeaminfo.in/modular-courses/machine-learning-classes"
        },
        {
            "name": "Mastering GenAI",
            "url": "https://www.sunbeaminfo.in/modular-courses/mastering-generative-ai"
        },
        {
            "name": "Mastering MCQs",
            "url": "https://www.sunbeaminfo.in/modular-courses.php?mdid=57"
        },
        {
            "name": "MERN (FULL-STACK) DEVELOPMENT",
            "url": "https://www.sunbeaminfo.in/modular-courses/mern-full-stack-developer-course"
        },
        {
            "name": "MLOps & LLMOps",
            "url": "https://www.sunbeaminfo.in/modular-courses/mlops-llmops-training-institute-pune"
        },
        {
            "name": "Python Development",
            "url": "https://www.sunbeaminfo.in/modular-courses/python-classes-in-pune"
        }
    ]
    
    all_courses = []
    
    print(f"{'#'*60}")
    print(f"SCRAPING {len(course_links)} MODULAR COURSES")
    print(f"{'#'*60}")
    
    for idx, course in enumerate(course_links, 1):
        print(f"\n[{idx}/{len(course_links)}]")
        
        course_data = scrape_course_page(driver, course["url"], course["name"])
        all_courses.append(course_data)
        
        # Small delay between requests
        time.sleep(0.5)
    
    return {
        "total_courses": len(all_courses),
        "courses": all_courses
    }


if __name__ == "__main__":
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Scrape all courses
        result = scrape_all_courses(driver)
        
        # Save to JSON
        import json
        with open('modular_courses_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'#'*60}")
        print(f"SCRAPING COMPLETE!")
        print(f"{'#'*60}")
        print(f"Total courses scraped: {result['total_courses']}")
        print(f"Data saved to: modular_courses_data.json")
        
    finally:
        driver.quit()