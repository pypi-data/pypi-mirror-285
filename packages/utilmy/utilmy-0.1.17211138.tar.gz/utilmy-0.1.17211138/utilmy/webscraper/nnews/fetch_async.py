"""
Need to download many website using different ways

  1) requests
      URL --> download --> save on disk as JSON (even it failed, json is written)


    2)For all the failed JSON:     
      DO
      2) Playwright/Selenium
               URL --> download --> save on disk as JSON (even it failed, json is written)
   

     3) For all the failed JSON 
         DO   3) Use 3rd API scrapingBee
                URL --> download --> save on disk as JSON (even it failed, json is written)


### Fetch again.
pip install fire utilmy

python myfile.py  myfunctionOfmyCode  --url. "dsfsfd"
python myfile.py  test1

"""
import os, time, random

from utilmy import log, loge, log2, os_makedirs, json_load, json_save
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor



###################################################################
##### Global params  ##############################################
url0    = 'https://app.scrapingbee.com/api/v1/'
params0 =  { 'api_key': '5WZXPPVDF9UMC5Y0Y797F4WX1S2ESQ6GRX',
            'url': '', 
            'wait': '500',
            'premium_proxy': 'false',
            'stealth_proxy': 'false', 
            'country_code':'jp'
        }

params1 =  { 'api_key': '5WZXPPVDF9UMC5Y0Y797F4WX',
            'url': '', 
            'wait': '1000',
            'premium_proxy': 'true',
            'stealth_proxy': 'true', 
            'country_code':'jp'
        }

def test_index0():
  index = IndexLock('test_file.txt', min_size=5, skip_comment=True, ntry=20)
  files_to_write = ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt', 'file5.txt']
  
  def write_to_index(val):
      index.save_isok(val)
  
  def read_from_index():
      return index.read()
  def simulate_concurrent_access():
      threads = []
      for i in range(5):
          t = threading.Thread(target=write_to_index, args=(files_to_write,))
          threads.append(t)
          t.start()
      for thread in threads:
          thread.join()
      index_contents = read_from_index()
      log2("Current index contents after writing:", index_contents)
  simulate_concurrent_access()
  


###################################################################
def test_index0_worker(data):
    try:
        index_lock, data = data

        #### index_lock.put
        files_inserted = index_lock.put(data)
        if files_inserted:
            log2(f"Process {os.getpid()}, index_lock.put: {files_inserted}")

        #### index_lock.get_block
        time.sleep(2+ random.random() )
        data_all =  ['data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10']
        fnew = index_lock.get_block(data_all)
        log2(f"Process {os.getpid()}, get_block: {fnew}")

        #### index_lock.get_block
        flist = index_lock.get()
        log2(f"Process {os.getpid()}, get: {flist}")

    except Exception as e:
        log2(f"Exception in worker {os.getpid()}: {e}")

def test_index0_simulate_parallel_writes(dirindex, data_list):
    index_lock = IndexLock(dirindex)
    args_list  = [(index_lock, data) for data in data_list]

    with ProcessPoolExecutor(max_workers=len(data_list)) as executor:
        futures = [executor.submit(test_index0_worker, args) for args in args_list]
        time.sleep(4)
        for future in futures:
            future.result()
    log2("All processes finished.")


