from elasticsearch import helpers, Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl import Q
import csv
import math
import pandas as pd
import json



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
    mapping = None
    filename = None
    es_mappings_settings = '''
              {
             "mappings": {
               "csv": {
                 "properties": {
                   "topic": {
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
                   }
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

    def __init__(self, index_name="qnrf_standard", mapping=es_mappings_settings_no_shard, filename='/Users/mohammedshinoy/BitBucket/qnrf-research-visualization/Dash/Static/data/qnrf_funding_data.csv' ):
        self.es = Elasticsearch()
        self.index_name = index_name
        self.mapping = mapping
        self.filename = filename



        self.add_index()
        # test_delete_index()
        # test_add()

    def add_index(self):
        """
        Calls automatically for creation of elasticsearch index
        :return:
        """
        if self.es.indices.exists(index=self.index_name):
            pass
        else:
            print(self.filename)
            with open(self.filename) as f:
                reader = csv.DictReader(f)
                print(self.index_name)
                print("mapping is ", self.mapping)
                self.es.indices.create(index=self.index_name, body=self.mapping)
                helpers.bulk(self.es, reader, index=self.index_name, doc_type='csv')
                self.es.indices.refresh()
                # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    def sample_add(self, data):
        import json
        tmp = data.to_json(orient="records")
        df_json = json.loads(tmp)
        for doc in df_json:
            self.es.index(index="qnrf", doc_type="testtype", body=doc)

    def test_delete_index(self):
        are_you_sure = input("Are you sure you want to delete _all (Yes/No) ")
        are_you_sure = are_you_sure.lower()
        if are_you_sure.lower() == "yes" or are_you_sure.lower() == "y":
            self.es.indices.delete(index='_all')
            print("Deleted index _all")
        else:
            print("Not Deleted")

    def test_delete(self, name):
        self.es.indices.delete(index=name)
        print("Deleted index {}".format(name))

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
        print("Length of response for word {} is {}".format(searchterm,len(response)))

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

    def test_search(self, search_term):
        es = self.es
        res = es.search(index='desc2',
                        body={
                            "size": 1000,
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query":  search_term,
                                            "fields": [ "Proposal Title:.fourgrams_test","Research Keyword 1.fourgrams_test","Research Keyword 2.fourgrams_test","Research Keyword 3.fourgrams_test","Research Keyword 4.fourgrams_test","Research Keyword 5.fourgrams_test","Benefit to Qatar:.fourgrams_test","Proposal Description:.fourgrams_test"]
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
                                    ]
                                }
                            }
                        }
                        )
        print("Got %d Hits:" % res['hits']['total'])


            # Doing multi level filtering
            # print("Stuff inside the search is")
            # print(hit["_source"]["speciality_1"], hit["_source"]["sub_category_1"], hit["_source"]["research_area_1"])

        # Get Top 10% of the search listing containing sub_category_1

        number_of_results = res['hits']['total']
        ten_percent = (10 * number_of_results) / number_of_results

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

        print (sub_category_filters)
        sub_category_filters_2 = sub_category_filters.copy()

        sub_category_filters.append("")
        sub_category_filters_1 = sub_category_filters.copy()

        print (sub_category_filters_1)
        print (sub_category_filters_2)

        # sub_category_filters_1 = json.dumps(sub_category_filters_1)
        # sub_category_filters_2 = json.dumps(sub_category_filters_2)

        res = es.search(index='desc2',
                        body={
                            "size": 1000,
                            "_source": ["Proposal Title:", "Research Keyword 1","Research Keyword 2","Research Keyword 3","Research Keyword 4","Research Keyword 5","Lead Investigator:","sub_category_1","sub_category_2"],
                            "query": {
                                "bool": {
                                    "must": [
                                        {"multi_match": {
                                            "query":  search_term,
                                            "fields": [ "Proposal Title:.fourgrams_test","Research Keyword 1.fourgrams_test","Research Keyword 2.fourgrams_test","Research Keyword 3.fourgrams_test","Research Keyword 4.fourgrams_test","Research Keyword 5.fourgrams_test","Benefit to Qatar:.fourgrams_test","Proposal Description:.fourgrams_test"]
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
                                    "filter":{
                                    	"bool":{
                                    		"should":[
                                    			{ "terms":  { "sub_category_1.keyword": sub_category_filters_1}},
                                    			{ "terms":  { "sub_category_2.keyword": sub_category_filters_2}}
                                    			]
                                    	}
                                    }
                                }
                            }
                        }
                        )
        print("Got %d Hits:" % res['hits']['total'])

        ids = []
        for hit in res['hits']['hits']:
            # print(hit._id)
            # print(hit.meta.doc_type, hit.meta.score, hit.topic, hit.meta.id)
            print("{id} {score} {title}".format(id=hit["_id"], score=hit["_score"],
                                                title=hit["_source"]["Proposal Title:"]))
            # ids[int(hit["_id"])]=hit["_score"]
            ids.append((int(hit["_id"]), hit["_score"]))

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

        # response = s.execute()
        # print(response)

        print("ElasticSearch Professor Results for", searchterm)

        for hit in s.scan():
            print(hit["Proposal Number:"], hit["Proposal Title:"])
            print(hit["Lead Investigator:"])
            print(hit["Personnel"])
            print(hit.meta.id)
            print(hit.meta.index)

        ids = [int(hit.meta.id) for hit in s.scan()]

        return ids

    def professor_processing(self, df):
        print(df.proposal_number)
        print(df.investigator.value_counts())
        return df

    def search_personnel(self, searchterm, index="qnrf_personnel_index"):
        client = self.es

        q = Q("multi_match", query=searchterm,
              fields=['investigator'],
              type='cross_fields')

        # s = Search(using=client, index="csvfile").query("multi_match", name="shinoy hiba")
        s = Search(using=client, index=index).query(q)

        print("ElasticSearch Professor Results for", searchterm)

        hitlist = []

        for hit in s.scan():
            print(hit["Proposal Number:"], hit["investigator"])
            print(hit.meta.id)
            print(hit.meta.index)
            hitlist.append({"_id": hit.meta.id, "proposal_number": hit["Proposal Number:"], "investigator": hit["investigator"]})

        ids = [int(hit.meta.id) for hit in s.scan()]

        hitlist_dataframe = pd.DataFrame(data=hitlist)
        # hitlist_dataframe = pd.DataFrame(data=hitlist, columns=["_id", "proposal_number", "investigator"])

        self.professor_processing(hitlist_dataframe)

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


# Standard
index1 = "qnrf1"
mapping1 ='''{
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
                    }
                  }
                }
              },
              "settings": {
                "analysis": {
                  "analyzer": "standard"
                }
              }
            }
           '''

# 10 n grams
index2="qnrf2"
mapping2 = '''{
              "mappings": {
                "csv": {
                  "properties": {
                    "Proposal Title:": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigrams": {
                          "type": "text",
                          "analyzer": "multigrams"
                        }
                      }
                    },
                    "Research Keyword 1": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigrams": {
                          "type": "text",
                          "analyzer": "multigrams"
                        }
                      }
                    },
                    "Research Keyword 2": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigrams": {
                          "type": "text",
                          "analyzer": "multigrams"
                        }
                      }
                    },
                    "Research Keyword 3": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigrams": {
                          "type": "text",
                          "analyzer": "multigrams"
                        }
                      }
                    },
                    "Research Keyword 4": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigrams": {
                          "type": "text",
                          "analyzer": "multigrams"
                        }
                      }
                    },
                    "Research Keyword 5": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigrams": {
                          "type": "text",
                          "analyzer": "multigrams"
                        }
                      }
                    }
                  }
                }
              },
              "settings": {
                "analysis": {
                  "filter": {
                    "multigrams_filter": {
                      "type": "ngram",
                      "min_gram": 4,
                      "max_gram": 10
                    }
                  },
                  "analyzer": {
                    "multigrams": {
                      "type": "custom",
                      "tokenizer": "standard",
                      "filter": [
                        "lowercase",
                        "multigrams_filter"
                      ]
                    }
                  }
                }
              }
            }
           '''

# basic fourgram
index3="qnrf3"
mapping3 = '''{
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
                   }
                 }
               }
           '''



# basic test
test1="test1"
mapping_test_1 = '''
                {
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
                        }
                      }
                    }
                  },
                  "settings": {
                    "analysis": {
                      "analyzer": "standard"
                    },
                    "number_of_shards":1
                  }
                }
           '''

# fourgram test
test2="test2"
mapping_test_2 = '''
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

