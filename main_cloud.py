import csv
import datetime
import json
import time
import urllib
import undetected_chromedriver as uc
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, \
    NoSuchElementException

import requests
from selenium.webdriver.common.keys import Keys
import pandas as pd
import random
import os
from VirtualDispalyCodeAndTranslate import SmartDisplayWithTranslate

# zip codes required - 30305, 28202, 33139, 33647, 34786


PROXIES = [
    'u5.p.webshare.io:10004',
    'u6.p.webshare.io:10006',
    'u5.p.webshare.io:10018',
    'u5.p.webshare.io:10023',
    'u4.p.webshare.io:10032',
    'u5.p.webshare.io:10034',
    'u5.p.webshare.io:10035',
    'u6.p.webshare.io:10002',
    'u6.p.webshare.io:10008',
    'u6.p.webshare.io:10009'
]


class Instacart:
    def __init__(self):
        self.SCROLL_LIMIT = 15
        self.searchterm = None
        self.current_url = ""
        self.products = []
        self.links = []
        # self.zip = input("ZIP Code: ")
        # self.GetLocationsFromZip()
        # self.Location = input("Select from above locations: ")
        # self.Address = input("Type Address: ")
        # self.GetAddressesFromLocation()
        # self.Area = input("Select from above areas: ")

        self.zip = "30305"
        self.GetLocationsFromZip()
        self.Location = "Atlanta, GA"
        self.Address = "3180 Peachtree Road"
        self.GetAddressesFromLocation()
        self.Area = "3180 Peachtree Road"

        self.zip = "33612"
        self.GetLocationsFromZip()
        self.Location = "Tampa. FL"
        self.Address = "2200 E Fowler Ave, Tampa, FL 33612, United States"
        self.GetAddressesFromLocation()
        self.Area = "2200 East Fowler Avenue"

        self.zip = "28208"
        self.GetLocationsFromZip()
        self.Location = "Charlotte, NC"
        self.Address = "1201 W 4th Street Ext, Charlotte, NC 28208"
        self.GetAddressesFromLocation()
        self.Area = "1201 W 4th St"

        self.zip = "33139"
        self.GetLocationsFromZip()
        self.Location = "Miami Beach, FL"
        self.Address = "Ocean Dr, Miami Beach, FL 33139"
        self.GetAddressesFromLocation()
        self.Area = "Ocean Drive"

        self.zip = "34786"
        self.GetLocationsFromZip()
        self.Location = "Windermere, FL"
        self.Address = "11465 Park Ave, Windermere, FL 34786, United States"
        self.GetAddressesFromLocation()
        self.Area = "11465 Park Avenue"

        print("For ZIP {} you selected {} location with {} address at {} area".format(self.zip, self.Location,
                                                                                      self.Address, self.Area))
        self.LoopTargets()

    def GetLocationsFromZip(self):
        q1 = {"query": str(self.zip), "coordinates": None}
        q1 = self.convert_obj_to_var(q1)
        q2 = {"persistedQuery": {"version": 1,
                                 "sha256Hash": "f720dae8b46e5d5cb6bd351762296829f4c6efbfc2d19b96c64021f75424e747"}}
        q2 = self.convert_obj_to_var(q2)

        req = requests.get(
            "https://www.instacart.com/graphql?operationName=AutoCompleteLocations&variables={}&extensions={}".format(
                q1, q2)).json()

        locations = req['data']['autocompleteLocations']['locations']

        for location in locations:
            print(location['viewSection']['lineTwoString'])

    def GetAddressesFromLocation(self):
        q1 = {"query": self.Address, "coordinates": None}
        q1 = self.convert_obj_to_var(q1)
        q2 = {"persistedQuery": {"version": 1,
                                 "sha256Hash": "f720dae8b46e5d5cb6bd351762296829f4c6efbfc2d19b96c64021f75424e747"}}
        q2 = self.convert_obj_to_var(q2)
        req = requests.get(
            "https://www.instacart.com/graphql?operationName=AutoCompleteLocations&variables={}&extensions={}".format(
                q1, q2)).json()

        locations = req['data']['autocompleteLocations']['locations']
        for location in locations:
            print(location['streetAddress'], location['postalCode'], location['viewSection']['lineOneString'],
                  location['viewSection']['lineTwoString'])

    def convert_obj_to_var(self, q):
        j = json.dumps(q)
        return urllib.parse.quote_plus(j)

    def LoopTargets(self):

        with open('targets_searchterm.txt', 'r') as f:
            links = [line.strip() for line in f]
        f.close()

        links = list(filter(None, links))
        for link in links:
            self.searchterm = link
            if "https://www.instacart.com/" in link:
                self.current_url = link
            else:
                self.current_url = "https://www.instacart.com/store/publix/search/" + link
            print(self.current_url)

            try:
                self.GetHomeProducts()
            except Exception as e:
                print("ERROR: ", e)
                break

    def GetHomeProducts(self):
        try:
            opts = uc.ChromeOptions()
            proxy = random.choice(PROXIES)
            opts.add_argument(f'--proxy-server=socks5://{proxy}')
            self.driver = uc.Chrome(
                browser_executable_path="/usr/bin/google-chrome",
                options=opts,
                # version_main=95,
                # patcher_force_close=True
            )
            self.driver.maximize_window()

            print("Home products")
            self.driver.get("https://www.instacart.com/store/publix/storefront")
            # //*[@class="css-1tpfu6x-Logo"]/span
            # WebDriverWait(self.driver, 40).until(
            #     EC.element_to_be_clickable((By.XPATH, '//*[@class="css-xip6hz-Logo"]'))).click()

            # WebDriverWait(self.driver, 20).until(
            #     expected_conditions.visibility_of_element_located((By.XPATH, '//*[@class="css-xip6hz-Logo"]')))

            self.SelectLocation()
            self.driver.get(self.current_url)
            self.IsLoading()
            self.LoadMore()
            self.FetchProducts()
            self.SaveToFile()
        except Exception as e:
            print("ERROR: ", e)

    def SelectLocation(self):
        self.driver.find_element("xpath", "//div[contains(@class,'DeliveryAddressPicker')]").click()
        # WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="css-1an9ecb-AddressButton"]'))).click()
        # WebDriverWait(self.driver, 20).until(
        #     expected_conditions.visibility_of_element_located((By.XPATH, '//*[@class="css-1an9ecb-AddressButton"]')))

        self.ShimmerEffectDetection()
        self.EnterZipCode()
        self.ShimmerEffectDetection()
        self.SelectLocationFromAddress()
        self.ShimmerEffectDetection()
        self.SelectAddress()
        self.ShimmerEffectDetection()
        self.SelectArea()
        self.driver.find_element("xpath", "//span[text()='Save Address']").click()
        time.sleep(5)
        self.CheckIfModalIsShowing()

    def CheckIfModalIsShowing(self):
        while True:
            try:
                self.driver.find_element("xpath", "//span[text()='No thanks']").click()
            except:
                print("Modal Not Found")
                break

    def ShimmerEffectDetection(self):
        while True:
            try:
                self.driver.find_elements("xpath", "//div[contains(@data-testid,'loading-list-test-id')]")
                print("Loading...")
                time.sleep(0.5)
                break
            except:
                print("Loaded!")
                break

    def EnterZipCode(self):
        while True:
            try:
                self.driver.find_element("xpath", "//input[contains(@id,'streetAddress')]").send_keys(self.zip)
                break
            except:
                print("Need time to load..")
                time.sleep(1)

    def SelectArea(self):
        while True:
            try:
                self.driver.find_element("xpath", "//span[text()='{}']".format(self.Area)).click()
                break
            except:
                print("Need time to load..")
                time.sleep(1)

    def SelectLocationFromAddress(self):
        while True:
            try:
                self.driver.find_element("xpath", "//span[text()='{}']".format(self.Location)).click()
                break
            except:
                print("Need time to load..")
                time.sleep(1)

    def SelectAddress(self):
        while True:
            try:
                self.driver.find_element("xpath", "//input[contains(@id,'streetAddress')]").send_keys(self.Address)
                break
            except:
                print("Need time to load..")
                time.sleep(1)

    def IsHasMore(self):
        try:
            self.driver.find_element("xpath", "//button[contains(@class,'LoadMore')]")
            return True
        except:
            print("No is more")
            return False

    def IsLoading(self):
        count = 1
        while count != 0:
            try:
                count = len(self.driver.find_elements("xpath", "//div[contains(@aria-label,'Loading')]"))
                time.sleep(2)
            except:
                count = 0

    def LoadMore(self):
        more = self.IsHasMore()
        while more and self.SCROLL_LIMIT:
            self.SCROLL_LIMIT = self.SCROLL_LIMIT - 1
            try:
                self.driver.find_element("xpath", "//button[contains(@class,'LoadMore')]").click()
                self.IsLoading()
                more = self.IsHasMore()
            except StaleElementReferenceException as e:
                print("Loading..")
                more = True
            except ElementClickInterceptedException:
                time.sleep(1)
                self.driver.find_element_by_css_selector("body").send_keys(Keys.PAGE_UP)
                self.driver.find_element_by_css_selector("body").send_keys(Keys.PAGE_DOWN)
                self.driver.find_element_by_css_selector("body").send_keys(Keys.PAGE_UP)
                self.driver.find_element_by_css_selector("body").send_keys(Keys.PAGE_DOWN)
                more = self.IsHasMore()

            except NoSuchElementException:
                self.driver.find_element_by_css_selector("body").send_keys(Keys.PAGE_UP)
                self.driver.find_element_by_css_selector("body").send_keys(Keys.PAGE_DOWN)
                more = self.IsHasMore()
        else:
            print("Loaded all products")

    def FetchProducts(self):
        try:
            products = self.driver.find_elements("xpath", "//div[contains(@class,'ItemCardHoverProvider')]")
            # print("Products: ",len(products), "Links: ", len(self.links))
            for i, product in enumerate(products):
                link = self.driver.find_elements("xpath", "//div[contains(@class,'ItemCardHoverProvider')]/div/div/a")
                if len(link)>=i:
                    link = link[i].get_attribute("href")
                else:
                    continue
                self.links.append(link)
                # print("#{} - #{}".format(i + 1, len(products)))
            # print("We got #{} product(s). start fetching data".format(len(self.links)))
            self.driver.close()
            self.GoThroughEveryProduct()
            self.driver.quit()
        except Exception as e:
            print("ERROR: ", e)

    def GoThroughEveryProduct(self):

        self.filename = '{}_{}_{}_{}.csv'.format(self.searchterm, self.zip, self.Area, str(datetime.datetime.now()))

        if "http" in self.searchterm:
            last = self.searchterm.split("/")[-1]
            self.filename = 'CATEGORY_{}_{}_{}_{}.csv'.format(last, self.zip, self.Area, str(datetime.datetime.now()))

        if len(self.links) > 300:
            self.links = self.links[:300]

        print(f"Writing {len(self.links)} Products")
        for link in self.links:
            print(link)
            item = link.split("/items/")[1]
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                'Cookie': '__Host-instacart_sid=7UgrCEYOF-qGKuN08_yj_UvsXU5AboBaacxdWwSFAv0'}
            try:
                req = requests.get("https://www.instacart.com/v3/containers/items/{}".format(item), headers=headers)
                req = req.json()
                product_id = req["container"]["modules"][0]["data"]["item"]["product_id"]
                # url = "https://www.instacart.com/store/" + str(req["container"]["path"])
                title = req['container']['title']
                price = req['container']['modules'][0]['data']['item']['pricing']['price']
                full_price = req['container']['modules'][0]['data']['item']['pricing']['full_price']
                full_price_label = req['container']['modules'][0]['data']['item']['pricing']['full_price_label']
                secondary_price = req['container']['modules'][0]['data']['item']['pricing']['secondary_price']
                price_per_unit = req['container']['modules'][0]['data']['item']['pricing']['price_per_unit']
                units = req['container']['modules'][0]['data']['item']['size']
                image = req['container']['modules'][0]['data']['item']['image']['url']
                date_time = datetime.datetime.now()
                raw_json = req['container']
                description = self.TryToGetProductDescription(req)
                ingredient = self.TryToGetProductIngredient(req)
                product_object = {
                    "product_id": product_id,
                    "title": title,
                    "price": price,
                    "price_per_unit": price_per_unit,
                    "full_price": full_price,
                    "full_price_label": full_price_label,
                    "secondary_price": secondary_price,
                    "units": units,
                    "image": image,
                    "description": description,
                    "ingredient": ingredient,
                    "link": link,
                    "search_term": self.searchterm,
                    "date_time": date_time,
                    "raw_json": raw_json
                }
                self.products.append(product_object)

                # if file does not exist write header
                obj = pd.DataFrame.from_dict(product_object)
                if not os.path.isfile(self.filename):
                    obj.to_csv("backup/"+self.filename, index=False)
                else:  # else it exists so append without writing the header
                    obj.to_csv("backup/"+self.filename, mode='a', header=False, index=False)

            except Exception as e:
                print("ERROR:{}".format(e))
                pass

    def TryToGetProductDescription(self, j_request):
        modules_len = len(j_request['container']['modules'])
        modules = j_request['container']['modules']
        for m in range(0, modules_len):
            try:
                desc_len = len(modules[m]['data']['details'])
                for ii in range(0, desc_len):
                    if modules[m]['data']['details'][ii]['header'] == "Details":
                        return modules[m]['data']['details'][ii]['body']
                    return "No Description Detected!"
            except:
                pass

    def TryToGetProductIngredient(self, j_request):
        modules_len = len(j_request['container']['modules'])
        modules = j_request['container']['modules']
        for m in range(0, modules_len):
            try:
                desc_len = len(modules[m]['data']['details'])
                for ii in range(0, desc_len):
                    if modules[m]['data']['details'][ii]['header'] == "Ingredients":
                        return modules[m]['data']['details'][ii]['body']
                    return "No ingredient Detected!"
            except:
                pass

    def SaveToFile(self):
        df = pd.DataFrame(self.products)
        df.to_csv("instacart_data/" + self.filename, index=False)
        self.products = []
        self.links = []
        self.current_url = ""
        self.searchterm = None

        # with open(filename, 'w', newline='',
        #           encoding="utf-8-sig", ) as Saver:
        #     headers = [
        #         "product_id",
        #         "title",
        #         "price",
        #         "price_per_unit",
        #         "full_price",
        #         "full_price_label",
        #         "secondary_price",
        #         "units",
        #         "image",
        #         "description",
        #         "ingredient",
        #         "link",
        #         "date_time",
        #         "raw_json"
        #     ]
        #     dw = csv.DictWriter(Saver, delimiter=',', fieldnames=headers)
        #     dw.writeheader()
        #     results_writer = csv.writer(Saver)
        #     for p in self.products:
        #         try:
        #
        #             results_writer.writerow(
        #                 [
        #                 p["product_id"],
        #                 p["title",]
        #                 p["price"],
        #                 p["price_per_unit"],
        #                 p["full_price"],
        #                 p["full_price_label"],
        #                 p["secondary_price"],
        #                 p["units"],
        #                 p["image"],
        #                 p["description"],
        #                 p["ingredient"],
        #                 p["link"],
        #                 p["date_time"],
        #                 p["raw_json"]
        #                 ])
        #         except Exception as e:
        #             print("ERROR: Saving file error, ", e)
        #             continue
        #     self.products = []


if __name__ == '__main__':
    smt_dsp = SmartDisplayWithTranslate()
    app = Instacart()
    try:
        smt_dsp.stopSmartDisplay()
    except:
        pass
