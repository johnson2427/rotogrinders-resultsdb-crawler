# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# from pymongo import MongoClient
import logging
from pymongo import MongoClient


class MongodbPipeline(object):

    def __init__(self):
        # self.mongo_uri = 'mongodb://localhost:27017'
        self.mongo_uri = 'mongodb://blake-G750JM:27017'
        self.mongo_db = 'DraftKings_Contests'

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        result = dict(item)
        keys = []
        for key in result.keys():
            keys.append(key)
        if len(keys[0].split('-')) == 3:
            collection_name = 'date_{key}'.format(key=keys[0])
            for i, entry in enumerate(result[keys[0]]):
                entry_doc_name = 'slate_' + entry['_id']
                entry['_id'] = entry_doc_name
                self.db[collection_name].insert_one(entry)
        elif len(keys[0].split('-')) == 5:
            collection_name = 'date_{key}'.format(key=keys[0])
            result['_id'] = keys[0]
            self.db[collection_name].insert_one(result[keys[0]])
        else:
            collection_name = 'contest_{contest_id}'.format(contest_id=result['contest_info']['contest_id'])
            entry = result['contest_info']
            contest_details = {
                '_id': 'contest_details',
                'contest_name': entry['contest_name'],
                'contest_id': entry['contest_id'],
                'number_of_games': entry['num_of_games'],
                'max_entries': entry['max_entries'],
                'entry_fee': entry['entry_fee'],
                'total_entries': entry['total_entries'],
                "sport#": entry["sport#"],
                'date_time': entry['date_time'],
                'complete': entry['complete'],
                'prize_pool': entry['prize_pool'],
                'top_prize': entry['top_prize'],
                'cash_line': entry['cash_line'],
                'winning_score': entry['winning_score']
            }
            self.db[collection_name].insert_one(contest_details)

            entry = result['payout_structure'][0]
            winning_chart = {
                '_id': 'winning_chart',
                'chart': entry['prizes']
            }
            self.db[collection_name].insert_one(winning_chart)

            entry = result['player_ownership'][0]
            player_ownership = {
                '_id': 'player_ownership',
                'ownership': entry['playerOwnership']
            }
            self.db[collection_name].insert_one(player_ownership)

            for i, entry in enumerate(result['contest_standings']['entries']):
                entry_doc_name = 'entry_' + str(i)
                entry['_id'] = entry_doc_name
                self.db[collection_name].insert_one(entry)
        return item