def test_index0():
    """ 
         python fetch_async.py test_index0
          log:
            Process 11356, index_lock.put: ['data1']
            Process 6524, index_lock.put: ['data2']

            file lock waiting 1s
            Process 2216, index_lock.put: ['data7']


            Process 9368, index_lock.put: ['data4']
            Process 8668, index_lock.put: ['data8']
            Process 11356, get_block: None
            Process 11356, get: ['data1', 'data2', 'data3', 'data5', 'data7', 'data9', 'data10', 'data6', 'data4', 'data8']
            Process 6524, get_block: None


            Process 9368, get: ['data1', 'data2', 'data3', 'data5', 'data7', 'data9', 'data10', 'data6', 'data4', 'data8']
            Process 8668, get_block: None
            Process 8668, get: ['data1', 'data2', 'data3', 'data5', 'data7', 'data9', 'data10', 'data6', 'data4', 'data8']
            All processes finished.
            Current contents of the file:
            data1
            data2
            data3
            data5
            data7
            data9
            data10
            data6
            data4

    
    """
    dirindex  = 'ztmp/test_file.txt'
    data_list = ['data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'data8', 'data9', 'data10']
    test_index0_simulate_parallel_writes(dirindex, data_list)
    with open(filename, 'r') as f:
        contents = f.readlines()

    log("###### Assertions ###")
    contents = [line.strip() for line in contents]
    log(contents)
    assert len(contents) == len(set(contents)), "There are duplicate entries in the file"
    assert set(contents) == set(data_list),     "Not all entries were processed"


###################################################################
def test1():        
    """
        ### pip install fire utilmy
        cd  folder
        python fetch_async.py test1
        logs:          
            For: fetch_and_save_requests(urls, dirout=dirout +"/requests") 
            python fetch_async.py test1
            Success:  {'url': 'https://books.toscrape.com/catalogue/a-light-in-the
            Success:  {'url': 'https://books.toscrape.com/catalogue/tipping-the-ve

            For: fetch_and_save_playwright(urls, dirout=dirout + "/playwright" )  
            python fetch_async.py test1
            Success:  {'url': 'https://books.toscrape.com/catalogue/a-light-in-the
            Success:  {'url': 'https://books.toscrape.com/catalogue/tipping-the-ve  
    """

    dirout ="ztmp/jsondir/"
    urls = ['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html',
            'https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']

    
    fetch_and_save_requests(urls, dirout=dirout +"/requests")  

    fetch_and_save_playwright(urls, dirout=dirout + "/playwright" )  

    ### pip install utilmy
    from utilmy import glob_glob, os_makedirs, json_load, log
    dirjson ="ztmp/jsondir/request/*/*.json"
    file_list = glob_glob(dirjson)

    for fi in file_list:
        ddict = json_load(fi)

        assert ddict['url']

        #### Check if not empty
        if len(str(ddict)) < 70:
            log("Empty json", fi)
        else:
            log("Success: ", str(ddict)[:60])
    
def test_pipeline_scrape():
    """
    logs:
        python fetch_async.py test_pipeline_scrape
        2 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        thread  0 1
        thread  1 1
        starts 0
        0 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        starts 1
        1 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]
        0 job finished
        1 job finished
        n_processed 2
        url json files: 2
    """

    """
    Input: list of urls in text file from disk

    1. Fetch parallel using fetch_and_save_requests()
    2. Grab the missing urls from JSON files on disk
    3. Fetch parallel using fetch_and_save_playwright()
    4. Grab the missing urls from JSON files on disk
    """
    pipeline_scrape()


def test_pipeline_scrape_with_lock():
    """
    logs:
        ### Pick up one file not yet done #############################
        ### Read url ################################
        ### start fetch ################################
        2 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        thread  0 1
        thread  1 1
        starts 0
        0 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        starts 1
        1 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]
        0 job finished
        1 job finished
        n_processed 2
        ### start missing 1 ###########################
        url json files: 0
        2 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'], ['https://books.toscrap
        thread  0 1
        thread  1 1
        starts 0
        0 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]
        starts 1
        1 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        0 job finished
        1 job finished
        n_processed 2
        url json files: 0
        ### start missing 2 ###########################
        #### Report as done ###########################        
        done
    """
    
    pipeline_scrape()


def test_pipeline_multiprocessing():
    """
        ### Pick up one file not yet done #############################
        ### Pick up one file not yet done #############################
        ### Pick up one file not yet done #############################
        file lock waiting 1sfile lock waiting 1s

        ### Read url ################################
        ### start fetch ################################
        2 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        exist in Index, skipping ztmp/urlist\urllist_1.txt
        ### Read url ################################
        ### start fetch ################################
        2 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        exist in Index, skipping ztmp/urlist\urllist_1.txt
        ### Read url ################################
        ### start fetch ################################

        ### start missing 1 ###########################

        starts 0
        0 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        starts 1
        1 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]
        thread  0 1
        thread  1 1

        url json files: 0
        ### start missing 2 ###########################
        #### Report as done ###########################
        1 job finished
        n_processed 2
        url json files: 0
        ### start missing 2 ###########################
        #### Report as done ###########################
        Circular reference detected
        done
        Circular reference detected
        Circular reference detected
        done
        done
    """


def test_pipeline_multiprocessing_5_process():
    """
        python fetch_async.py test_pipeline_multiprocessing_5_process

        ### Pick up one file not yet done #############################
        ### Pick up one file not yet done #############################

        (1, 'The process cannot access the file because another process has locked a portion of the file.')
        (1, 'The process cannot access the file because another process has locked a portion of the file.')(1, 'The process cannot access the file because another process has locked a portion of the file.')
        ### Read url ################################
        ### start fetch ################################
        # (1, 'The process cannot access the file because another process has locked a portion of the file.')

        (1, 'The process cannot access the file because another process has locked a portion of the file.')
        ### start fetch ################################

        2(1, 'The process cannot access the file because another process has locked a portion of the file.')
        [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc(1, 'The process cannot access the file because another process has locked a portion of the file.')
        2
        (1, 'The process cannot access the file because another process has locked a portion of the file.')
        [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        (1, 'The process cannot access the file because another process has locked a portion of the file.')
    
        ### Read url ################################
        (1, 'The process cannot access the file because another process has locked a portion of the file.')### start fetch ################################

        (1, 'The process cannot access the file because another process has locked a portion of the file.')
        2 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        (1, 'The process cannot access the file because another process has locked a portion of the file.')
        (1, 'The process cannot access the file because another process has locked a portion of the file.')
        ### Read url ################################
        ### start fetch ################################
        2 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        ### Read url ################################
        ### start fetch ################################
        2 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'], ['https://books.tosc
        thread  0 1
        thread  1 1thread  0 1
        thread
        1 1
        thread  0 1
        thread  1 1

        startsstarts 0
        0
        00 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        starts 0
        0 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        starts 0

        1 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]
        0 job finished

        n_processed 12
        ### start missing 1 ###########################
        job finished
        url json files: 0
        n_processed 2
        2### start missing 1 ###########################
        [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'], ['https://books.toscrap1
        url json files:  job finished
        0
        2 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'], ['https://books.toscrap
        ### start missing 1 ###########################
        url json files: 0
        2 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html'], ['https://books.toscrap
        thread  thread  00 1
        thread  1  1
        starts 0
        starts starts 0
        000
        [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]0
        0[['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']][['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]

        [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]starts
        0
        0 [['https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html']]
        starts 1
        starts1  [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]1

        starts starts11  1
        [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        1
        1 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]starts[['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        1

        1 [['https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html']]
        0 job finished
        1 job finished
        n_processed 2
        url json files: 0
        ### start missing 2 ###########################
        #### Report as done ###########################
        0 job finished
        0 job finished

        url json files: 0
        ### start missing 2 ###########################
        #### Report as done ###########################
        1 job finished
        n_processed 2
        url json files: 0
        ### start missing 2 ###########################
        #### Report as done ###########################
        Circular reference detectedCircular reference detected

    """
    import multiprocessing
    import concurrent.futures

    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(pipeline_scrape) for _ in range(5)]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()  # Get the result of the process
            except Exception as e:
                log(e)
            else:
                log("Pipeline scrape completed successfully.")
                




