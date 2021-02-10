import requests
import os
import json
import urllib

from urllib.parse import urlparse
from bs4 import BeautifulSoup


def get_reg_data(link):
    if link.startswith('http://grls') or link.startswith('https://grls'):
        web_page = BeautifulSoup(requests.get(link, {}).text, "lxml")
        reg_number = web_page.find(name="input", attrs={"id": "ctl00_plate_RegNr"})
        reg_id = web_page.find(name="input", attrs={"id": "ctl00_plate_hfIdReg"})
        print(reg_id["value"], reg_number["value"])

        return reg_number["value"], reg_id["value"]
    else:
        raise ValueError('We only support valid GRLS links.')


def get_file_links(reg_num, reg_id):
    url = 'http://grls.rosminzdrav.ru/GRLS_View_V2.aspx/AddInstrImg'
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain',
               'Content-Encoding': 'utf-8'}
    data = {"regNumber": reg_num,
            "idReg": reg_id}

    answer = requests.post(url, data=json.dumps(data), headers=headers)
    print(reg_num, answer)
    return answer.json()


def download_file(url, location):
    print("Downloading... ", url)
    file = requests.get(url)
    with open(location, 'wb') as f:
        f.write(file.content)


def get_pdfs(reg_num, reg_id):
    response = get_file_links(reg_num, reg_id)
    d = json.loads(response["d"])
    instructions = d['Sources'][0]['Instructions']

    instr_dict = {}

    for instr in instructions:
        images = instr['Images']

        if len(images) > 1:
            for image in images:
                url_encoded_str = '/' + image['Url'].split('\\')[1] + '/' + image['Url'].split('\\')[2] + '/' + \
                                  image['Url'].split('\\')[3] + '/' + image['Url'].split('\\')[4]
                filename = os.path.basename(urlparse(url_encoded_str).path)
                download_file("http://grls.rosminzdrav.ru" + url_encoded_str, filename)
                instr_dict[image['Label']] = filename

        else:
            url_encoded_str = '/' + images[0]['Url'].split('\\')[1] + '/' + images[0]['Url'].split('\\')[2] + '/' + \
                              images[0]['Url'].split('\\')[3] + '/' + images[0]['Url'].split('\\')[4]
            filename = os.path.basename(urlparse(url_encoded_str).path)
            download_file("http://grls.rosminzdrav.ru" + url_encoded_str, filename)
            instr_dict[images[0]['Label']] = filename

    return instr_dict
