import requests
import bs4
import re
import time
import json



def main_page():
    req = requests.get("https://www.chicagotribune.com/")
    soup = bs4.BeautifulSoup(req.text,'html.parser')
    div = soup.findAll('div', attrs={'class': 'flex-grid'})
    refs = []
    ref_dict = {}
    for d in div:
        refs += re.findall(r'<h2 class="r-mb h6-mb h6">(.*?)</h2>', str(div))
        for ref in refs:
            key = re.sub(r'<.*?>', '', ref)
            val = re.findall(r'href="(.*?)"', ref)[0]
            ref_dict[key] = val
    return ref_dict


def content_news(news_link: str):
    #req = requests.get(news_link)
    news_link="https://www.chicagotribune.com/"
    req = requests.get(news_link)
    soup = bs4.BeautifulSoup(req.text,'html.parser')
    content_dict = {}

    if re.search('www.chicagotribune.com', news_link):
        cont = soup.findAll('main', attrs={'class': 'artcl--m'})
        aucont = soup.findAll('div', attrs={'class': 'byline-wrapper'})
    else:
        return {}

    paragraphs = []
    authors = []
    for div in cont:
        paragraphs += re.findall(r'<p.*?>(.*?)</p>', str(div))
    for div in aucont:
        authors += re.findall(r'<span><a.*?>(.*?)</a>', str(div))
    if len(paragraphs):
        content_dict['content'] = ' '.join(paragraphs)
    if len(authors):
        content_dict['authors'] = ' '.join(authors)
    return content_dict


def validate(entry: dict):
    keywords = ['republican', 'Republican', 'GOP', 'democratic', 'Democratic']
    title = entry.get('title')
    content = entry.get('content')
    if title == None or content == None:
        return False
    fit = False
    for keyword in keywords:
        if re.search(keyword, title):
            fit = True
        if re.search(keyword, content):
            fit = True
    return fit


def save_json (data, fname: str):
    with open(fname, 'w') as fp:
        json.dump(data, fp)


def load_json(fname: str):
    d = {}
    try:
        with open(fname, 'r') as fp:
            d = json.load(fp)
    finally:
        return d


if __name__ == '__main__':
    entries = load_json("chicagotribune.json")
    filtered_entries = load_json("chicagotribune_filtered.json")
    i = 1

    while 1:
        print("Попытка #" + str(i))
        refs = main_page()
        for entry_name, link in refs.items():
            if entries.get(link) == None:
                time.sleep(.5)
                print('Получение контента: "' + entry_name + '"...')
                news = content_news(link)
                if len(news):
                    news['title'] = entry_name
                    entries[link] = news
                    if validate(news):
                        filtered_entries[link] = news
                else:
                    entries[link] = {}
        save_json(entries, "chicagotribune.json")
        save_json(filtered_entries, "chicagotribune_filtered.json")
        print("Попытка #" + str(i) + " закончена\n")
        i += 1
        time.sleep(3600)