##############################################################################
####### Synchronous HTML grabberfunction #####################################
def fetch_and_save_requests(urls, dirout="./ztmp/data/urls_fetch/"):
    # Standalone/Autonomous function
    import time, random, json, requests
    
    if isinstance(urls, str):
        urls = [urls]
    
    if isinstance(urls, list):  ### for parallel compute
        if isinstance(urls[0], list):
          urls = urls[0]
    
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',        
    }
    
    for url in urls:
        try:
            response = requests.get(url=url, headers=headers, timeout=10)
            response.raise_for_status()

            html = response.text
            dd = { "url": url,  "html": html }            
            
            ts, tag  = int(time.time()),random.randint(10000, 99999)
            filename = f"{dirout}/{ts}_{tag}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dd, f, ensure_ascii=False, indent=2)

        except Exception as e:                        
            loge('Error: ', url, e)


def fetch_and_save_selenium(urls, dirout="./ztmp/data/urls_fetch/"):
    # Standalone/Autonomous function
    import time, random, json
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    if isinstance(urls, str):
        urls = [urls]
    
    if isinstance(urls, list):  ### for parallel compute
        if isinstance(urls[0], list):
          urls = urls[0]
    
    # Create headless chrome instance
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set path to chromedriver as per your configuration
    webdriver_service = Service(ChromeDriverManager().install())

    # Choose Chrome Browser
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)    
    
    for url in urls:
        try:
            driver.get(url)            
            
            html = driver.page_source
            dd = { "url": url,  "html": html }
            
            ts, tag  = int(time.time()),random.randint(10000, 99999)
            filename = f"{dirout}/{ts}_{tag}.json"            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dd, f, ensure_ascii=False, indent=2)
        except Exception as e:
            loge('Error: ', url, e)            
    
    driver.quit()   


def fetch_and_save_playwright(urls, dirout="./ztmp/data/urls_fetch/"):
    # Standalone/Autonomous function
    import time, random, json
    from playwright.sync_api import sync_playwright
    
    if isinstance(urls, str):
        urls = [urls]
    
    if isinstance(urls, list):  ### for parallel compute
        if isinstance(urls[0], list):
          urls = urls[0]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for url in urls:
            try:
                page.goto(url)
                page.wait_for_timeout(5000)   
                
                html = page.content()
                dd = { "url": url,  "html": html }
                
                ts, tag  = int(time.time()),random.randint(10000, 99999)
                filename = f"{dirout}/{ts}_{tag}.json"            
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(dd, f, ensure_ascii=False, indent=2)
            except Exception as e:
                loge('Error: ', url, e)                
    
        browser.close()    


