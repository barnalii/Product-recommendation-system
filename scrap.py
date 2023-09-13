import urllib.request
import pandas as pd
from bs4 import BeautifulSoup
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"


def flipkart_scrap(url):

    response = urllib.request.urlopen(url)
    html_content = response.read()
    soup = BeautifulSoup(html_content, "lxml")

    flipkart_name = soup.find_all("div", class_="_4rR01T")
    flipkart_price = soup.find_all("div", class_="_30jeq3 _1_WHN1")
    flipkart_rating = soup.find_all("div", class_="_3LWZlK")
    flipkart_images = soup.find_all("img", class_="_396cs4")
    flipkart_links = soup.find_all("a", class_="_1fQZEK")

  

    items = []

    for i in range(len(flipkart_name)):
        item = {
            "Name": flipkart_name[i].text,
            "Price": flipkart_price[i].text,
            "Review": flipkart_rating[i].text,
            "ImageURL": flipkart_images[i]['src'] if i < len(flipkart_images) else None,
            "ProductURL": "https://www.flipkart.com" + flipkart_links[i]['href'] if i < len(flipkart_links) else None,
            
        }
        items.append(item)

    return items


def amazon_scrap(url):
    headers = {
        'User-Agent': user_agent,
    }
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    html_content = response.read().decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    product_containers = soup.find_all(
        "div", class_="sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")

    data = []

    for container in product_containers:
        amazon_name = container.find(
            "span", class_="a-size-medium a-color-base a-text-normal")
        amazon_price = container.find("span", class_="a-price-whole")
        amazon_review = container.find("span", class_="a-icon-alt")
        amazon_image = container.find("img", class_="s-image")
        amazon_link = container.find("a", class_="a-link-normal")
        

        item = {
            "Name": amazon_name.get_text(strip=True) if amazon_name else "",
            "Price": amazon_price.get_text(strip=True) if amazon_price else "",
            "Review": amazon_review.get_text(strip=True) if amazon_review else "",
            "ImageURL": amazon_image['src'] if amazon_image else "",
             "ProductURL": "https://www.amazon.in" + amazon_link['href'] if amazon_link else "",
           
        }

        data.append(item)

    return data


def scrap_web(find_product):

    flipkart_url = f"https://www.flipkart.com/search?q={find_product}"

    flipkart_data = flipkart_scrap(flipkart_url)

    amazon_url = f"https://www.amazon.in/s?k={find_product}"

    amazon_data = amazon_scrap(amazon_url)

    merge_data = flipkart_data + amazon_data
    df = pd.DataFrame(merge_data)

    excel_file = "laptop.xlsx"
    df.to_excel(excel_file, index=False)

    df = pd.read_excel("laptop.xlsx")

    df['Price'] = pd.to_numeric(df['Price'].str.replace(
        '[^0-9.]', '', regex=True), errors='coerce')
    df['Review'] = pd.to_numeric(df['Review'].str.replace(
        '[^0-9.]', '', regex=True), errors='coerce')

    product_price = df['Price']
    max_price = df['Price'].max()
    min_price = df['Price'].min()
    df['Normalized Price'] = (
        max_price - product_price) / (max_price - min_price)

    product_review = df['Review']
    max_review = df['Review'].max()
    min_review = df['Review'].min()
    df['Normalized Review'] = (
        max_review - product_review) / (max_review - min_review)

    df[['Name', 'Normalized Price']].to_excel(
        "Normalized price.xlsx", index=False)
    df[['Name', 'Normalized Review']].to_excel(
        "Normalized review.xlsx", index=False)

    price_weight = 0.6
    review_weight = 0.4
    df['Normalization list'] = df['Normalized Price'] * \
        price_weight + df['Normalized Review'] * review_weight

    sorted_df = df.sort_values(by='Normalization list', ascending=False)

    sorted_df.to_excel("sorted_product.xlsx", index=False)
    print("Data written to 'sorted_product.xlsx'")