# multigram 5-10 test
test3="test3"
mapping_test_3 = '''
            {
              "mappings": {
                "csv": {
                  "properties": {
                    "Proposal Title:": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigram_test": {
                          "type": "text",
                          "analyzer": "multigram_test"
                        }
                      }
                    },
                    "Research Keyword 1": {
                      "type": "text",
                      "analyzer": "english",
                      "fields": {
                        "multigram_test": {
                          "type": "text",
                          "analyzer": "multigram_test"
                        }
                      }
                    }
                  }
                }
              },
              "settings": {
                "analysis": {
                  "filter": {
                    "multigram_test_filter": {
                      "type": "ngram",
                      "min_gram": 4,
                      "max_gram": 10
                    }
                  },
                  "analyzer": {
                    "multigram_test": {
                      "type": "custom",
                      "tokenizer": "standard",
                      "filter": [
                        "lowercase",
                        "multigram_test_filter"
                      ]
                    }
                  }
                },
                "number_of_shards": 1
              }
            }
           '''



######## Trial of original file ################

# elastic_dash1 = ElasticDash(index1, mapping1)
# elastic_dash2 = ElasticDash(index2, mapping2)
# elastic_dash3 = ElasticDash(index3, mapping3)

#
# elastic_dash1.test_delete(index1)
# elastic_dash1.test_delete(index2)
# elastic_dash1.test_delete(index3)



