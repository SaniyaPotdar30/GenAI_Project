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
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print(f"\n(Content length: {len(content)} characters)\n")
                
            except Exception as e:
                print(f"Error processing accordion {idx + 1}: {e}")
                continue
                
    except Exception as e:
        print(f"Error in scrape_accordion_sections: {e}")
    
    return accordion_data


def scrape_all_tables(driver, wait):
    """
    Scrapes all tables and returns them with proper identification.
    """
    all_tables_data = []
    
    try:
        # Wait a bit for all tables to load
        time.sleep(1)
        tables = driver.find_elements(By.TAG_NAME, "table")
        
        print(f"\n{'='*60}")
        print(f"TOTAL TABLES FOUND: {len(tables)}")
        print(f"{'='*60}\n")
        
        for table_idx, table in enumerate(tables):
            try:
                # Scroll to table
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", table)
                time.sleep(0.3)
                
                # Try to get headers
                headers = table.find_elements(By.TAG_NAME, "th")
                header_names = [h.text.strip() for h in headers if h.text.strip()]
                
                # If no th tags, try first row as headers
                if not header_names:
                    first_row = table.find_elements(By.TAG_NAME, "tr")[0] if table.find_elements(By.TAG_NAME, "tr") else None
                    if first_row:
                        cells = first_row.find_elements(By.TAG_NAME, "td")
                        if cells:
                            header_names = [c.text.strip() for c in cells if c.text.strip()]
                
                if not header_names:
                    print(f"Table {table_idx + 1}: No headers found, skipping...")
                    continue
                
                print(f"{'='*60}")
                print(f"TABLE {table_idx + 1}")
                print(f"{'='*60}")
                print(f"Headers: {' | '.join(header_names)}")
                print(f"{'='*60}\n")
                
                # Get all rows (skip first row if it was header)
                rows = table.find_elements(By.TAG_NAME, "tr")
                start_idx = 1 if table.find_elements(By.TAG_NAME, "th") else 1
                
                table_data = []
                for row_idx, row in enumerate(rows[start_idx:], 1):
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 0:
                        row_dict = {}
                        row_values = []
                        
                        for idx, cell in enumerate(cells):
                            cell_text = cell.text.strip()
                            if idx < len(header_names):
                                row_dict[header_names[idx]] = cell_text
                                row_values.append(cell_text[:30] + "..." if len(cell_text) > 30 else cell_text)
                        
                        if row_dict:
                            table_data.append(row_dict)
                            print(f"Row {row_idx}: {' | '.join(row_values)}")
                
                print(f"\n{'='*60}")
                print(f"TOTAL ROWS: {len(table_data)}")
                print(f"{'='*60}\n")
                
                # Store table with metadata
                all_tables_data.append({
                    "table_index": table_idx,
                    "headers": header_names,
                    "data": table_data,
                    "row_count": len(table_data)
                })
                
            except Exception as e:
                print(f"Error processing table {table_idx + 1}: {e}")
                continue
        
        return all_tables_data
        
    except Exception as e:
        print(f"Error in scrape_all_tables: {e}")
        return []


def identify_tables(all_tables):
    """
    Identify which table is which based on headers.
    """
    programs_table = None
    batches_table = None
    
    for table in all_tables:
        headers = table['headers']
        
        # Check if it's the Available Programs table
        if any(h in ['Technology', 'Aim', 'Prerequisite', 'Learning', 'Location'] for h in headers):
            programs_table = table
            print(f"✓ Identified TABLE {table['table_index'] + 1} as: AVAILABLE INTERNSHIP PROGRAMS")
        
        # Check if it's the Batch Schedule table
        elif any(h in ['Batch', 'Start Date', 'End Date', 'Fees (Rs.)'] for h in headers):
            batches_table = table
            print(f"✓ Identified TABLE {table['table_index'] + 1} as: INTERNSHIP BATCHES SCHEDULE")
    
    return programs_table, batches_table


def get_main_description(driver):
    """
    Extracts the main description/introduction text from the page.
    """
    try:
        # Get paragraphs that come after h5 heading
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "h5 ~ p")
        desc_text = []
        
        for p in paragraphs[:4]:  # Get first 4 paragraphs
            text = p.text.strip()
            if text:
                desc_text.append(text)
        
        main_desc = "\n\n".join(desc_text)
        
        if main_desc:
            print(f"{'='*60}")
            print("MAIN DESCRIPTION")
            print(f"{'='*60}")
            print(main_desc)
            print(f"\n(Description length: {len(main_desc)} characters)")
            print(f"{'='*60}\n")
        
        return main_desc
        
    except Exception as e:
        print(f"Error getting main description: {e}")
        return ""


def scrape_internship_page():
    """
    Main function to scrape the complete internship page.
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
        print("STARTING INTERNSHIP PAGE SCRAPING")
        print(f"{'#'*60}\n")
        
        driver.get("https://sunbeaminfo.in/internship")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)
        
        print(f"Page Title: {driver.title}\n")

        # 1. Get main description
        print("\n" + "="*60)
        print("STEP 1: SCRAPING MAIN DESCRIPTION")
        print("="*60)
        main_desc = get_main_description(driver)

        # 2. Get accordion sections
        print("\n" + "="*60)
        print("STEP 2: SCRAPING ACCORDION SECTIONS")
        print("="*60)
        accordion_sections = scrape_accordion_sections(driver, wait)

        # 3. Scrape ALL tables
        print("\n" + "="*60)
        print("STEP 3: SCRAPING ALL TABLES")
        print("="*60)
        all_tables = scrape_all_tables(driver, wait)
        
        # 4. Identify which table is which
        print("\n" + "="*60)
        print("STEP 4: IDENTIFYING TABLES")
        print("="*60)
        programs_table, batches_table = identify_tables(all_tables)

        # Final Summary
        print("\n" + "#"*60)
        print("SCRAPING COMPLETE - FINAL SUMMARY")
        print("#"*60)
        print(f"✓ Main Description: {'YES' if main_desc else 'NO'}")
        print(f"✓ Accordion Sections: {len(accordion_sections)}")
        print(f"✓ Available Programs: {len(programs_table['data']) if programs_table else 0}")
        print(f"✓ Batch Schedule: {len(batches_table['data']) if batches_table else 0}")
        print("#"*60 + "\n")

        driver.quit()
        
        return {
            "main_description": main_desc,
            "accordion_sections": accordion_sections,
            "programs": programs_table['data'] if programs_table else [],
            "batches": batches_table['data'] if batches_table else []
        }

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        driver.quit()
        return None


if __name__ == "__main__":
    data = scrape_internship_page()
    
    if data:
        print("\n" + "="*60)
        print("DATA SUCCESSFULLY SCRAPED!")
        print("="*60)
        
        # Optional: Save to JSON
        import json
        with open('internship_complete_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✓ Data saved to 'internship_complete_data.json'")