import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def clean_text(text):
    """Clean the text by removing \r and \n characters."""
    return text.replace('\r', ' ').replace('\n', ' ').strip()


def scrape_page(url):
    """Scrape a single page and return data as a list of dictionaries."""

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

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
        href = "https://nuforc.org/" + link["href"] + " " if link else ""

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


def get_page_urls(base_url):
    """Get URLs of all pages."""
    page_urls = [base_url]

    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all pagination buttons
    pagination_buttons = soup.find_all('a', class_='paginate_button')

    # Extract the highest page number
    max_page = 1
    for button in pagination_buttons:
        try:
            page_num = int(button.text)
            if page_num > max_page:
                max_page = page_num
        except ValueError:
            continue

    # Generate URLs for all pages
    for page in range(2, max_page + 1):
        page_url = f"{base_url}&page={page}"
        page_urls.append(page_url)

    return page_urls


def main():
    base_url = 'https://nuforc.org/subndx/?id=highlights'
    page_urls = get_page_urls(base_url)

    all_data = []
    for url in page_urls:
        print(f"Scraping {url}")
        page_data = scrape_page(url)
        all_data.extend(page_data)

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
    df.to_csv('nuforc_data_all_pages.csv', index=False)
    print("Data saved to nuforc_data_all_pages.csv")


if __name__ == "__main__":
    main()
