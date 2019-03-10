## QF Research Data Visualization in Dashboard

This software facilitate the visualization of research data on QNRF website. Provides information regarding personnel and research projects in the state of Qatar in an easy interpretable way for decision makers to find professors working in a research area and make funding decisions as necessary.

This project utilises Python, Dash (upon flask) and ElasticSearch for the webpage.

Scrapy is heavily utilized in order to crawl the QNRF website for data collection.


## Software Requirements

Python3 >= 3.6  
ElasticSearch - https://www.elastic.co/downloads/elasticsearch  
Bitbucket Git (to pull code) or Dropbox(No VCS here)  

Postman - to debug elasticsearch queries  



Python Library Requirements

Scrapy==1.5.0  
elasticsearch==6.3.0    
plotly==3.1.1  
numpy==1.12.1  
dash==0.26.3  
Jinja2==2.10  
networkx==1.11  
Flask==0.12  
SQLAlchemy==1.1.9  
Flask_Login==0.4.1  
pandas==0.19.2  
dash_html_components==0.11.0  
dash_auth==1.1.2  
dash_core_components==0.28.0  
elasticsearch_dsl==6.1.0  


Installation Procedure

Install elasticsearch  
Install scrapy and above said libraries.  

Make sure elasticsearch is working properly - eg: adding a new index, deleting index etc  
https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html  

Usual errors:  
1) /Common error  - During ElasticSearch start up  
Fix: Install Java 8 or higher with 64 bit,
Also add java to path.  more info here https://discuss.elastic.co/t/cannot-start-elasticsearch/129779  

2) encoding char error for pandas or any python open file.  
Fix: In mac change encoding to -'utf-8'  
Fix: In windows change encoding to 'cp1252' for all read_csv for pandas  


### TO RUN IN WINDOWS

1) open terminal as administrator
2) go to QNRF_Visualization\elasticsearch-6.4.0
3) type in <bin\elasticsearch.bat>
4) Open Anaconda Prompt or a terminal which can run python3.  
5) cd to folder qnrf-research-visualization/Dash/  
6) type in <python app.py> i.e run app.py  
8) open localhost:8050
9) enter username: hello password:world  
10) Use the QNRF Application.
