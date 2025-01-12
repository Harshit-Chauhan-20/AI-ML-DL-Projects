import requests
from bs4 import BeautifulSoup
from io import StringIO
from html.parser import HTMLParser
import pandas as pd


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


headers = ({'User-Agent':
                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})

n_pages = 0

# Initialise a new dataframe
df = pd.DataFrame(columns=['propertyName',
                           'pricing',
                           'tenure',
                           'propertyType',
                           'propertySQFT',
                           'furnishStatus',
                           'numBedroom',
                           'numBathroom'])

# Scrap a total of 1.5k pages
for page in range(0, 1500):
    n_pages += 1
    url = "https://www.propsocial.my/buy/kuala-lumpur-33?page=" + str(n_pages)

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    house_containers = soup.find_all('div', class_="classified-ad-details")

    if len(house_containers) != 0:
        for house in house_containers:
            if len(house.find_all('div')) >= 13:  # Check if each card is a property card (some are just advertisement)
                propertyName = (strip_tags(str(house.find_all('h3')[0]))).strip()
                pricing = (strip_tags(str(house.find_all('div', class_='pricing')[0]))).strip().replace('For Sale: RM ', '').replace(',', '')
                tenure = (strip_tags(str(house.find_all('div')[3]))).strip()
                propertyType = (strip_tags(str(house.find_all('div')[5]))).strip()
                propertySQFT = (strip_tags(str(house.find_all('div')[7]))).strip().replace(' SQ. FT', '').replace(',', '')
                furnishStatus = (strip_tags(str(house.find_all('div')[9]))).strip()
                numBedroom = (strip_tags(str(house.find_all('div')[11]))).strip().replace(' Bedrooms', '')
                numBathroom = (strip_tags(str(house.find_all('div')[13]))).strip().replace(' Bathrooms', '')

                houseDetails = {'propertyName': propertyName,
                                'pricing': pricing,
                                'tenure': tenure,
                                'propertyType': propertyType,
                                'propertySQFT': propertySQFT,
                                'furnishStatus': furnishStatus,
                                'numBedroom': numBedroom,
                                'numBathroom': numBathroom}

                df = df.append(houseDetails, ignore_index=True)

df.to_csv('../data/propsocial_kl.csv', encoding='utf-8', index=False)
