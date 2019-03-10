import scrapy


class qnrf_scraper(scrapy.Spider):
    """
    Scraper class thatholds the fucntion for scraping the website pub.qgrants.org

    Methods:
        parse - Collects the URLS
        parse_research_page - Parses the collected URLS

    """
    name = "qnrfspider"
    start_urls = ['https://pub.qgrants.org/Awards/SearchResult/']
    no_of_urls = None
    labels = ['Proposal Number:', 'Program Cycle:', 'Submitting Institution Name:', 'Project Status:', 'Start Date:',
              'Lead Investigator:', 'Project Duration:', 'End Date:', 'SubmissionType:', 'Proposal Title:',
              'Benefit to Qatar:', "Proposal Description:",
              'Research Area Keywords:', 'Research Type:']

    def parse(self, response):
        """
        Function collects all the urls linking to the project details at "https://pub.qgrants.org/Awards/SearchResult"
        """
        print("\n\n Parsing Now \n\n")
        urls = response.xpath('//table//tr/td[6]/a/@href').extract()

        # Get URLS for debugging purposes
        # urls = urls[0:10]

        # Get these URLS only
        # urls = ["https://pub.qgrants.org/Awards/ProjectDetails?p=29146&s=V&prm2=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0"]
        # urls = ["https://pub.qgrants.org/Awards/ProjectDetails?p=25834&s=N&prm2=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0"]
        # urls = ["https://pub.qgrants.org/Awards/ProjectDetails?p=14258&s=Y&prm2=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0"]

        # NPRP8-1556-3-313 - Columns missing values, multiple values
        # urls = ["https://pub.qgrants.org/Awards/ProjectDetails?p=18938&s=N&prm2=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0",
        #         "https://pub.qgrants.org/Awards/ProjectDetails?p=29146&s=V&prm2=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0",
        #         "https://pub.qgrants.org/Awards/ProjectDetails?p=30765&s=J&prm2=0&prm3=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0",
        #         "https://pub.qgrants.org/Awards/ProjectDetails?p=25834&s=N&prm2=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0",
        #         "https://pub.qgrants.org/Awards/ProjectDetails?p=25783&s=N&prm2=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0",
        #         "https://pub.qgrants.org/Awards/ProjectDetails?p=4409&s=H&prm2=0&prm3=0&prm4=0&prm5=0&prm6=0&prm9=0&prm12=0&prm13=0&prm14=0"]


        self.no_of_urls = len(urls)
        print("Number of documents : {}".format(self.no_of_urls))

        for url in urls:
            next_page = response.urljoin(url)
            yield response.follow(next_page, self.parse_research_page)

    def parse_research_page(self, response):
        """
        Function that parses each value under the labels given below

        'Proposal Number:', 'Program Cycle:', 'Submitting Institution Name:', 'Project Status:', 'Start Date:',
        'Lead Investigator:', 'Project Duration:', 'End Date:', 'SubmissionType:', 'Proposal Title:',
        'Benefit to Qatar:', "Proposal Description:", 'Research Area Keywords:', 'Research Type:'

        :param response:
        :return:
        """
        def extract_with_xpath(search_query_label):
            # return response.css(query).extract_first().strip()
            # return response.xpath('//a[contains(@href, "image")]/img/@src').extract()

            return response.xpath('//div[@class ="row"]//div[@class = "form-group"]/label[contains (text(),$query_label)]/following::div/div/text()', query_label=search_query_label).extract_first()

        # For Testing in scrapy shell
        # response.xpath('//div[@class ="row"]//div[@class = "form-group"]/label[contains (text(),"Proposal Number:")]/following::div/div/text()').extract_first()

        def extract_with_xpath_extra_info():
            # Old Method
            # return response.xpath('//div[contains(@class, "panel-title") and contains (text(),"Institution")]//following::div[contains(@class, "form-group")]//text()[normalize-space()]').extract()

            return response.xpath('//div[contains(@class, "panel-title") and contains (text(),"Institution")]//following::div[contains(@class, "form-group")]').extract()

        def extract_with_xpath_research_table():
            return response.xpath("//fieldset//div[@class = 'form-group'][not(label)]//text()").extract()
            # return response.xpath("//fieldset//div[@class = 'form-group']//text()").extract()

        # TODO: Bad programming practice here, Need to loop this somehow.
        yield {self.labels[0]: extract_with_xpath(self.labels[0]),
               self.labels[1]: extract_with_xpath(self.labels[1]),
               self.labels[2]: extract_with_xpath(self.labels[2]) or extract_with_xpath("School:"),
               self.labels[3]: extract_with_xpath(self.labels[3]),
               self.labels[4]: extract_with_xpath(self.labels[4]),
               self.labels[5]: extract_with_xpath(self.labels[5]),
               self.labels[6]: extract_with_xpath(self.labels[6]),
               self.labels[7]: extract_with_xpath(self.labels[7]),
               self.labels[8]: extract_with_xpath(self.labels[8]),
               self.labels[9]: extract_with_xpath(self.labels[9]),
               self.labels[10]: extract_with_xpath(self.labels[10]),
               self.labels[11]: extract_with_xpath(self.labels[11]),
               self.labels[12]: extract_with_xpath(self.labels[12]),
               self.labels[13]: extract_with_xpath(self.labels[13]),
               "extra_info": extract_with_xpath_extra_info(),
               "research_table_info": extract_with_xpath_research_table(),
               "URL": response.request.url
               }
