
# IMPORT AND MODIFY THE DATA
import pandas as pd


class DataProcessor:
    ''' Class that provides the data '''
    data = None
    personnel_data = None
    outcome_data = None

    data_source_funding = "./Static/data/qnrf_funding_data.csv"
    data_source_personnel = "./Static/data/qnrf_funding_personnel.csv"
    data_source_outcome = "./Static/data/qnrf_funding_outcomes.csv"

    def __init__(self):
        self.data = pd.read_csv(self.data_source_funding)
        self.personnel_data = pd.read_csv(self.data_source_personnel)
        self.outcome_data = pd.read_csv(self.data_source_outcome)

        # Data Columns (UPDATE AS NEED BE)
        # Proposal Number:,Program Cycle:,Submitting Institution Name:,Project Status:,Start Date:,Lead Investigator:,
        # Project Duration:,End Date:,SubmissionType:,Proposal Title:,Research Keyword 1,Research Keyword 2,Research Keyword 3,
        # Research Keyword 4,Research Keyword 5,Research Type:,Personnel,Institution,URL

        # Index(['_id', 'Proposal Number:', 'Program Cycle:',
        #        'Submitting Institution Name:', 'Project Status:', 'Start Date:',
        #        'Lead Investigator:', 'Project Duration:', 'End Date:',
        #        'SubmissionType:', 'Proposal Title:', 'Research Keyword 1',
        #        'Research Keyword 2', 'Research Keyword 3', 'Research Keyword 4',
        #        'Research Keyword 5', 'Research Type:', 'Personnel', 'Institution',
        #        'Outcomes', 'URL', 'Benefit to Qatar:', 'Proposal Description:',
        #        'research_area_1', 'sub_category_1', 'speciality_1', 'research_area_2',
        #        'sub_category_2', 'speciality_2'],
        #       dtype='object')

        # Processing and removing unwanted columns for faster response
        self.process_funding_data()
        self.process_outcome_data()

    def process_funding_data(self):

        self.data.drop(columns=['SubmissionType:', 'Research Keyword 1', 'Research Keyword 2',
                               'Research Keyword 3', 'Research Keyword 4', 'Research Keyword 5',
                               'Research Type:', 'Personnel', 'Institution','Outcomes', 'URL',
                               'Benefit to Qatar:', 'Proposal Description:','research_area_1',
                               'sub_category_1', 'speciality_1', 'research_area_2','sub_category_2',
                               'speciality_2'],
                       inplace=True,
                       axis=1)

        self.data["Start Date:"] = pd.to_datetime(self.data["Start Date:"])
        self.data["End Date:"] = pd.to_datetime(self.data["End Date:"])

        # Setting all school names as "Secondary Schools"
        self.data.loc[self.data["Program Cycle:"] == "SSREP", ["Submitting Institution Name:", "Lead Investigator:"]] = ["Secondary Schools", "School Teachers"]

        start_date = self.data["Start Date:"]

        self.data['start_year'] = pd.DatetimeIndex(start_date).year
        self.data['start_month'] = pd.DatetimeIndex(start_date).month
        self.data.fillna(-1, inplace=True)

    def process_outcome_data(self):
        # Removing NaN Values from outcome_data
        self.outcome_data.dropna(subset=["type", "pub_title", "authors", "reference_no"], how='all', inplace=True)