def fetch_and_save_3rd(urls, dirout="./ztmp/data/urls_fetch/", version='v1'):
    # Standalone/Autonomous function
    global params_global_3rd

    params0 = params_global_3rd[version]

    import time, random, json, requests, copy
    
    if isinstance(urls, str):
        urls = [urls]
    
    if isinstance(urls, list):  ### for parallel compute
        if isinstance(urls[0], list):
          urls = urls[0]
          
    for url in urls:
        try:
            pp = copy.deepcopy(params0)
            pp['url'] = url
            response = requests.get( url=url0, params=pp, )    
            html = response.text
            dd = { "url": url,  "html": html }
            
            ts, tag  = int(time.time()),random.randint(10000, 99999)
            filename = f"{dirout}/{ts}_{tag}.json"            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dd, f, ensure_ascii=False, indent=2)
        except Exception as e:
            loge('Error: ', url,e)





#################################################################################################
def fetch_parallel_from_textfile(fun_async, url_list: list,
                                 dirout: str = "./ztmp/data/urls_fetch/",
                                 npool=3, max_url=1000000, istart=0):
    from utilmy.parallel import multithread_run, multiproc_tochunk
    from utilmy import os_makedirs
    import time

    os_makedirs(dirout)

    input_list_list = multiproc_tochunk(url_list[:max_url], npool=npool)
    input_fixed = {"dirout": dirout}  # input_fixed={'const': 50, 'const2': i}
    time.sleep(2)

    res = multithread_run(fun_async, input_list_list,
                          n_pool=npool, input_fixed=input_fixed)

###############################################
def pipeline_scrape(dirurlist="ztmp/urlist",
                    dirout="ztmp/urldone",
                    direport="ztmp/report/", npool=4):
    """
        alias scrape=" python fetch_async.py "
        scrape pipeline_scrape --dirurl "ztmp/urls/"  --direport "ztmp/report"
    """
    from utilmy import glob_glob

    dir_index = direport + "urllist_global_index.txt"
    index_lock = IndexLock(dir_index)

    log("### Pick up one file not yet done #############################")
    file_list = glob_glob(dirurlist + "/*.txt")
    ### Atomic read and write back 
    furl_current = index_lock.get_block(file_list)
    if furl_current is None: 
        log("All done")
        return 

                      
    log("### Read url ################################")
    with open(furl_current, 'r') as f:
        urls = f.read().split('\n')

                      
    log("### start fetch ################################")
    fun_async = fetch_and_save_requests
    fetch_parallel_from_textfile(fun_async, urls, npool=len(urls))


    log("### start missing 1 ###########################")
    done_urls = get_previous_done_urls(dirout)
    missing_urls = list(set(urls) - set(done_urls))

    if missing_urls:
        fun_async = fetch_and_save_playwright
        fetch_parallel_from_textfile(fun_async, missing_urls,
                                     npool=len(missing_urls))
        done_urls2 = get_previous_done_urls(dirout)
        done_urls2 = set(urls).intersection(set(done_urls2))
        missing_urls2 = list(set(urls) - set(done_urls2))

    log("### start missing 2 ###########################")


                      
    log("#### Report as done ###########################")
    dd = {
        'fileurl':     furl_current,
        'url_missing': missing_urls2,
        'url_done':    done_urls2
     }

    from utilmy import date_now, json_save
    import time
    import random

    y, m, d, h = date_now(fmt="%y-%m-%d-%H").split("-")
    ts, tag    = int(time.time()), random.randint(10000, 99999)
    json_save(dd, direport + f"/{y}/{m}/{d}/{h}/f{ts}_{tag}.json")
    log("All done")








##############################################################################
############# Search : fetch the URL #########################################


def test_pipeline_scrape_search():
    """
    python fetch_async.py pipeline_scrape_search
    logs

    """
    dirurlist="ztmp/urlsearchlist"
    dirout="ztmp/urldone"
    ll = [  "https://news.google.com/search?q=%22microsoft%22%20%22partner%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen",
            "https://news.google.com/search?q=microsoft%20%22acquisition%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen",
         ]
    for i in range(0, 6):
        with open( dirurlist + f"/urlsearch+{i}.txt", mode = 'w') as fp:
            fp.writelines(ll)

    pipeline_scrape_search(dirurlist=dirurlist,
                    dirout=dirout,
                    direport="ztmp/report/", npool=4)

    fjson - glob_glob(dirout +"/*.json" )
    

