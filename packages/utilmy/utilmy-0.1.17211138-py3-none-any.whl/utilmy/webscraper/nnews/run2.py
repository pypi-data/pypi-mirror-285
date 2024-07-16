"""


pip install fire


python dom_save.py test1

     




 Playwright issues:
    IP blocking:
    Timeout  
    DOM : issues with parsing.

Playwright --> execute the javascript and all live compute
  --> final computed DOM (visible on the browser)

1)
   Playwright --> Save the serialzied DOM on disk
   User Agent: Mozilla Iphone 10.

2) load the DOM from disk --> parse it by another tool (beautiful)









        
"""
from playwright.sync_api import sync_playwright
import re
import time

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from playwright._impl._utils import serialize, deserialize
import pandas as pd



#### pip install --upgrade utilmy
from utilmy import pd_to_file, pd_read_file


MISC_WORDS = ["Articles", "News", "Share", "LinkedIn", "Twitter", "Facebook", "WhatsApp", "Email"]




async def dom_extract_v2(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        dom = await page.content()
        await browser.close()
        return dom
    
    
async def dom_extract(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        dom = await page.content()
        serialized_dom = serialize(dom)
        await browser.close()
        return serialized_dom




def url_dom_fetch_all(urls=None, dirout="/ztmp/urls_dom_raw.parquet"):

   if urls is None:
      urls = [
                "https://3dprint.com/109310/airbus-autodesk-dividing-wall/amp/",
                "https://coincentral.com/partnering-with-consensys-amazon-web-services-launches-kaleido-blockchain-platform/",
                "https://investors.bakkt.com/news/news-details/2022/Bakkt-and-Global-Payments-Announce-Strategic-Alliance/default.aspx",
                "https://new.abb.com/news/detail/85887/abb-working-with-aws-to-develop-digitally-integrated-all-electric-operations-for-net-zero-emissions-mining",
                "https://news.microsoft.com/2020/10/19/bentley-systems-expands-alliance-with-microsoft-to-accelerate-infrastructure-digital-twin-innovations/",
      ]                 
   df = [] 
   for url in urls: 
      # dom_raw = asyncio.run(extract_dom(url))
      dom_raw = asyncio.get_event_loop().run_until_complete(dom_extract(url))
      df.append([[ url, dom_raw  ]])
      
   ### save on disk   
   df = pd.DataFrame(df, columns=['url', 'dom'])
   pd_to_file(df, dirout,  show=1)    




async def dom_deserialize_playwright_async(serialized_dom):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        deserialized_dom = deserialize(page, serialized_dom)
        await browser.close()
        return deserialized_dom


def process_dom_with_bs4(serialized_dom):
    soup = BeautifulSoup(serialized_dom, 'html.parser')
    # Example processing: Extract all links
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return links




def test1():
    # url = 'https://example.com'
    # serialized_dom = asyncio.run(dom_extract(url))
    urls = [ "https://www.prnewswire.com/news-releases/microsoft-announces-3-3-billion-investment-in-wisconsin-to-spur-artificial-intelligence-innovation-and-economic-growth-302139892.html"]
    url_dom_fetch_all(urls=urls,  dirout="ztmp/urls_dom_raw.parquet")

    # To deserialize
    df_dom = pd_read_file("ztmp/urls_dom_raw.parquet")
    print(df_dom)
    dom = df_dom["dom"].values[0]
    dom2 = deserialize(dom)   
    links = process_dom_with_bs4(dom2)
    print(links)





























def clean(string):
    return re.sub('\n+', '', re.sub('\s+', ' ', string)).strip()

def remove_misc(text):
    for misc in MISC_WORDS :
        text = text.replace(misc, "")

    return text

def url_extract_words(url) :

    # trims last char if it is "/"
    if url.endswith("/") :
        url = url[:-1]

    # get the longest string which is potentially the url title
    word_list = url.split("/")[-1]

    # many urls will have potential keywords list in second last part of it
    if len(url.split("/")[-1]) <  len(url.split("/")[-2]) :
        word_list = url.split("/")[-2]

    # remove words with length less than 5
    word_list = list(filter(lambda ele: len(ele) >= 5, word_list.split("-")))

    return word_list, url

def get_best_content(txt_all, txt_specific, txt_all_sel, txt_sel_specific):
    if (len(txt_all) > 0 and len(txt_specific) > 0) and (len(txt_all) > len(txt_specific)):

        # if there is slight difference (upto 20%) in the text lengths, then it is highly possible that specific tags have got precise core content
        if float(len(txt_specific))/float(len(txt_all)) < 0.2:
            txt, txt_sel = txt_specific, txt_sel_specific
        else:
            txt, txt_sel = txt_all, txt_all_sel

    elif txt_specific != "":
        txt, txt_sel = txt_specific, txt_sel_specific

    else :
        txt, txt_sel = txt_all, txt_all_sel

    return txt, txt_sel


def find_best(text, text_sel, title, title_sel, txt, txt_sel, ttl, ttl_sel, txt_len, ttl_len, word):
    if txt_len < len(text) :
        txt, txt_sel, txt_len = text, text_sel, len(text)

    if title.lower().startswith(word.lower()):
        # this is the title even if anything else has longer length
        ttl, ttl_sel, ttl_len = title, title_sel, 200

    if ttl_len < len(title):
        ttl, ttl_sel, ttl_len = title, title_sel, len(title)

    return txt, txt_sel, txt_len, ttl, ttl_sel, ttl_len

def extract_tag_text(page, elts, word, source):
    max_len, text, text_sel = 0, "", ""

    try :
        for elt in elts:
            # checking if the elt is html elt or not if not isinstance(elt, page._elt_handle_factory.create_js_handle('HTMLelt')._impl), so if goes to except, means elt is not html elt and we should move to next elt in loop
            try :
                elt_text = elt.inner_text()

            except :
                continue

            # skip texts exceeding char len of 230 for potential titles
            if source == "Title" and len(elt_text) > 230:
                continue

            else :
                elt_text = remove_misc(elt_text)

            # check if given word is present in the element text
            if word.lower() in elt_text.lower():
                elt_tag = elt.get_property('tagName').json_value().lower()

                # skip "script" tags
                if elt_tag == "script" :
                    continue

                # check if element is having class attribute present
                elt_classes = None

                if elt.get_attribute("class") :
                    elt_classes = ".".join(elt.get_attribute("class").split())

                elt_sel = f"{elt_tag}.{elt_classes}" if elt_classes else elt_tag

                # prioritize elements with tag=h1, for potential titles over other elements
                if source.strip() == "Title" and elt_tag == "h1":
                    return elt_text, elt_sel

                if max_len < len(elt_text) :
                    text, text_sel, txt_len = elt_text, elt_sel, len(elt_text)

    except Exception as e:
        pass

    return text, text_sel



def playw_cookies(page):
    try:
        # list of possible "accept all cookies" button selectors
        cookie_btn_sel = 'button[title="Accept all"], button[id="onetrust-accept-btn-handler"], a[id="btnSelectAllCheckboxes"], button[aria-label="Accept cookies"], button[id*="cookie"], button[class*="cookie"]'
        if page.is_visible(cookie_btn_sel):
            page.click(cookie_btn_sel)

    except:
        pass


def playw_find_sel_by_text(page, txt):

    playw_cookies(page)

    # find all elts, potential title and potential content elements
    all_elts = page.query_selector_all("body *")
    title_elts = page.query_selector_all('h1, h2, [class*="heading"], [class*="header"], [class*="title"]')
    txt_elts = page.query_selector_all('[class*="entry-content"], [class*="articleBody"], [class*="post-content"], [class*="content-body"], [class*="article-body"], [class*="the-content"], [class*="article-content"]')

    # get best title and core text found for the given word from all potential elements
    title, title_sel = extract_tag_text(page, title_elts, txt, "Title")
    txt_specific, txt_sel_specific = extract_tag_text(page, txt_elts, txt, "Core")
    txt_all, txt_all_sel = extract_tag_text(page, all_elts, txt, "Core")

    # choose one core text from "potential selectors" and "all selectors"
    txt, txt_sel = get_best_content(txt_all, txt_specific, txt_all_sel, txt_sel_specific)

    return txt_sel, txt, title_sel, title

def test1():
    urls_list = ["https://3dprint.com/109310/airbus-autodesk-dividing-wall/amp/"]
    run(urls_list)

def run(urls_list):
    fout        = open("results_cleaned_code.tsv", "w")
    fout_miss   = open("exceptions_cleaned_code.tsv", "w")

    # write headers in output files
    fout.write("\t".join([ "url", "text_sel", "core_text", "title_sel", "title" ])+"\n")
    fout_miss.write("\t".join([ "url", "exception_message"]))

    # open browser with playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page    = browser.new_page()

        # parse urls in list, one by one to get the core text and title
        for url1 in urls_list :
            # open link in the browser
            page.goto(url1)
            try :
                # get list of keywords from url to search in text
                word_list, url1 = url_extract_words(url1)

                txt_len, txt, txt_sel = 0, "", ""
                ttl_len, ttl, ttl_sel = 0, "", ""

                for word in word_list:
                    text_sel, text, title_sel, title = playw_find_sel_by_text(page, word)

                    # compare the potential text and title we got for this word, with texts and titles from previous words and update the texts, selectors, max lengths of texts
                    txt, txt_sel, txt_len, ttl, ttl_sel, ttl_len = find_best(text, text_sel, title, title_sel, txt, txt_sel, ttl, ttl_sel, txt_len, ttl_len, word_list[0])
                            
                # write output for every url, so file keeps getting updated after every url run
                fout.write("\t".join([clean(url1), clean(txt_sel), clean(txt), clean(ttl_sel), clean(ttl)])+"\n")

            except Exception as e:

                # write url and exception message in file
                fout_miss.write(url1+"\t"+clean(str(e))+"\n")

        browser.close()

    fout.close()
    fout_miss.close()

test1()



                                        
        




###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()





