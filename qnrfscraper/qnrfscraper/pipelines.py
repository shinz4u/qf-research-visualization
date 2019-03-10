# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
from itertools import zip_longest
import re
import numpy as np
import pandas as pd

from collections import OrderedDict


class QnrfscraperPipeline(object):
    main_file = None
    pi_file = None
    institution_file = None
    outcome_file = None

    labels = None
    personnel_labels = None
    institution_labels = None
    outcome_labels = None

    qnrf_main_writer = None
    qnrf_personnel_writer = None
    qnrf_institution_writer = None
    qnrf_outcome_writer = None

    index_number = 0

    def process_item(self, item, spider):
        """

        :param item: scraped content of 1 article
        :param spider:
        :return:
        """
        # print(item)
        for key in item.keys():
            if item[key] and key != "extra_info" and key != "research_table_info":
                item[key] = item[key].strip()
        # line = json.dumps(dict(item)) + "\n"
        item['Personnel'], item['Institution'], item['Outcomes'] = self.process_extra_info(item['extra_info'])
        item["research_area_1"], item["sub_category_1"], item["speciality_1"], item["research_area_2"], item[
            "sub_category_2"], item["speciality_2"] = self.process_research_area(item['research_table_info'])
        del item['extra_info']
        del item['research_table_info']

        #Adding index of row to the csv
        item['_id'] = self.index_number
        self.index_number += 1
        print(self.index_number)

        personnel_to_write = self.process_triple_tuple_list(item['Proposal Number:'], item['Personnel'], self.personnel_labels)
        institution_to_write = self.process_triple_tuple_list(item['Proposal Number:'], item['Institution'], self.institution_labels)
        outcome_to_write = self.process_four_tuple_list(item['Proposal Number:'], item['Outcomes'],
                                                              self.outcome_labels)
        item['Research Keyword 1'], item['Research Keyword 2'], item['Research Keyword 3'], item['Research Keyword 4'], item['Research Keyword 5'] = self.process_research_keywords(item["Research Area Keywords:"])
        del item['Research Area Keywords:']

        item['Project Duration:'] = self.process_project_duration(item['Project Duration:'])
        item['Program Cycle:'] = self.remove_text_after_space(item['Program Cycle:'])
        self.writer_function(self.qnrf_main_writer, item)

        # Personnel and Institution CSV files
        # So writer_function_triple


        # Adding index to  personnel_to_write, institution_to_write, outcome_to_write

        #  TODO: make it a single function by modularisation
        self.writer_function_triple(self.qnrf_personnel_writer, personnel_to_write)
        self.writer_function_triple(self.qnrf_institution_writer, institution_to_write)
        self.writer_function_triple(self.qnrf_outcome_writer, outcome_to_write)

        return item

    def remove_text_after_space(self, text, there=re.compile(re.escape(' ')+'.*')):
        """This function removes text after a whitespace
        Use case : "YSREP 01" --> "YSREP"
                    "NPRP 07" --> "NPRP"
        """
        return there.sub('', text)

    def process_research_keywords(self, research_keyword):
        """Since there are 5 research keywords always
        returning the split value of 5 keywords

        Also Handles cases where research keywords are not provided or less than 5
        """
        research_keyword_split = research_keyword.split(";")

        # Handling cases where research keywords are not provided or less than 5
        while len(research_keyword_split) < 5:
            research_keyword_split.append("")
        return research_keyword_split[0], research_keyword_split[1], research_keyword_split[2], research_keyword_split[3], research_keyword_split[4]

    def process_research_area(self, text_array):
        """
        Processes the research_table_info containing research (Research Area,Sub Research Area,Sub Speciality,Primary?,Secondary?)
        Strips \n \t and spaces
        :param text_array:
        :return: a list containing the processed departments in this order "research_area_1,sub_category_1,speciality_1,research_area_2,sub_category_2,speciality_2"
        """
        text_array = np.array(text_array)
        text_array = text_array.reshape(-1, 5)
        text_array = text_array[:2]
        text_array = np.delete(text_array, [3, 4], 1)
        text_array = np.array([[item.strip() for item in x] for x in text_array])
        text_array = text_array.flatten()
        print(text_array)

        while len(text_array) < 6:
            text_array = np.append(text_array, "")
        return text_array

    def process_triple_tuple_list(self, proposal_number, triple_tuple_list, field_names):
        """"
        ['Proposal Number:', 'role', 'investigator', 'institution'])
        converts this to dictionary to write into csv an.
        """
        counter = 1
        # [{'name': rec[0], 'age': rec[1], 'weight': rec[2]} for rec in recs]
        if len(triple_tuple_list) < 1:
            # handling cases where there is no item['Personnel'] or/and item['Institution']
            counter += 1
            return [{field_names[0]: proposal_number , field_names[1]: "", field_names[2]: "", field_names[3]: ""}]
        long_list = np.insert(triple_tuple_list, 0, proposal_number, axis=1)

        # TODO: return a generator or list for better memory management?
        counter += 1
        return [{field_names[0]: item[0], field_names[1]: item[1], field_names[2]: item[2], field_names[3]: item[3]} for item in long_list]

    def process_four_tuple_list(self, proposal_number, triple_tuple_list, field_names):
        """"
        ['Proposal Number:', 'type', 'title', 'authors', 'reference_no'])
        converts this to dictionary to write into csv an.
        """
        # [{'name': rec[0], 'age': rec[1], 'weight': rec[2]} for rec in recs]
        if len(triple_tuple_list) < 1:
            # handling cases where there is no item['Personnel'] or/and item['Institution']
            return [{field_names[0]: proposal_number , field_names[1]: "", field_names[2]: "", field_names[3]: "", field_names[4]: ""}]
        long_list = np.insert(triple_tuple_list, 0, proposal_number, axis=1)

        # TODO: return a generator or list for better memory management?
        return [{field_names[0]: item[0], field_names[1]: item[1], field_names[2]: item[2], field_names[3]: item[3], field_names[4]: item[4]} for item in long_list]

    def open_spider(self, spider):
        """This method is called automatically when the spider is opened."""
        # self.labels = ['Proposal Number:', 'Program Cycle:', 'Submitting Institution Name:', 'Project Status:',
        #                'Start Date:',
        #                'Lead Investigator:', 'Project Duration:', 'End Date:', 'SubmissionType:', 'Proposal Title:',
        #                'Research Area Keywords:', 'Research Type:', 'Personnel', 'Institution', 'URL']

        # Making first self.labels as _id so that elasticsearch picks it up.
        self.labels = ['_id', 'Proposal Number:', 'Program Cycle:', 'Submitting Institution Name:', 'Project Status:',
                       'Start Date:',
                       'Lead Investigator:', 'Project Duration:', 'End Date:', 'SubmissionType:', 'Proposal Title:',
                       'Research Keyword 1', 'Research Keyword 2', 'Research Keyword 3',
                       'Research Keyword 4', 'Research Keyword 5', 'Research Type:', 'Personnel', 'Institution', 'Outcomes', 'URL',
                       'Benefit to Qatar:', "Proposal Description:","research_area_1","sub_category_1","speciality_1",
                       "research_area_2","sub_category_2","speciality_2"]

        self.personnel_labels = ['Proposal Number:', 'role', 'investigator', 'institution']
        self.institution_labels = ['Proposal Number:', 'institution', 'country', 'role']
        self.outcome_labels = ['Proposal Number:', "type", "pub_title", "authors", "reference_no"]

        self.main_file = open('qnrf_funding_data.csv', 'w', newline='')
        self.qnrf_main_writer = csv.DictWriter(self.main_file, fieldnames=self.labels)
        self.qnrf_main_writer.writeheader()

        self.pi_file = open('qnrf_funding_personnel.csv', 'w', newline='')
        self.qnrf_personnel_writer = csv.DictWriter(self.pi_file, fieldnames=self.personnel_labels)
        self.qnrf_personnel_writer.writeheader()

        self.institution_file = open('qnrf_funding_institution.csv', 'w', newline='')
        self.qnrf_institution_writer = csv.DictWriter(self.institution_file, fieldnames=self.institution_labels)
        self.qnrf_institution_writer.writeheader()

        self.outcome_file = open('qnrf_funding_outcomes.csv', 'w', newline='')
        self.qnrf_outcome_writer = csv.DictWriter(self.outcome_file, fieldnames=self.outcome_labels)
        self.qnrf_outcome_writer.writeheader()

        # TODO: Write the function that does the parsing of institution and personnel

    def writer_function(self, csv_writer, item):
        # qnrf_writer = csv.DictWriter(self.main_file, fieldnames=labels)
        """writes all the data to the csv file based on whether item contains 1 or more arrays"""
        csv_writer.writerow(item)

        # if len(item) > 1:
        #     csv_writer.writerows(item)
        # else:
        #     csv_writer.writerow(item)

    def writer_function_triple(self, csv_writer, item):
        """Write rows function"""
        csv_writer.writerows(item)

    def process_institution(self, institution):
        pass

    def process_personnel(self, personnel):
        pass

    def close_spider(self, spider):
        """This method is called automatically when the spider is closed."""
        self.main_file.close()
        # print("Completed funding file creation")
        self.institution_file.close()
        self.pi_file.close()
        self.outcome_file.close()
        print("All files closed")

        data_institution = pd.read_csv("qnrf_funding_institution.csv", header=0)
        data_institution.to_csv("qnrf_funding_institution.csv", index_label="_id")
        print("Completed institution file creation")


        data_pi_file = pd.read_csv("qnrf_funding_personnel.csv", header=0)
        data_pi_file.to_csv("qnrf_funding_personnel.csv", index_label="_id")
        print("Completed PI file creation")

        data_outcome_file = pd.read_csv("qnrf_funding_outcomes.csv", header=0)
        data_outcome_file.to_csv("qnrf_funding_outcomes.csv", index_label="_id")
        print("Completed outcome file creation")


    def process_extra_info(self, info):
        a = None
        # extra_info_extracter = lambda x: re.search('label>(.*)</label', x) or re.search('\\r\\n(.*)\\r\\n', x)
        extra_info_extracter = lambda x: re.search('label>(.*)</label', x) or re.search('\\r\\n(.*)\\r\\n', x,
                                                                                        re.DOTALL)
        re_result_list = [extra_info_extracter(x) for x in info]
        info = [x.group(1).strip() for x in re_result_list]
        info = [x.strip() for x in info]
        triple_tuple_list = self.grouper(3, info)
        institution = []
        personnel = []
        outcome = []

        # TODO: Case for handling the publications? Note that publication have 4 columns
        # publications = []

        # print(info)

        # TODO: Better switching should be implemented
        switch_val = 0
        for i in triple_tuple_list:
            # Personnel
            if i[0] == 'Role':
                switch_val = 1
                continue
            # Institution
            if i[0] == 'Institution':
                switch_val = 2
                continue
            # Outputs
            if i[0] == 'Type':
                switch_val = 0
                continue
            if switch_val is 1:
                personnel.append(i)
            elif switch_val is 2:
                institution.append(i)
            elif switch_val is 0:
                for j in i:
                    outcome.append(j)


        # Process Outcome here
        outcome = [x for x in outcome if x is not None]
        # for idx, val in enumerate(outcome[::-1]):
        #     if val is None:
        #         del outcome[idx]
        #     if val:
        #         break
        # outcome = outcome[1:]
        # # Since output
        processed_outcome = self.grouper(4, outcome[1:])

        # Removing duplicate values and returning the list
        return list(OrderedDict.fromkeys(personnel)), list(OrderedDict.fromkeys(institution)), list(OrderedDict.fromkeys(processed_outcome))

    def process_outcome(self, outcome):
        pass


    def grouper(self, n, iterable, padvalue=None):
        """"grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"""
        return zip_longest(*[iter(iterable)] * n, fillvalue=padvalue)

    def process_project_duration(self, info):
        """Removes all the space between the project duration"""
        return " ".join(info.split())