def pipeline_scrape_search(dirurlist="ztmp/urlsearchlist",
                    dirout="ztmp/urldone",
                    direport="ztmp/report/", npool=4):
    """
        alias scrape=" python fetch_async.py "
        scrape pipeline_scrape_search --dirurl "ztmp/urls/"  --direport "ztmp/report"
    """
    from utilmy import glob_glob, json_save

    dir_index = direport + "urlsearchlist_global_index.txt"
    index_lock = IndexLock(dir_index)

    log("### Pick up one file not yet done ##################")
    file_list = glob_glob(dirurlist + "/*.txt")
    ### Atomic read and write back 
    furl_current = index_lock.get_block(file_list)
    if furl_current is None: 
        log("All done")
        return 

                      
    log("### Read url ######################################")
    with open(furl_current, 'r') as f:
        urls = f.read().split('\n')
                      
    log("### start fetch ####################################")
    fun_async =  fetch_and_save_searchurl
    fetch_parallel_from_textfile(fun_async, urls, npool=len(urls))


    log("### start missing 1 ###########################")
    done_urls2 = get_previous_done_urls(dirout)
    missing_urls2 = list(set(urls) - set(done_urls2))

    # if missing_urls:
    #     fun_async =  fetch_and_save_3rd
    #     fetch_parallel_from_textfile(fun_async, missing_urls,
    #                                  npool=len(missing_urls))
    #     done_urls2 = get_previous_done_urls(dirout)
    #     done_urls2 = set(urls).intersection(set(done_urls2))
    #     missing_urls2 = list(set(urls) - set(done_urls2))
                      
    log("#### Report as done ###########################")
    dd = {
        'fileurl':     furl_current,
        'url_missing': missing_urls2,
        'url_done':    done_urls2
     }

    from utilmy import date_now, json_save
    import time, random
    ymdh = date_now(fmt="%y%m%d_%H%M").split("-")
    ts, tag    = int(time.time()), random.randint(10000, 99999)
    json_save(dd, direport + f"/{ymdh}_{ts}_{tag}.json")
    log("All done")




def fetch_and_save_searchurl(urls, dirout="./ztmp/data/urls_search/"):
    """
      output in. json :
        {
            'urlsearch': url_googlenews,
            'url_list': =[url1, url2, url3, ]
        }

        microsoft ai
        google deepmind
    """
    import json, time, random


    for url in urls:
        ddict = None

        ### Google News
        if "https://news.google.com/search?q" in url:
           x = url.split("search?q=")[-1] ## right
           x = x.split("&hl=")[0]   ### left
           keywordlist = (url, [ t.strip()  for t in  x.split("%22") ] )

           urlsearch, urls_list = urls_fetch_googlenews_single(url=x[0],  pagemax=2,)
           ddict  = {
               'urlsearch': urlsearch,
                'keywords':  keywordlist,
                'url_list':  urls_list
            }
        else:
            log('not implemented')

                    url_list.append({
                        'title': title,
                        'url':   link,
                        'date':   date,
                        'origin': urlsearch
                    })
            except Exception as e:
                print(f"Error: {e}")
                continue
        browser.close()

        if ddict:
            ts, tag  = int(time.time()),random.randint(10000, 99999)
            filename = f"{dirout}/{ts}_{tag}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(ddict, f, ensure_ascii=False, indent=2)



# @diskcache_decorator
def urls_fetch_googlenews_single(urlsearch=None, keywords="microsoft funding", pagemax=2,):
    """

    
        ## https://news.google.com/search?q=%22microsoft%22%20%22partner%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen
        ## https://news.google.com/search?q=microsoft%20%22acquisition%22%20when%3A7d&hl=en-US&gl=US&ceid=US%3Aen
        ### "https://news.google.com/search?q=". &hl=en-US&gl=US&ceid=US%3Aen"

    """
    from datetime import datetime

    if urlsearch is None :
        prefix = 'https://news.google.com'
        dt0 = datetime.now().strftime("%Y/%m/%d")
        urlp = "https://news.google.com/search?q="
        keys = keywords.split(" ")
        keys = [f"%22{x}%22" for x in keys]
        keys = "%20".join(keys)
        urlsearch = f"{urlp}{keys}&hl=en-US&when%3A15d&gl=US&ceid=US%3Aen"

    log(urlsearch)

    ARTICLE_SELECTOR = 'c-wiz.PO9Zff'
    TITLE_SELECTOR = 'a.JtKRv'
    LINK_SELECTOR = 'a.JtKRv'
    DATE_SELECTOR = 'time.hvbAAd'

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(urlsearch)
        page.wait_for_timeout(5000)

        url_list = []
        items = page.query_selector_all(ARTICLE_SELECTOR)

        for item in items:
            try:
                title_element = item.query_selector(TITLE_SELECTOR)
                link_element = item.query_selector(LINK_SELECTOR)
                date_element = item.query_selector(DATE_SELECTOR)
                #text_element = item.query_selector(TEXT_SELECTOR)

                if title_element and link_element and date_element:
                    title = title_element.inner_text().strip()
                    link = link_element.get_attribute('href')
                    date = date_element.inner_text().strip()
                    #text = TEXT_element.inner_text().strip()

                    url_list.append({
                        'title': title,
                        'url':   link,
                        'date':   date,
                        'origin': urlsearch
                    })
            except Exception as e:
                print(f"Error: {e}")
                continue
        browser.close()

    urls2 = [ {"url": str(prefix + x['url']),  'keywords': keywords,
                 'art_title': x['title'], 'art_dt': dt0 + x['date'],
                 'origin': x['origin']
              }  for x in url_list   ]
    return urlsearch, urls2



