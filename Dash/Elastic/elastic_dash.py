from elasticsearch import helpers, Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl import Q
import csv
import math


# class ElementIndex(DocType):
#     id = Text()
#     name = Text()
#     address = Text()
#     url = Text()
#
#     class Meta:
#         index = 'csvfile'
#
#     def indexing(self):
#         obj = ElementIndex(
#             id=str(self['NAME']),
#             name=str(self['NAME'])
#         )
#         obj.save(index="csvfile")
#         return obj.to_dict(include_meta=True)
#
# def bulk_indexing(args):
#
#     # ElementIndex.init(index="index_name")
#     ElementIndex.init()
#     self.es = Elasticsearch()
#
#     # here your result dict with data from source
#
#     r = helpers.bulk(client=self.es, actions=(indexing(c) for c in result))
#     self.es.indices.refresh()

class ElasticDash():
    es = None
    index_name = None
    body = None

    #
    # _id, Proposal
    # Number:, Program
    # Cycle:, Submitting
    # Institution
    # Name:, Project
    # Status:, Start
    # Date:, Lead
    # Investigator:, Project
    # Duration:, End
    # Date:, SubmissionType:,
    # Proposal Title:,
    # Research
    # Keyword
    # 1, Research
    # Keyword
    # 2, Research
    # Keyword
    # 3, Research
    # Keyword
    # 4, Research
    # Keyword
    # 5, Research
    # Type:, Personnel, Institution, URL

    es_mappings_settings_no_shard = '''
                  {
                 "mappings": {
                   "csv": {
                     "properties": {
                       "Proposal Title:": {
                         "type": "text",
                         "analyzer": "english",
                         "fields": {
                           "fourgrams": {
                             "type": "text",
                             "analyzer": "fourgrams"
                           }
                         }
                       },
                       "Research Keyword 1": {
                         "type": "text",
                         "analyzer": "english",
                         "fields": {
                           "fourgrams": {
                             "type": "text",
                             "analyzer": "fourgrams"
                           }
                         }
                       },
                       "Research Keyword 2": {
                         "type": "text",
                         "analyzer": "english",
                         "fields": {
                           "fourgrams": {
                             "type": "text",
                             "analyzer": "fourgrams"
                           }
                         }
                       },
                       "Research Keyword 3": {
                         "type": "text",
                         "analyzer": "english",
                         "fields": {
                           "fourgrams": {
                             "type": "text",
                             "analyzer": "fourgrams"
                           }
                         }
                       },
                       "Research Keyword 4": {
                         "type": "text",
                         "analyzer": "english",
                         "fields": {
                           "fourgrams": {
                             "type": "text",
                             "analyzer": "fourgrams"
                           }
                         }
                       },
                       "Research Keyword 5": {
                         "type": "text",
                         "analyzer": "english",
                         "fields": {
                           "fourgrams": {
                             "type": "text",
                             "analyzer": "fourgrams"
                           }
                         }
                       },
                        "Benefit to Qatar:": {
                          "type": "text",
                          "analyzer": "english",
                          "fields": {
                            "fourgrams": {
                              "type": "text",
                              "analyzer": "fourgrams"
                            }
                          }
                        },
                        "Proposal Description:": {
                          "type": "text",
                          "analyzer": "english",
                          "fields": {
                            "fourgrams": {
                              "type": "text",
                              "analyzer": "fourgrams"
                            }
                          }
                        }
                     }
                   }
                 },
                 "settings": {
                   "analysis": {
                     "filter": {
                       "fourgrams_filter": {
                         "type": "ngram",
                         "min_gram": 4,
                         "max_gram": 4
                       }
                     },
                     "analyzer": {
                       "fourgrams": {
                         "type": "custom",
                         "tokenizer": "standard",
                         "filter": [
                           "lowercase",
                           "fourgrams_filter"
                         ]
                       }
                     }
                   },
                   "number_of_shards":1
                 }
               }
           '''

    desc2_mapping = '''
                                     {
                                      "mappings": {
                                        "csv": {
                                          "properties": {
                                            "Proposal Title:": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            },
                                            "Research Keyword 1": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            },
                                            "Research Keyword 2": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            },
                                            "Research Keyword 3": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            },
                                            "Research Keyword 4": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            },
                                            "Research Keyword 5": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            },
                                            "Benefit to Qatar:": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            },
                                            "Proposal Description:": {
                                              "type": "text",
                                              "analyzer": "english",
                                              "fields": {
                                                "fourgrams_test": {
                                                  "type": "text",
                                                  "analyzer": "fourgrams_test"
                                                }
                                              }
                                            }
                                          }
                                        }
                                      },
                                      "settings": {
                                        "analysis": {
                                          "filter": {
                                            "fourgrams_test_filter": {
                                              "type": "ngram",
                                              "min_gram": 4,
                                              "max_gram": 4
                                            }
                                          },
                                          "analyzer": {
                                            "fourgrams_test": {
                                              "type": "custom",
                                              "tokenizer": "standard",
                                              "filter": [
                                                "lowercase",
                                                "fourgrams_test_filter"
                                              ]
                                            }
                                          }
                                        },
                                        "number_of_shards": 1
                                      }
                                    }
                               '''
    fivegrams_mapping = '''
                                         {
                                          "mappings": {
                                            "csv": {
                                              "properties": {
                                                "Proposal Title:": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                },
                                                "Research Keyword 1": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                },
                                                "Research Keyword 2": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                },
                                                "Research Keyword 3": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                },
                                                "Research Keyword 4": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                },
                                                "Research Keyword 5": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                },
                                                "Benefit to Qatar:": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                },
                                                "Proposal Description:": {
                                                  "type": "text",
                                                  "analyzer": "english",
                                                  "fields": {
                                                    "fivegrams": {
                                                      "type": "text",
                                                      "analyzer": "fivegrams"
                                                    }
                                                  }
                                                }
                                              }
                                            }
                                          },
                                          "settings": {
                                            "analysis": {
                                              "filter": {
                                                "fivegrams_filter": {
                                                  "type": "ngram",
                                                  "min_gram": 5,
                                                  "max_gram": 5
                                                }
                                              },
                                              "analyzer": {
                                                "fivegrams": {
                                                  "type": "custom",
                                                  "tokenizer": "standard",
                                                  "filter": [
                                                    "lowercase",
                                                    "fivegrams_filter"
                                                  ]
                                                }
                                              }
                                            },
                                            "number_of_shards": 1
                                          }
                                        }
                                   '''

    standard_mapping = '''{
                                      "mappings": {
                                        "csv": {
                                          "properties": {
                                            "Proposal Title:": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            },
                                            "Research Keyword 1": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            },
                                            "Research Keyword 2": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            },
                                            "Research Keyword 3": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            },
                                            "Research Keyword 4": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            },
                                            "Research Keyword 5": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            },
                                            "Benefit to Qatar:": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            },
                                            "Proposal Description:": {
                                              "type": "text",
                                              "analyzer": "standard"
                                            }
                                          }
                                        }
                                      },
                                      "settings": {
                                        "analysis": {
                                          "analyzer": "standard"
                                        },
                                        "number_of_shards": 1
                                      }
                                    }
                                   '''

    def __init__(self):
        self.es = Elasticsearch()

        self.index_name = "qnrf_standard"
        self.personnel_index = "qnrf_personnel_index"
        self.body = self.standard_mapping

        # self.index_name = "qnrf"
        # self.body = self.es_mappings_settings_no_shard

        # self.index_name = "desc2"
        # self.body = self.desc2_mapping
        #
        # self.index_name = "fivegrams"
        # self.body = self.fivegrams_mapping

        # self.index_name = "qnrf1"
        # self.index_name = "qnrf2"
        # self.index_name = "qnrf3"
        self.add_index()
        # test_delete_index()
        # test_add()

    def add_index(self):
        """
        Calls automatically for creation of elasticsearch index
        :return:
        """
        if self.es.indices.exists(index=self.index_name) and self.es.indices.exists(index=self.personnel_index):
            pass
        else:
            with open(
                    '/Users/mohammedshinoy/BitBucket/qnrf-research-visualization/Dash/Static/data/qnrf_funding_data.csv') as f:
                reader = csv.DictReader(f)
                self.es.indices.create(index=self.index_name, body=self.body)
                helpers.bulk(self.es, reader, index=self.index_name, doc_type='csv')
                self.es.indices.refresh()

            with open('/Users/mohammedshinoy/BitBucket/qnrf-research-visualization/Dash/Static/data/qnrf_funding_personnel.csv') as f:
                reader = csv.DictReader(f)
                self.es.indices.create(index=self.personnel_index)
                helpers.bulk(self.es, reader, index=self.personnel_index, doc_type='csv')
                self.es.indices.refresh()
                # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    def sample_add(self, data):
        import json
        tmp = data.to_json(orient="records")
        df_json = json.loads(tmp)
        for doc in df_json:
            self.es.index(index=self.index_name, doc_type="testtype", body=doc)

    def test_delete_index(self):
        are_you_sure = input("Are you sure you want to delete _all (Yes/No) ")
        are_you_sure = are_you_sure.lower()
        if are_you_sure.lower() == "yes" or are_you_sure.lower() == "y":
            self.es.indices.delete(index='_all')
            print("Deleted index _all")
        else:
            print("Not Deleted")

    def test_delete(self):
        pass

    def search_keywords(self, searchterm):
        client = self.es
        # multiple = MultiMatch(query='shinoy hills', fields=['name', 'address'])
        q = Q("multi_match", query=searchterm,
              fields=['Research Keyword 1', 'Research Keyword 2', 'Research Keyword 3', 'Research Keyword 4',
                      'Research Keyword 5', 'Proposal Title:'])

        # s = Search(using=client, index="csvfile").query("multi_match", name="shinoy hiba")
        s = Search(using=client, index=self.index_name).query(q)

        # .filter('term', name="cyber")

        # .filter("term", category="search") \
        # .query("match", title="shinoy")   \
        # .exclude("match", description="beta")

        # s.aggs.bucket('per_tag', 'terms', field='tags') \
        #     .metric('max_lines', 'max', field='lines')

        count = s.count()
        response = s[0:count].execute()
        print("Length of response for word {} is {}".format(searchterm, len(response)))

        print("what inside elastic keyword?")
        for hit in response:
            # print(hit.to_dict())
            # print(hit.meta)
            # print(hit)
            # print(hit.keys())
            print(hit["Proposal Number:"], hit["Proposal Title:"], hit["Research Keyword 1"], hit["Research Keyword 2"],
                  hit["Research Keyword 3"], hit["Research Keyword 4"], hit["Research Keyword 5"])
            print(hit.meta.id)
            print(hit.meta.index)
        ids = [int(hit.meta.id) for hit in response]
        return ids
        # print(hit.meta.doc_type, hit.meta.score, hit.id, hit.'Proposal Number')
        # h = response.hits[0]
        # print(h)
        # # print(h.meta)
        # # print(response)
        # print('/%s/%s/%s returned with score %f' % (
        #     h.meta.index, h.meta.doc_type, h.meta.id, h.meta.score))

        # for tag in response.aggregations.per_tag.buckets:
        #     print(tag.key, tag.max_lines.value)

    def test_search(self, search_term, must_not_term):
        """
        The search function that searches for the research topic query in the elastic search corpus
        :param search_term:
        :return:
        """
        print("must not term is", must_not_term)

        if not must_not_term:
            must_not_term = ""

        es = self.es
        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:.fourgrams", "Research Keyword 1.fourgrams",
                                                       "Research Keyword 2.fourgrams", "Research Keyword 3.fourgrams",
                                                       "Research Keyword 4.fourgrams", "Research Keyword 5.fourgrams",
                                                       "Benefit to Qatar:.fourgrams", "Proposal Description:.fourgrams"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:.fourgrams", "Research Keyword 1.fourgrams",
                                                       "Research Keyword 2.fourgrams", "Research Keyword 3.fourgrams",
                                                       "Research Keyword 4.fourgrams", "Research Keyword 5.fourgrams",
                                                       "Benefit to Qatar:.fourgrams", "Proposal Description:.fourgrams"]
                                        }
                                        }
                                    ]
                                }
                            }
                        }
                        )

        print("Got %d Hits:" % res['hits']['total'])

        number_of_results = res['hits']['total']
        ten_percent = (10 * number_of_results) / 100

        if ten_percent > 20:
            ten_percent = 20
        ten_percent = math.ceil(ten_percent)
        print("ten_percent =", ten_percent)

        sub_category_filters = []

        print(res)

        for hit in res['hits']['hits']:
            print(hit["_source"]["sub_category_1"])

        hit_list = res['hits']['hits']
        hit_list = hit_list[:ten_percent]
        for hit in hit_list:
            sub_category_filters.append(hit["_source"]["sub_category_1"])
        sub_category_filters = list(set(sub_category_filters))

        print(sub_category_filters)
        sub_category_filters_2 = sub_category_filters.copy()

        sub_category_filters.append("")
        sub_category_filters_1 = sub_category_filters.copy()

        print(sub_category_filters_1)
        print(sub_category_filters_2)

        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:.fourgrams",
                                                       "Research Keyword 1.fourgrams",
                                                       "Research Keyword 2.fourgrams",
                                                       "Research Keyword 3.fourgrams",
                                                       "Research Keyword 4.fourgrams",
                                                       "Research Keyword 5.fourgrams",
                                                       "Benefit to Qatar:.fourgrams",
                                                       "Proposal Description:.fourgrams"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:.fourgrams",
                                                       "Research Keyword 1.fourgrams",
                                                       "Research Keyword 2.fourgrams",
                                                       "Research Keyword 3.fourgrams",
                                                       "Research Keyword 4.fourgrams",
                                                       "Research Keyword 5.fourgrams",
                                                       "Benefit to Qatar:.fourgrams",
                                                       "Proposal Description:.fourgrams"]
                                        }
                                        }
                                    ],
                                    "filter": {
                                        "bool": {
                                            "should": [
                                                {"terms": {"sub_category_1.keyword": sub_category_filters_1}},
                                                {"terms": {"sub_category_2.keyword": sub_category_filters_2}}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                        )

        ids = []
        for hit in res['hits']['hits']:
            # print(hit._id)
            # print(hit.meta.doc_type, hit.meta.score, hit.topic, hit.meta.id)
            print("{id} {score} {title}".format(id=hit["_id"], score=hit["_score"],
                                                title=hit["_source"]["Proposal Title:"]))
            # ids[int(hit["_id"])]=hit["_score"]
            ids.append((int(hit["_id"]), hit["_score"]))

        # ids = [int(hit["_id"]) for hit in res['hits']['hits']]

        return ids

    def test_search_fivegrams(self, search_term, must_not_term):
        """
        The search function that searches for the research topic query in the elastic search corpus
        :param search_term:
        :return:
        """
        print("must not term is", must_not_term)

        if not must_not_term:
            must_not_term = ""

        es = self.es
        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:.fivegrams", "Research Keyword 1.fivegrams",
                                                       "Research Keyword 2.fivegrams", "Research Keyword 3.fivegrams",
                                                       "Research Keyword 4.fivegrams", "Research Keyword 5.fivegrams",
                                                       "Benefit to Qatar:.fivegrams", "Proposal Description:.fivegrams"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:.fivegrams", "Research Keyword 1.fivegrams",
                                                       "Research Keyword 2.fivegrams", "Research Keyword 3.fivegrams",
                                                       "Research Keyword 4.fivegrams", "Research Keyword 5.fivegrams",
                                                       "Benefit to Qatar:.fivegrams", "Proposal Description:.fivegrams"]
                                        }
                                        }
                                    ]
                                }
                            }
                        }
                        )

        print("Got %d Hits:" % res['hits']['total'])

        number_of_results = res['hits']['total']
        ten_percent = (10 * number_of_results) / 100

        if ten_percent > 20:
            ten_percent = 20
        ten_percent = math.ceil(ten_percent)
        print("ten_percent =", ten_percent)

        sub_category_filters = []

        print(res)

        for hit in res['hits']['hits']:
            print(hit["_source"]["sub_category_1"])

        hit_list = res['hits']['hits']
        hit_list = hit_list[:ten_percent]
        for hit in hit_list:
            sub_category_filters.append(hit["_source"]["sub_category_1"])
        sub_category_filters = list(set(sub_category_filters))

        print(sub_category_filters)
        sub_category_filters_2 = sub_category_filters.copy()

        sub_category_filters.append("")
        sub_category_filters_1 = sub_category_filters.copy()

        print(sub_category_filters_1)
        print(sub_category_filters_2)

        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:.fivegrams",
                                                       "Research Keyword 1.fivegrams",
                                                       "Research Keyword 2.fivegrams",
                                                       "Research Keyword 3.fivegrams",
                                                       "Research Keyword 4.fivegrams",
                                                       "Research Keyword 5.fivegrams",
                                                       "Benefit to Qatar:.fivegrams",
                                                       "Proposal Description:.fivegrams"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:.fivegrams",
                                                       "Research Keyword 1.fivegrams",
                                                       "Research Keyword 2.fivegrams",
                                                       "Research Keyword 3.fivegrams",
                                                       "Research Keyword 4.fivegrams",
                                                       "Research Keyword 5.fivegrams",
                                                       "Benefit to Qatar:.fivegrams",
                                                       "Proposal Description:.fivegrams"]
                                        }
                                        }
                                    ],
                                    "filter": {
                                        "bool": {
                                            "should": [
                                                {"terms": {"sub_category_1.keyword": sub_category_filters_1}},
                                                {"terms": {"sub_category_2.keyword": sub_category_filters_2}}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                        )

        ids = []
        for hit in res['hits']['hits']:
            # print(hit._id)
            # print(hit.meta.doc_type, hit.meta.score, hit.topic, hit.meta.id)
            print("{id} {score} {title}".format(id=hit["_id"], score=hit["_score"],
                                                title=hit["_source"]["Proposal Title:"]))
            # ids[int(hit["_id"])]=hit["_score"]
            ids.append((int(hit["_id"]), hit["_score"]))

        # ids = [int(hit["_id"]) for hit in res['hits']['hits']]

        return ids

    def test_search_standard(self, search_term, must_not_term):
        """
        The search function that searches for the research topic query in the elastic search corpus
        :param search_term:
        :return:
        """
        print("must not term is", must_not_term)

        if not must_not_term:
            must_not_term = ""

        es = self.es
        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:", "Research Keyword 1", "Research Keyword 2",
                                                       "Research Keyword 3", "Research Keyword 4", "Research Keyword 5",
                                                       "Benefit to Qatar:", "Proposal Description:"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:", "Research Keyword 1", "Research Keyword 2",
                                                       "Research Keyword 3", "Research Keyword 4", "Research Keyword 5",
                                                       "Benefit to Qatar:", "Proposal Description:"]
                                        }
                                        }
                                    ]
                                }
                            }
                        }
                        )

        # print("Got %d Hits:" % res['hits']['total'])


        number_of_results = res['hits']['total']
        ten_percent = (10 * number_of_results) / 100

        if ten_percent > 20:
            ten_percent = 20
        ten_percent = math.ceil(ten_percent)
        print("ten_percent =", ten_percent)

        sub_category_filters = []

        # print(res)

        # for hit in res['hits']['hits']:
        #     print(hit["_source"]["sub_category_1"])

        hit_list = res['hits']['hits']
        hit_list = hit_list[:ten_percent]
        for hit in hit_list:
            sub_category_filters.append(hit["_source"]["sub_category_1"])
        sub_category_filters = list(set(sub_category_filters))

        print(sub_category_filters)
        sub_category_filters_2 = sub_category_filters.copy()

        sub_category_filters.append("")
        sub_category_filters_1 = sub_category_filters.copy()

        print(sub_category_filters_1)
        print(sub_category_filters_2)

        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:", "Research Keyword 1", "Research Keyword 2",
                                                       "Research Keyword 3", "Research Keyword 4", "Research Keyword 5",
                                                       "Benefit to Qatar:", "Proposal Description:"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:", "Research Keyword 1", "Research Keyword 2",
                                                       "Research Keyword 3", "Research Keyword 4", "Research Keyword 5",
                                                       "Benefit to Qatar:", "Proposal Description:"]
                                        }
                                        }
                                    ],
                                    "filter": {
                                        "bool": {
                                            "should": [
                                                {"terms": {"sub_category_1.keyword": sub_category_filters_1}},
                                                {"terms": {"sub_category_2.keyword": sub_category_filters_2}}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                        )

        ids = []
        for hit in res['hits']['hits']:
            # print(hit._id)
            # print(hit.meta.doc_type, hit.meta.score, hit.topic, hit.meta.id)
            print("{id} {score} {title}".format(id=hit["_id"], score=hit["_score"],
                                                title=hit["_source"]["Proposal Title:"]))
            # ids[int(hit["_id"])]=hit["_score"]
            ids.append((int(hit["_id"]), hit["_score"]))



        # ids = [int(hit["_id"]) for hit in res['hits']['hits']]

        return ids

    def test_search_standard_perfect(self, search_term, must_not_term):
        """
        The search function that searches for the research topic query in the elastic search corpus
        :param search_term:
        :return:
        """

        print("must not term is", must_not_term)

        if not must_not_term:
            must_not_term = ""

        es = self.es
        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:", "Research Keyword 1", "Research Keyword 2",
                                                       "Research Keyword 3", "Research Keyword 4", "Research Keyword 5",
                                                       "Benefit to Qatar:", "Proposal Description:"],
                                            "operator":"and"
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:", "Research Keyword 1", "Research Keyword 2",
                                                       "Research Keyword 3", "Research Keyword 4", "Research Keyword 5",
                                                       "Benefit to Qatar:", "Proposal Description:"],
                                        }
                                        }
                                    ]
                                }
                            }
                        }
                        )

        ids = []
        for hit in res['hits']['hits']:
            # print(hit._id)
            # print(hit.meta.doc_type, hit.meta.score, hit.topic, hit.meta.id)
            print("{id} {score} {title}".format(id=hit["_id"], score=hit["_score"],
                                                title=hit["_source"]["Proposal Title:"]))
            # ids[int(hit["_id"])]=hit["_score"]
            ids.append((int(hit["_id"]), hit["_score"]))



        # ids = [int(hit["_id"]) for hit in res['hits']['hits']]

        return ids

    def test_search_desc2(self, search_term, must_not_term):
        """
        The search function that searches for the research topic query in the elastic search corpus
        :param search_term:
        :return:
        """
        print("must not term is", must_not_term)

        if not must_not_term:
            must_not_term = ""

        es = self.es
        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:.fourgrams_test",
                                                       "Research Keyword 1.fourgrams_test",
                                                       "Research Keyword 2.fourgrams_test",
                                                       "Research Keyword 3.fourgrams_test",
                                                       "Research Keyword 4.fourgrams_test",
                                                       "Research Keyword 5.fourgrams_test",
                                                       "Benefit to Qatar:.fourgrams_test",
                                                       "Proposal Description:.fourgrams_test"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:.fourgrams_test",
                                                       "Research Keyword 1.fourgrams_test",
                                                       "Research Keyword 2.fourgrams_test",
                                                       "Research Keyword 3.fourgrams_test",
                                                       "Research Keyword 4.fourgrams_test",
                                                       "Research Keyword 5.fourgrams_test",
                                                       "Benefit to Qatar:.fourgrams_test",
                                                       "Proposal Description:.fourgrams_test"]
                                        }
                                        }
                                    ]
                                }
                            }
                        }
                        )

        print("Got %d Hits:" % res['hits']['total'])

        number_of_results = res['hits']['total']
        ten_percent = (5 * number_of_results) / 100

        if ten_percent > 8:
            ten_percent = 8
        ten_percent = math.ceil(ten_percent)

        sub_category_filters = []



        for hit in res['hits']['hits']:
            print(hit["_source"]["sub_category_1"])

        print("ten_percent =", ten_percent)

        hit_list = res['hits']['hits']
        hit_list = hit_list[:ten_percent]
        for hit in hit_list:
            sub_category_filters.append(hit["_source"]["sub_category_1"])
        sub_category_filters = list(set(sub_category_filters))

        print(sub_category_filters)
        sub_category_filters_2 = sub_category_filters.copy()

        sub_category_filters.append("")
        sub_category_filters_1 = sub_category_filters.copy()

        print(sub_category_filters_1)
        print(sub_category_filters_2)

        res = es.search(index=self.index_name,
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query": search_term,
                                            "fields": ["Proposal Title:.fourgrams_test",
                                                       "Research Keyword 1.fourgrams_test",
                                                       "Research Keyword 2.fourgrams_test",
                                                       "Research Keyword 3.fourgrams_test",
                                                       "Research Keyword 4.fourgrams_test",
                                                       "Research Keyword 5.fourgrams_test",
                                                       "Benefit to Qatar:.fourgrams_test",
                                                       "Proposal Description:.fourgrams_test"]
                                        }
                                        }
                                    ],
                                    "should": [
                                        {
                                            "match": {
                                                "Proposal Title:": {
                                                    "query": search_term,
                                                    "cutoff_frequency": 10,
                                                    "boost": 3
                                                }
                                            }
                                        }
                                    ],
                                    "must_not": [
                                        {"multi_match": {
                                            "query": must_not_term,
                                            "fields": ["Proposal Title:.fourgrams_test",
                                                       "Research Keyword 1.fourgrams_test",
                                                       "Research Keyword 2.fourgrams_test",
                                                       "Research Keyword 3.fourgrams_test",
                                                       "Research Keyword 4.fourgrams_test",
                                                       "Research Keyword 5.fourgrams_test",
                                                       "Benefit to Qatar:.fourgrams_test",
                                                       "Proposal Description:.fourgrams_test"]
                                        }
                                        }
                                    ],
                                    "filter": {
                                        "bool": {
                                            "should": [
                                                {"terms": {"sub_category_1.keyword": sub_category_filters_1}},
                                                {"terms": {"sub_category_2.keyword": sub_category_filters_2}}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                        )

        ids = []
        for hit in res['hits']['hits']:
            # print(hit._id)
            # print(hit.meta.doc_type, hit.meta.score, hit.topic, hit.meta.id)
            print("{id} {score} {title}".format(id=hit["_id"], score=hit["_score"],
                                                title=hit["_source"]["Proposal Title:"]))
            # ids[int(hit["_id"])]=hit["_score"]
            ids.append((int(hit["_id"]), hit["_score"]))

        # ids = [int(hit["_id"]) for hit in res['hits']['hits']]

        return ids

    def search_professors(self, searchterm):
        client = self.es
        # multiple = MultiMatch(query='shinoy hills', fields=['name', 'address'])
        q = Q("multi_match", query=searchterm,
              fields=['Lead Investigator:', 'Personnel'],
              type='cross_fields')

        # s = Search(using=client, index="csvfile").query("multi_match", name="shinoy hiba")
        s = Search(using=client, index=self.index_name).query(q)

        # .filter('term', name="cyber")

        # .filter("term", category="search") \
        # .query("match", title="shinoy")   \
        # .exclude("match", description="beta")

        # s.aggs.bucket('per_tag', 'terms', field='tags') \
        #     .metric('max_lines', 'max', field='lines')

        response = s.execute()
        print(response)

        print("ElasticSearch Professor Results for", searchterm)

        for hit in s.scan():
            print(hit["Proposal Number:"], hit["Proposal Title:"])
            print(hit.meta.id)
            print(hit.meta.index)

        ids = [int(hit.meta.id) for hit in s.scan()]

        return ids

    def search_personnel(self, searchterm):
        client = self.es

        q = Q("multi_match", query=searchterm,
              fields=['investigator'],
              type='cross_fields')

        # s = Search(using=client, index="csvfile").query("multi_match", name="shinoy hiba")
        s = Search(using=client, index=self.personnel_index).query(q)

        print("ElasticSearch Professor Index Results for", searchterm)

        # hitlist = []
        for hit in s.scan():
            print(hit["Proposal Number:"], hit["investigator"])
            print(hit.meta.id)
            print(hit.meta.index)
            # hitlist.append({"_id": hit.meta.id, "proposal_number": hit["Proposal Number:"], "investigator": hit["investigator"]})

        ids = [int(hit.meta.id) for hit in s.scan()]

        # hitlist_dataframe = pd.DataFrame(data=hitlist)
        # # hitlist_dataframe = pd.DataFrame(data=hitlist, columns=["_id", "proposal_number", "investigator"])

        return ids
