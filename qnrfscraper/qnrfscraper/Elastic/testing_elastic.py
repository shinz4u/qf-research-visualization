from elasticsearch import helpers, Elasticsearch
from elasticsearch_dsl import Search, analyzer, tokenizer, Index
from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl import Q
from elasticsearch_dsl.field import Text


import csv


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
#     es = Elasticsearch()
#
#     # here your result dict with data from source
#
#     r = helpers.bulk(client=es, actions=(indexing(c) for c in result))
#     es.indices.refresh()

from elasticsearch_dsl import connections



def test_add(file_name, index_name):
    mapping = '''
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

    with open(file_name) as f:
        reader = csv.DictReader(f)
        es.indices.create(index=index_name, body=mapping)
        helpers.bulk(es, reader, index=index_name, doc_type='csv')
        es.indices.refresh()
        # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')


def define_index():
    pass


def change_analyzer():
    # my_analyzer = analyzer('simple',
    #                        tokenizer=tokenizer('trigram', 'nGram', min_gram=3, max_gram=3),
    #                        filter=['lowercase']
    #                        )

    # name = Text(analyzer='simple')
    # es.indices.refresh()



    i = Index('testfile')
    # print(i.get_settings())
    i.close()
    # i.analyzer('simple')
    # i.open()
    #
    # name = Text(analyzer='simple')
    # my_analyzer = analyzer('simple')
    # i.analyzer(my_analyzer)
    # i.open()

    es.indices.put_settings(index='testfile',
                            body={
                                    "analysis": {
                                        "analyzer": "simple"
                                    }
                                }
                            )

    i.open()



def test_delete_all():
    are_you_sure = input("Are you sure you want to delete _all (Yes/No) ")
    are_you_sure = are_you_sure.lower()
    if are_you_sure.lower() == "yes" or are_you_sure.lower() == "y":
        es.indices.delete(index='_all')
        print("Deleted index _all")
    else:
        print("Not Deleted")


def test_delete(index):
    are_you_sure = input("Are you sure you want to delete {} (Yes/No) ".format(index))
    are_you_sure = are_you_sure.lower()
    if are_you_sure.lower() == "yes" or are_you_sure.lower() == "y":
        es.indices.delete(index=index)
        print("Deleted index {}".format(index))
    else:
        print("Not Deleted")



def test_search(index_to_search, search_term, field_list):
    es = Elasticsearch()
    res = es.search(index=index_to_search,
                    body={
                          "size": 20,
                          "query": {
                            "bool": {
                                "must": [
                                    { "match": { "topic.fourgrams": search_term}
                                    }
                              ],
                              "should": [
                                {
                                  "match": {
                                    "topic": {
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
    for hit in res['hits']['hits']:
        # print(hit._id)
        # print(hit.meta.doc_type, hit.meta.score, hit.topic, hit.meta.id)
        print("{id} {score} {topic}" .format(id=hit["_id"], score=hit["_score"], topic=hit["_source"]["topic"]))

def test_search_2(index_to_search, search_term, field_list):

    client = Elasticsearch()

    test_body = """ {
                        "bool": {
                            "must": [
                                { "match": { "topic.fourgrams":%s }
                                }
                          ],
                          "should": [
                            {
                              "match": {
                                "topic": {
                                  "query": %s,
                                  "cutoff_frequency": 10,
                                  "boost": 3
                                }
                              }
                            }
                          ]
                        }
                      }
    """ % (search_term, search_term)
    # print(test_body)

    test_body = '{"bool":{"must":[{"match":{"topic.fourgrams":"cyber"}}],"should":[{"match":{"topic":{"query":"cyber security","cutoff_frequency":10,"boost":3}}}]}}'
    print(test_body)

    # multiple = MultiMatch(query='shinoy hills', fields=['name', 'address'])
    q = Q("multi_match", query=search_term,
          fields=field_list,
          operator='or',
          type='cross_fields')

    # s.query = Bool(should=[MultiMatch(query='albert', operator='or', boost=3,
    #                                   fields=["title^4", "content^3", "interest^1", "subtitle^2"])
    #                        ])


    # q = Q("multi_match", query='python django', fields=['title', 'body'])
    # q = Q('bool', must=[Q('match', title='python'), Q('match', body='best')])

    # q = Q('bool', must=[Q('match', topic='cyber')])
    # q = Q('bool', must=[Q('match', topic='cyber')], should=[Q('match', topic='cyber security')])
    q = Q('bool', must=[Q('match', topic='cyber')], should=[Q('match', topic='{"query":"cyber security" ,"cutoff_frequency": 10,"boost": 3}')])





    # must = [Q('match', topic={"fourgrams":"cyber security")]

    # "topic": {
    #     "type": "text",
    #     "fields": {
    #         "fourgrams": {
    #             "type": "text",
    #             "analyzer": "fourgrams"
    #         }
    #     },
    #     "analyzer": "english"
    # }


    # {"multi_match": {"query": "python django", "fields": ["title", "body"]}}
    demo=MultiMatch(query='python django', fields=['title', 'body'])

    # {"match": {"title": {"query": "web framework", "type": "phrase"}}}
    demo=Match(title={"query": "web framework", "type": "phrase"})


    print(q)

    # s = Search(using=client, index="csvfile").query("multi_match", name="shinoy hiba")
    s = Search(using=client, index=index_to_search).query(test_body)
        # .filter('term', name="cyber")
    # .filter('term', name="food")
    # .exclude("match", description="beta")

    # .filter("term", category="search") \
    # .query("match", title="shinoy")   \
    # .exclude("match", description="beta")

    # s.aggs.bucket('per_tag', 'terms', field='tags') \
    #     .metric('max_lines', 'max', field='lines')

    # s[0:count].execute()
    count = s.count()
    response = s[0:count].execute()

    print("Length of response is ",len(response))


    for hit in response:
        print(hit.meta.doc_type, hit.meta.score, hit.topic,hit.meta.id)
    # h = response.hits[0]
    # print(h)
    # # print(h.meta)
    # # print(response)
    # print('/%s/%s/%s returned with score %f' % (
    #     h.meta.index, h.meta.doc_type, h.meta.id, h.meta.score))

    # for tag in response.aggregations.per_tag.buckets:
    #     print(tag.key, tag.max_lines.value)

def test_add_qnrf_sample():

    mapping = '''
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
            }
          }
        }
    '''
    with open('/Users/mohammedshinoy/BitBucket/qnrf-research-visualization/Dash/Static/data/sample_qnrf_funding_data.csv') as f:
        reader = csv.DictReader(f)
        # es.indices.create(index='qnrf_sample', doc_type='csv', body=mapping)
        helpers.bulk(es, reader, index='qnrf_sample', doc_type='csv', body=mapping)
        es.indices.refresh()
        # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

def test_search_qnrf(searchterm = "cyber security"):
    client = Elasticsearch()
    # multiple = MultiMatch(query='shinoy hills', fields=['name', 'address'])
    q = Q("multi_match", query=searchterm,
          fields=['Research Keyword 1', 'Research Keyword 2', 'Research Keyword 3', 'Research Keyword 4',
                  'Research Keyword 5', 'Proposal Title:'])

    # s = Search(using=client, index="csvfile").query("multi_match", name="shinoy hiba")
    s = Search(using=client, index="qnrf").query(q)

        # .filter('term', name="cyber")

    # .filter("term", category="search") \
    # .query("match", title="shinoy")   \
    # .exclude("match", description="beta")

    # s.aggs.bucket('per_tag', 'terms', field='tags') \
    #     .metric('max_lines', 'max', field='lines')

    response = s.execute()

    print("what?")
    for hit in response:
        # print(hit.to_dict())
        # print(hit.meta)
        # print(hit)
        # print(hit.keys())
        print(hit["Proposal Number:"],hit["Proposal Title:"],hit["Research Keyword 1"], hit["Research Keyword 2"], hit["Research Keyword 3"], hit["Research Keyword 4"], hit["Research Keyword 5"])
        print(hit.meta.id)
        print(hit.meta.index)
    ids = [int(hit.meta.id) for hit in response]
    print(ids)

        # print(hit.meta.doc_type, hit.meta.score, hit.id, hit.'Proposal Number')
    # h = response.hits[0]
    # print(h)
    # # print(h.meta)
    # # print(response)
    # print('/%s/%s/%s returned with score %f' % (
    #     h.meta.index, h.meta.doc_type, h.meta.id, h.meta.score))

    # for tag in response.aggregations.per_tag.buckets:
    #     print(tag.key, tag.max_lines.value)


connections.create_connection(hosts=['localhost'], timeout=20)
es = Elasticsearch()



# ADDING
# test_add('test_csv.csv','csvfile')
# test_add('test_2.csv','testfile')


# SEARCHING


# CSVFILE
# test_search('csvfile','cyber security',['topic','address','url'])
# change_analyzer()



# TESTFILE
test_search('testfile','cyber',['topic'])


# test_search_qnrf("cyber")
# test_add_qnrf_sample()
# testing()



# DELETING
# test_delete_all()
# test_delete('csvfile')
# test_delete('testfile')