#################################################################################
def get_previous_done_urls(dirin=f"./ztmp/data/urls_fetch//**/*.json"):
    from utilmy import json_load, glob_glob

    urls_from_json = glob_glob(dirin)

    success_urls = set()
    for item in urls_from_json:
        data = json_load(item)

        txt = data['html']
        if len(txt) < 100:
            continue
        url = data['url']

        if isinstance(url, list):
            success_urls = success_urls | set(url)
        else:
            success_urls.add(url)

    log("url json files:", len(success_urls))

    return list(success_urls)




#########################################################################################################
####### Atomic File Index  read/writing #################################################################
class IndexLock(object):
    """
    Keep a Global Index of processed files.
    INDEX = IndexLock(findex)

    flist = index.save_isok(flist)  ## Filter out files in index and return available files
    ### only process correct files
    """
    # Manage Inventory Index with Atomic Write/Read

    def __init__(self, findex, file_lock=None, min_size=5, skip_comment=True, ntry=20):
        import os

        self.findex = findex

        os.makedirs(os.path.dirname(os.path.abspath(self.findex)),exist_ok=True)

        if file_lock is None:
            file_lock = os.path.dirname(
                findex) + "/" + findex.split("/")[-1].replace(".", "_lock.lock")

        self.plock = file_lock

        # Initiate the file
        if not os.path.isfile(self.findex):
            with open(self.findex, mode='a') as fp:
                fp.write("")

        self.min_size = min_size
        self.skip_comment = skip_comment
        self.ntry = ntry

    def read(self):
        return self.get()

    def save_isok(self, flist: list):
        return self.put(flist)

    def save_filter(self, val: list = None):
        return self.put(val)


    ######################################################################   
    def get_block(self, flist_ref:list, **kw):
        import random
        import time

        i = 0
        while i < self.ntry:
            try:
                lock_fd = os_lock_acquireLock(self.plock)
                flist_global_index = self.get()

                ## Files in flist_ref NOT in flist_global_index
                fnew = list( set(flist_ref).difference(set(flist_global_index)))

                if len(fnew) < 1:
                    return None 

                f_pickup_one = fnew[0] 
                with open(self.findex, mode='a') as fp:
                       fp.write(f_pickup_one+"\n")

                os_lock_releaseLock(lock_fd)
                return f_pickup_one    

            except Exception as e :
                time.sleep(i* (5 + random.random() ) )
                log(e)

        return None


    def get(self, **kw):
        """ Read the Global Index content and return it, Not atomic
            # return the list of files
        
        
        """
        with open(self.findex, mode='r') as fp:
            flist = fp.readlines()

        if len(flist) < 1:
            return []

        flist2 = []
        for t in flist:
            if len(t) < self.min_size:
                continue
            if self.skip_comment and t[0] == "#":
                continue
            flist2.append(t.strip())
        return flist2


    def put(self, val_list: list = None):
        """ Read, check if the insert values are there, and save the files
          flist = index.check_filter(flist)   ### Remove already processed files
          if  len(flist) < 1 : continue   ### Dont process flist

          ### Need locking mechanism Common File to check for Check + Write locking.
        """
        import random, time

        #### Val : List of values to be inserted
        if val_list is None:
            return []

        if isinstance(val, str):
            val_list = [val_list]

        i = 1
        while i < self.ntry:
            try:
                lock_fd = os_lock_acquireLock(self.plock)

                ### Discard if values already exist  #####################
                fall = self.read()
                val2 = []
                for fi in val:
                    if fi in fall:
                        print('exist in Index, skipping', fi)
                    else:
                        val2.append(fi)
                if len(val2) < 1:
                    return []

                ##### Write the list of values on Global Index file: Wont be able to use by other processes
                ss = ""
                for fi in val2:
                    ss = ss + str(fi).strip() + "\n"

                with open(self.findex, mode='a') as fp:
                    fp.write(ss)

                os_lock_releaseLock(lock_fd)

                #### Rerturn Value Actually inserted
                return val2

            except Exception as e:                
                log2(f"file_lock: {self.findex}")
                time.sleep(random.random() * i)
                i += 1


