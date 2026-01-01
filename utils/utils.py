from selenium.webdriver.common.by import By

def scrape_accordion(driver, accordion_selector):
    """
    Generic accordion scraper.
    Returns list of {title, content}
    """
    data = []

    accordions = driver.find_elements(By.CSS_SELECTOR, accordion_selector)

    for acc in accordions:
        title = acc.find_element(By.TAG_NAME, "h3").text
        content = acc.text.replace(title, "").strip()

        data.append({
            "title": title.strip(),
            "content": content.strip()
        })

    return data 

def scrape_table_to_dictionary(driver, table_selector):
    """
    Converts HTML table to list of dictionaries
    """
    table = driver.find_element(By.CSS_SELECTOR, table_selector)
    rows = table.find_elements(By.TAG_NAME, "tr")

    headers = [th.text for th in rows[0].find_elements(By.TAG_NAME, "th")]
    table_data = []

    for row in rows[1:]:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_dict = dict(zip(headers, [cell.text for cell in cells]))
        table_data.append(row_dict)

    return table_data   
