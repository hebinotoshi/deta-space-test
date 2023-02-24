from deta import app
# use app.lib.cron decorator for the function that runs on the schedule
# the function takes an `event` as an argument
import gspread
import requests
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials

def scrape_and_go():
    # Authenticate to Google Sheets
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
    client = gspread.authorize(credentials)
    # Open the Google Sheet
    sheet = client.open("titans_beers").sheet1
    def clear_sheet_data():
        # Get the number of existing rows in the sheet
        existing_rows = sheet.row_count + 1
        # Get the number of rows in the sheet, excluding the header row
        num_rows = len(sheet.get_all_values()) - 1
        # Clear all the data in the sheet, except for the header row
        if num_rows > 0:
            sheet.delete_rows(2, num_rows)
            sheet.delete_rows(2, num_rows)
    # Scrape the beer info from the page
    url = "https://untappd.com/v/titans-craft-beer-bar-and-bottle-shop/5286704"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    beers = soup.select(".menu-section-list li")
    # Call the clear_sheet_data function to clear all data in the sheet except for the header row
    clear_sheet_data()

    # Write the beer info to the Google Sheet, starting from row 2
    for beer in beers:
        name = beer.select_one(".track-click").text.strip()
        brewery = beer.find("h6").find("a").text.strip('\n')
        style = beer.find("h5").find("em").text.strip('\n')
        abv = beer.find("h6").find("span").text.split("\n", 1)[0]

        image_url = beer.find("div", class_="beer-label").find("img")["src"]
        data_rating = beer.find("div", class_="caps small").get("data-rating")
        rounded_rating=round((float(data_rating)),2)
        check_in = "https://untappd.com/" + beer.select_one(".track-click")["href"]
        print(check_in)

        beer_info = {
            "name": name,
            "brewery": brewery,
            "style": style,
            "abv": abv,
            "label" :image_url,
            "rating" : rounded_rating,
            "check_in": check_in
        }
        print(beer_info)
        sheet.append_row(list(beer_info.values()), value_input_option='RAW')




@app.lib.run()
@app.lib.cron()
def cron_task(event):
    return scrape_and_go()
    # print("running on a schedule") 