#####################################################################################################
######  Atomic Execution ############################################################################
def os_lock_acquireLock(plock: str = "tmp/plock.lock"):
    """
        acquire exclusive lock file access, return the locker
    """
    # import fcntl
    import os
    import portalocker

    os.makedirs(os.path.dirname(os.path.abspath(plock)), exist_ok=True)
    locked_file_descriptor = open(plock, 'w+')

    # fcntl.RedisLock(locked_file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    portalocker.lock(locked_file_descriptor,
                     portalocker.LOCK_EX | portalocker.LOCK_NB)

    return locked_file_descriptor


def os_lock_releaseLock(locked_file_descriptor):
    ''' release exclusive lock file access '''
    # import fcntl
    import portalocker

    # fcntl.flock(locked_file_descriptor, fcntl.LOCK_UN)
    portalocker.unlock(locked_file_descriptor)

    # locked_file_descriptor.close()


def os_lock_run(fun_run, fun_args=None, ntry=5, plock="tmp/plock.lock", sleep=5):
    """ Run a function in an atomic way :
         Write on disk  exclusively on COMMON File.
    """
    import time

    i = 0
    while i < ntry:
        try:
            lock_fd = os_lock_acquireLock(plock)
            fun_run(fun_args)
            os_lock_releaseLock(lock_fd)
            break
        except Exception as e:
            # log2(e)
            # reduce sleep time
            log2("file lock waiting", sleep, 'sec')
            time.sleep(sleep)
            i += 1
















def fetch_parallel(dirin:str  ="./ztmp/data/urls/url_all.csv",
                   dirout:str ="./ztmp/data/urls_fetch/latest/", 
                   npool=3, max_url=1000000, istart=0,):
    """ 
     and we dont need to care if the function failed or not.
       Function is launched --> manage itself.
        No Dependency

        Failure of one function does not impact others.....
            independent, autonomous.

        testing is easier: no dependency.
    """
    
    from utilmy.parallel import multithread_run,multiproc_tochunk
    from utilmy import os_makedirs
    import tempfile

    # myfun = fetch_and_save_3rdparty
    # myfun = fetch_and_save_selenium
    myfun = fetch_and_save_NewAlgo
    
    
    os_makedirs(dirout)

    urls = url_load_filter(dirin, istart=istart, max_url=max_url)
    input_list_list  = multiproc_tochunk(urls[:max_url], npool=npool )
    input_fixed = {"dirout": dirout}  # input_fixed={'const': 50, 'const2': i}
    time.sleep(2)

    res = multithread_run(myfun, input_list_list, 
                        n_pool=npool, input_fixed=input_fixed)






############## Multithread async runner ################################################
def multithread_run(
    fun_async,
    input_list: list,
    n_pool=5,
    start_delay=0.1,
    verbose=True,
    input_fixed: dict = None,
    npool=None,
    **kw,
):
    import functools
    import time

    n_pool = npool if isinstance(npool, int) else n_pool  ## alias

    #### Input xi #######################################
    if len(input_list) < 1:
        return []

    if input_fixed is not None:
        fun_async = functools.partial(fun_async, **input_fixed)

    #### Input xi #######################################
    xi_list = [[] for t in range(n_pool)]
    for i, xi in enumerate(input_list):
        jj = i % n_pool
        xi_list[jj].append(xi)  ### xi is already a tuple

    if verbose:
        for j in range(len(xi_list)):
            log("thread ", j, len(xi_list[j]))
        # time.sleep(6)

    #### Pool execute ###################################
    import multiprocessing as mp

    # pool     = multiprocessing.Pool(processes=3)
    pool = mp.pool.ThreadPool(processes=n_pool)
    job_list = []
    for i in range(n_pool):
        time.sleep(start_delay)
        log("starts", i)
        job_list.append(pool.apply_async(fun_async, (xi_list[i],)))
        if verbose:
            log(i, xi_list[i])

    res_list = []
    for i in range(len(job_list)):
        res_list.append(job_list[i].get())
        log(i, "job finished")

    pool.close()
    pool.join()
    pool = None
    log("n_processed", len(res_list))
    return res_list


def multiproc_tochunk(flist: list, npool=2):
    ll = []
    chunk = len(flist) // npool
    for i in range(npool):
        i2 = i + 1 if i < npool - 1 else 3 * (i + 1)
        ll.append(flist[i * chunk : i2 * chunk])
    log(len(ll), str(ll)[:100])
    return ll



















