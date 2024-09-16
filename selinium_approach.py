from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time


def clean_text(text):
    """Clean the text by removing \r and \n characters."""
    return text.replace('\r', ' ').replace('\n', ' ').strip()


def scrape_page(driver):
    """Scrape the current page loaded in the Selenium driver."""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = []
    skip_first_row = True  # Flag to skip the first row

    for idx, row in enumerate(soup.find_all('tr')):
        cells = row.find_all('td')

        # Skip the first row
        if skip_first_row and idx == 0:
            continue

        # Ensure that we have enough cells
        num_cells = len(cells)

        # Extract data with default values for missing elements
        link = cells[0].find("a", href=True) if num_cells > 0 else None
        href = "https://nuforc.org/" + link["href"] if link else ""

        row_data = {
            'href': href,
            'Date': clean_text(cells[1].get_text(strip=True)) if num_cells > 1 else "",
            'City': clean_text(cells[2].get_text(strip=True)) if num_cells > 2 else "",
            'State': clean_text(cells[3].get_text(strip=True)) if num_cells > 3 else "",
            'Country': clean_text(cells[4].get_text(strip=True)) if num_cells > 4 else "",
            'Shape': clean_text(cells[5].get_text(strip=True)) if num_cells > 5 else "",
            'Summary': clean_text(cells[6].get_text(strip=True)) if num_cells > 6 else "",
            'Reported': clean_text(cells[7].get_text(strip=True)) if num_cells > 7 else "",
            'Media': clean_text(cells[8].get_text(strip=True)) if num_cells > 8 else "",
            'Explanation': clean_text(cells[9].get_text(strip=True)) if num_cells > 9 else ""
        }

        # Add the row to data
        data.append(row_data)

    return data


def main():
    url = 'https://nuforc.org/subndx/?id=highlights'

    # Set up the Selenium WebDriver (you'll need to download the appropriate driver for your browser)
    driver = webdriver.Chrome()  # Or webdriver.Firefox(), etc.
    driver.get(url)

    all_data = []
    page = 1

    try:
        while True:
            print(f"Scraping page {page}")

            # Wait for the table to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table")))

            # Scrape the current page
            page_data = scrape_page(driver)
            all_data.extend(page_data)

            # Try to click the "Next" button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "a.paginate_button.next"))
                )
                next_button.click()
                page += 1
                time.sleep(2)  # Wait for the page to load
            except (TimeoutException, NoSuchElementException):
                print("Reached the last page or couldn't find the 'Next' button.")
                break

    finally:
        driver.quit()

    # Convert to DataFrame
    df = pd.DataFrame(all_data)

    # Print column names to check what we actually have
    print("Columns in the DataFrame:", df.columns.tolist())

    # Replace empty strings with NaN for proper handling in DataFrame
    df.replace("", np.nan, inplace=True)

    # Check if 'Reported' column exists before trying to convert
    if 'Reported' in df.columns:
        df['Reported'] = pd.to_numeric(df['Reported'], errors='coerce')
    else:
        print("Warning: 'Reported' column not found in the DataFrame")

    # Save to CSV
    df.to_csv('nuforc_data_all_pages_selenium.csv', index=False)
    print("Data saved to nuforc_data_all_pages_selenium.csv")


if __name__ == "__main__":
    main()
