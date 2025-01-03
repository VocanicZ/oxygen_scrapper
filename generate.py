from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import re
import convert

def getDriver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox") # linux only
    chrome_options.add_argument("--headless=new") # for Chrome >= 109
    chrome_options.add_argument("--user-data-dir=F:/Temp/Selenium")
    # chrome_options.add_argument("--headless")
    # chrome_options.headless = True # also works
    return webdriver.Chrome(options=chrome_options)

def closeDriver(driver):
    driver.quit()

def info_float(text):
    return float(re.sub(r'[^0-9.-]', '', text))

def scrape(driver, url, js, state, sub_state, delay=10):
    js_out = {}
    name = convert.get(js, "name")
    file_name = convert.get(js, "file_name")
    left_arrow = ["solidify", "condense"]
    try:
        key = convert.get(js, "db")
        driver.get(url+key)
        d_trigger = convert.get(js, "d_trigger", "name")
        try:
            WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.XPATH, f"//h5[text()='{d_trigger}']"))
            )
        except Exception as e:
            print(f"Error: Unable to find the element with text '{d_trigger}'. {e}")
            return
        rendered_html = driver.page_source
        soup = BeautifulSoup(rendered_html, 'html.parser')
        target_h5 = soup.find('h5', text=d_trigger)
        
        if not target_h5:
            print(f"No <h5> tag found containing text: {d_trigger}")
            return
        
        parent_div = target_h5.find_parent('div').find_parent('div')
        if parent_div:
            #print(f"Parent <div> class: {parent_div.get('class')}")
            """
            with open("result.html", 'w', encoding='utf-8') as file:
                file.write(parent_div.prettify())
            """
        else:
            print(f"No parent div found for <h5> containing text: {name}")
            return
            
        main_div=parent_div.findChild('div', recursive=False).findChild('div', recursive=False)
        if main_div:
            #print(f"main <div> class: {main_div.get('class')}")
            """
            with open("result.html", 'w', encoding='utf-8') as file:
                file.write(parent_div.prettify())
            """
        else: 
            print(f"No main div found")
            return
        
        _comment = main_div.findChild('p', recursive=False).get_text(strip=True)
        
        main_array_div = main_div.findChildren('div', recursive=False)
        if not main_array_div:
            print("main array not found")
            return
        
        # data section
        data = {}
        property_div, info_div, additional_info_div, *main_array_div = main_array_div

        # properties
        properties = []
        for property in property_div.findChildren('div', recursive=False):
            text = property.find('span').get_text(strip=True)
            #print(text)
            properties.append(convert.get(js, "file", text))
        data['properties']=properties

        # info
        for info in info_div.find_all('tr'):
            data[convert.s(info.find('th').get_text(strip=True).replace('.', ''))] = info_float(info.find('td').get_text(strip=True))

        # additional info
        _, additional_info_div = additional_info_div.findChildren('div', recursive=False)
        additional_info = {}
        for info in additional_info_div.find_all('tr'):
            additional_info_key = convert.s(info.find('th').get_text(strip=True).replace('.',''))
            additional_info_value = info_float(info.find('td').get_text(strip=True))
            additional_info[additional_info_key] = additional_info_value
        data['additional_info'] = additional_info
        data['state'] = state
        data['type'] = sub_state
        
        # todolist get from wiki
        # todo: radiation_absorption
        # todo: chemical_symbol
        # todo: biome

        # recipe section
        recipe = {}

        for i in main_array_div:
            if i.find('h6') == None:
                break
            data_key = convert.s(i.find('h6').get_text(strip=True))
            data_value = {}
            img=[]

            def inner_left(js=js,data_value=data_value):
                left=div[0]
                left_name = left.findChild('a',recursive=False)['href'].split('/')[-1]
                data_value["min"] = info_float(left.findChild('a').findChild('span').get_text(strip=True))
                data_value["min_target"] =  left_name
                return 
            
            def inner_right(js=js,data_value=data_value):
                right=div[-1]
                right_name = right.findChild('a',recursive=False)['href'].split('/')[-1]
                data_value["max"] = info_float(right.findChild('a').findChild('span').get_text(strip=True))
                data_value["max_target"] = right_name
            
            match data_key:
                case "state_transitions":
                    body = i.findChild('div', recursive=False)
                    img = body.findChildren('img', recursive=False)
                    left_img = img[0]
                    left_alt = left_img.get('alt', None).replace(" into...", '').lower()
                    div = body.findChildren('div', recursive=False)
                    if left_alt in left_arrow:
                        right_img = img[-1]
                        right_alt = right_img.get('alt', None).replace(" into...", '').lower()
                        inner_left(js,data_value)
                        data_value["min_process"] = left_alt
                        if len(img) > 1:
                            inner_right(data_value)
                            data_value["max_process"] = right_alt
                    else:
                        if len(img) > 1:
                            right_img = img[1]
                            right_img.get('alt', None).replace(" into...", '').lower()
                            inner_left(js, data_value)
                            data_value["min_process"] = right_alt
                        inner_right(data_value)
                        data_value["max_process"] = left_alt

            recipe[data_key] = data_value
        
        # final touch
        js_out = {
            "name": name,
            "id": file_name,
            "_comment": _comment,
            "data": data,
            "recipe": recipe
        }
        return js_out
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return None