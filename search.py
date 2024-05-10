# search.py

from elasticsearch import Elasticsearch
from config import ELASTICSEARCH_HOST, ELASTICSEARCH_PORT

def create_es_connection():
    es = Elasticsearch([{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT}])
    if not es.ping():
        print("Не удалось подключиться к Elasticsearch")
    return es

# Пример использования
# es = create_es_connection()
# if es is not None:
#     # Взаимодействие с Elasticsearch


def search_by_name(es, name):
    # body = {
    #     "query": {
    #         "bool": {
    #             "should": [
    #                 {"match_phrase": {"name": name}},  # Точный поиск
    #                 {"wildcard": {"name": f"{name}*"}}  # Поиск с подстановочным символом
    #             ],
    #             "minimum_should_match": 1  # Указывает, что должно совпадать хотя бы одно условие из 'should'
    #         }
    #     }
    # }
    name = name.split()
    should_clauses = [{"wildcard": {"name": part}} for part in name]

    body = {
        "query": {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 3
            }
        }
    }
    res_1 = es.search(index="udmega", body=body)
    res_2 = es.search(index="udoshka", body=body)
    res_3 = es.search(index="udbee", body=body)

    ids_1 = [res['_id'] for res in res_1['hits']['hits']]
    ids_2 = [res['_id'] for res in res_2['hits']['hits']]
    ids_3 = [res['_id'] for res in res_3['hits']['hits']]
    # return es.search(index="udmega,udoshka,udbee", body=body)
    # return es.search(index="udmega", body=body)
    return [ids_1, ids_2, ids_3]


def search_by_phone(es, phone):
    body = {
        "query": {
            "match": {
                "phone": phone  # замените 'phone_field' на название поля в индексе
            }
        }
    }
    if phone.startswith('99677') or phone.startswith('99622'):
        return es.search(index='udbee', body=body)
    elif phone.startswith('99655') or phone.startswith('99699'):
        return es.search(index="udmega", body=body)
    elif phone.startswith('99650') or phone.startswith('99670'):
        return es.search(index='udoshka', body=body)
    else:
        return []