def url_load_filter(dirin, istart=0, max_url=1000000):
    urls = pd_read_file(dirin, sep="\t")
    urls = urls.iloc[istart:istart+max_url,:]
    log('N_urls : ', len(urls))
        
    urls_done = url_previous_done()
    urls = urls[ -urls.url.str.contains("edge") ]  
    urls = urls[ -urls.url.isin(urls_done) ]    
    urls = urls.drop_duplicates('url')

    log('N_urls to fetch: ', len(urls))
    return list(urls['url'].values)




def url_previous_done():
    
    flist = glob_glob(f"./ztmp/data/urls_fetch//**/*.json") 

    urls1 = []
    for fi in flist: 
        di = json_load(fi) 
        txt = di['html']
        if len(txt)< 100 : continue                 
        x =di['url']
        if isinstance(x, list):
            urls1 = urls1 + x 
        else:    
            urls1.append(x) 
            
    log("url json files:", len(urls1))
        
    flist = glob_glob(f"./ztmp/data/urls_text/**//*.parquet")    
    dfuu = pd_read_file(flist)
    dfuu = dfuu.drop_duplicates('url')
    urls = list(dfuu['url'].values)    
    urls = urls1 + urls
    urls = set(urls)
    log('N already fetched: ', len(urls))
    return urls
    




fetch_parallel(dirin  = "./ztmp/data/urls/url_all.csv",
               dirout = "./ztmp/data/urls_fetch/latest/", 
               istart=0,
               npool=5, max_url=20000)









###################################################################
def url_merge_json(dirin="./ztmp/data/urls_fetch/", dirout="./ztmp/data/urls_text/", istest=False):

    from src.utils.utilmy_base import hash_int64     
    flist = glob_glob(f"{dirin}/*.json",)    
        
    df = []
    for ii,fi in enumerate(flist): 
        if ii % 20 == 0 : log(ii)
        try:
            djson = json_load(fi)
            dd = html_parse_goose(djson['html'])
            ri ={
                'url'      : djson['url'], ### original url
                'date'     : str_to_date(dd['publish_date']),
                'title'    : dd['title'],
                'text'     : dd['cleaned_text'],
                'info_json': json.dumps(dd)
            }        
            df.append(ri)
        except Exception as e:
            log('error:', ii, e )
        if istest: break 
               
    df = pd.DataFrame(df)
    for ci in ['date', 'text', 'url' ]:
       df[ci] = df[ci].astype("str")
      
    ymd = date_now(fmt="%y%m%d")
    tag = hash_int64(str(df['url'].values))
    diroutk = f"{dirout}/{ymd}/url_text_{tag}.parquet"  
    pd_to_file(df, diroutk, show=1)
    return df 



def html_parse_goose(html):
    from goose3 import Goose
    if html.endswith('.html'):
       with open('./ztmp/data/urls/page1.html', 'r') as f:
           html_content = f.read()
    else: 
       html_content = html       

    g = Goose()
    article = g.extract(raw_html=html_content)
    dd = {
        'title'           : article.title,
        'cleaned_text'    : article.cleaned_text,
        'meta_description': article.meta_description,
        'meta_keywords'   : article.meta_keywords,
        'canonical_link'  : article.canonical_link,
        'domain'          : article.domain,
        'top_image'       : article.top_image.src if article.top_image else None,
        'movies'          : [v.src for v in article.movies],
        'publish_date'    : str(article.publish_date),
        'authors'         : article.authors,
        'tags'            : article.tags,
        'links'           : article.links,
        'final_url'       : article.final_url,
        'meta_lang'       : article.meta_lang,
        'meta_favicon'    : article.meta_favicon
    }
    return dd



def str_to_date(x):
    """
        str_to_date(1684171328 )
        str_to_date( ['2023-03-01 17:33:10', '2023-03-01T12:03:10+00:00'] )
        
    """
    import dateparser
    from utilmy import date_now
    if isinstance(x, list):
           if len(x)> 0 :
              x = x[0]
           else : return ""    
               
    x1 = str(x)
    try:
        x2 =float(x1)
        return date_now(x2, fmt="%Y-%m-%d")
    except :
        pass        

    try:                  
        x2 = str(x1).split("T")[0]
        d1 = dateparser.parse(x2)
        d1 = date_now(d1, fmt="%Y-%m-%d")
        return d1 
    except Exception as e:
        return str(x)


dftxt = url_merge_json(dirin="./ztmp/data/urls_fetch/latest/", 
                       dirout="./ztmp/data/urls_text/")


dftxt2 = url_merge_json(dirin="./ztmp/data/urls_fetch/done/", 
                       dirout="./ztmp/data/urls_text/")


dft = pd.concat((dftxt, dftxt2))
dft = dft.drop_duplicates('url')


###################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()