#############################################
#############################################
######## Trial of test file ################


# elastic_dash_test1 = ElasticDash(test1, mapping_test_1, "testfile.csv")
# elastic_dash_test2 = ElasticDash(test2, mapping_test_2, "testfile.csv")
# elastic_dash_test3 = ElasticDash(test3, mapping_test_3, "testfile.csv")


# elastic_dash_test1.test_delete(test1)
# elastic_dash_test1.test_delete(test2)
# elastic_dash_test1.test_delete(test3)




# Elastic Dash 1

# elastic_dash1.test_search("cyber security")



################## TRAILS AFTER USING ALL THE COLUMNS #######################
##########################################################################################
##########################################################################################
##########################################################################################


# basic test
using_description_1="desc1"
# mapping_using_description_1 = '''{
#                                   "mappings": {
#                                     "csv": {
#                                       "properties": {
#                                         "Proposal Title:": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         },
#                                         "Research Keyword 1": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         },
#                                         "Research Keyword 2": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         },
#                                         "Research Keyword 3": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         },
#                                         "Research Keyword 4": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         },
#                                         "Research Keyword 5": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         },
#                                         "Benefit to Qatar:": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         },
#                                         "Proposal Description:": {
#                                           "type": "text",
#                                           "analyzer": "standard"
#                                         }
#                                       }
#                                     }
#                                   },
#                                   "settings": {
#                                     "analysis": {
#                                       "analyzer": "standard"
#                                     },
#                                     "number_of_shards": 1
#                                   }
#                                 }
#                                '''
#
# using_description_2="desc2"
# mapping_using_description_2 = '''
#                                  {
#                                   "mappings": {
#                                     "csv": {
#                                       "properties": {
#                                         "Proposal Title:": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         },
#                                         "Research Keyword 1": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         },
#                                         "Research Keyword 2": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         },
#                                         "Research Keyword 3": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         },
#                                         "Research Keyword 4": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         },
#                                         "Research Keyword 5": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         },
#                                         "Benefit to Qatar:": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         },
#                                         "Proposal Description:": {
#                                           "type": "text",
#                                           "analyzer": "english",
#                                           "fields": {
#                                             "fourgrams_test": {
#                                               "type": "text",
#                                               "analyzer": "fourgrams_test"
#                                             }
#                                           }
#                                         }
#                                       }
#                                     }
#                                   },
#                                   "settings": {
#                                     "analysis": {
#                                       "filter": {
#                                         "fourgrams_test_filter": {
#                                           "type": "ngram",
#                                           "min_gram": 4,
#                                           "max_gram": 4
#                                         }
#                                       },
#                                       "analyzer": {
#                                         "fourgrams_test": {
#                                           "type": "custom",
#                                           "tokenizer": "standard",
#                                           "filter": [
#                                             "lowercase",
#                                             "fourgrams_test_filter"
#                                           ]
#                                         }
#                                       }
#                                     },
#                                     "number_of_shards": 1
#                                   }
#                                 }
#                            '''






# elastic_dash1 = ElasticDash(using_description_1, mapping_using_description_1)
# elastic_dash2 = ElasticDash(using_description_2, mapping_using_description_2)


# elastic_dash2 = ElasticDash(index2, mapping2)
# elastic_dash3 = ElasticDash(index3, mapping3)


# Elastic Dash 1

# elastic_dash2.test_search("cyber security")



# Testing out professor search with aggregations

elastic_dash_professor = ElasticDash()
elastic_dash_professor.search_personnel("Noora")