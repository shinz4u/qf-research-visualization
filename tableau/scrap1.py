from bs4 import BeautifulSoup
import csv
import sys
import urllib2
import re
import requests
import itertools
from collections import Counter
import string

reload(sys)
sys.setdefaultencoding('utf8')

# to write output as txt file
orig_Stdout = sys.stdout

'''
. do your desired search and right click save html as SearchResults1.html
. you'll use the saved html file to extract urls which are from VIEW column more
'''

def scrapSearchResURL():
    '''
    . open saved results html file
    . use beautifulsoup to scrap for all links anchor tag "a"
    . store all links after concatenating the https://pub.qgrants.org
    . save all of the output as a txt file 'links1.txt'
    '''
    with open("SearchResult1.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    fwrite = open("links1.txt", 'w')
    sys.stdout = fwrite
    for link in soup.find_all('a'):
        data = link.get('href')
        print "https://pub.qgrants.org"+data

#call function
# scrapSearchResURL()
# print "done scraping and storing lincaks1.txt"

def scrapProjectFromURL():
    '''
    . read urls from links1.txt
    . use requests to visit the urls
    . use beautiful soup to parse and store proj desc, dates and other required data
    '''
    xx = []
    with open('links1.txt', 'r') as f:
        urls = f.readlines()
        # print urls

    # for all project urls
    fwrite = open("eDNewDesc.txt", 'w') # uncomment each section below, change file name and save
    sys.stdout = fwrite
    i = 1
    for x in urls:
        response = requests.get(x)
        soup = BeautifulSoup(response.content, "html.parser")
        # print i
        for elem in soup(text=re.compile(r'End Date:')):
            xyz = elem.parent.parent.parent #.get_text()
            print xyz.find_next_sibling("div").get_text()
        # for elem in soup(text=re.compile(r'End Date:')):
        #     print elem.parent.parent.parent.parent.get_text()
        # for elem in soup(text=re.compile(r'Research Area Keywords:')):
            # print elem.parent.parent.parent.parent.get_text()
        # for elem in soup(text=re.compile(r'Proposal Description')):
            # print elem.parent.parent.parent.parent.get_text()
        # for elem in soup(text=re.compile(r'Outputs/Outcomes')):
        #     print elem.parent.parent.parent.get_text()
        print "_____"
        i +=1
    print i

#call function
# scrapProjectFromURL()

# checking for one Project
# url = "https://pub.qgrants.org/Awards/ProjectDetails?p=29308&s=F&prm2=0&prm3=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=8&prm13=0&prm14=0"
#
# soup = BeautifulSoup(urllib2.urlopen(url), "html.parser")
#
# for elem in soup(text=re.compile(r'Proposal Description')):
#     print elem.parent.parent.parent.parent.get_text()

def cleanTxtFile():
    '''
    . remove unwanted space and text
    '''
    with open('eDNewDesc.txt') as infile, open('eDNewDesc2.txt', 'w') as outfile:
        for line in infile:
            # if not line.strip(): continue  # skip the empty line
            outfile.write(line.strip())  # non-empty line. Write it to output

#call function
# cleanTxtFile()


def cleanAllTxt():
    '''
    . remove unwanted space and text
    '''
    with open('keywordNewDesc2.txt') as infile, open('keywordNewDesc6.txt', 'w') as outfile:
        for line in infile:
            # if not line.strip(): continue  # skip the empty line
            # words = "";
            result =  line.lower()
            # result = result.replace(",", " ")
            result = result.replace(";", "\t")
            result = result.replace(",","  ")
            result = result.replace("research area keywords:", " ")
            outfile.write(result)#.strip())  # non-empty line. Write it to output
#call function
# cleanAllTxt()


def wordCounter():
    '''
    . counter for most used words in proj description
    '''
    fwrite = open("wordCount1.txt", 'w')
    sys.stdout = fwrite
    with open('projNewDesc3.txt', 'r') as f:
        ff = f.read()
        # i = 1
        # for line in ff:
            # print line
            # i += 1
            # print i
            # print "+++ ----------"
        wordcount = Counter(ff.split())
        for item in wordcount.items(): print("{}\t{}".format(*item))
#call function
# wordCounter()


def searchKeywords():
    exclude_list = ["security", "cyber security", "cybersecurity", "cyber-security", "threats", "attacks", "intrusion", "privacy"]
    data_set = []
    with open('projDesc.csv') as f:
    forbidden = re.compile('|'.join(re.escape(w) for w in exclude_list), re.I)
    for row in csv.reader(f):
        # Only record videos with at least 100 views and none of the bad words
        title, view_count = row
        if int(view_count) >= 100 and not forbidden.search(title):
            data_set.append(row)
#call function
searchKeywords()

# print "done!! :)"
