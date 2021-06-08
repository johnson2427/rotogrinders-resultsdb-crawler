# -*- coding: utf-8 -*-
import scrapy
from selenium.common import exceptions
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import pandas as pd
from datetime import datetime
import requests
import json
from pytz import timezone
import config


def timezone_conversion(scrape_date):
    contest_start_date = datetime.strptime(scrape_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    eastern = timezone('US/Eastern')
    gmt0 = timezone('Etc/GMT-0')
    contest_start_date_gmt0 = gmt0.localize(contest_start_date)
    contest_start_date_eastern = contest_start_date_gmt0.astimezone(eastern)
    converted_time = contest_start_date_eastern.strftime('%Y-%m-%d_%H:%M')
    return converted_time


class ResultsSpiderSelenium(scrapy.Spider):
    name = 'results_selenium'
    allowed_domains = ['www.rotogrinders.com/resultsdb/']
    start_urls = ['https://rotogrinders.com/resultsdb/site/draftkings/date/2021-04-01/sport/mlb/']

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_path = "/" + os.getcwd().split('/')[1] + "/" + os.getcwd().split('/')[2] + "/anaconda3/bin/chromedriver"
        self.driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
        self.dates = [d.strftime('%Y-%m-%d') for d in pd.date_range(config.RESULTS_DATES, config.RESULTS_DATES)]
        self.headers = {
            'authority': 'resultsdb-api.rotogrinders.com',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
            'accept': '*/*',
            'origin': 'https://rotogrinders.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://rotogrinders.com/',
            'accept-language': 'en-US,en;q=0.9',
            'if-none-match': 'W/"14eb-f+5kYuiovGuHE44nzD2RYko/Maw"',
        }
        self.sport = 2

    def get_slate(self, resp):
        return resp.xpath('//*[@id="root"]/main/div[3]/div[2]/h2/text()').get()

    def contest_information(self, contest_key, date_and_time, num_of_games, resp):
        return {
                'contest_name': resp.xpath('//tr[@data-row-key="{key}"]/td[1]/a'
                                           '/text()'.format(key=contest_key)).get(),
                'contest_id': contest_key,
                'num_of_games': num_of_games,
                'max_entries': resp.xpath('//div[2]/div/div/div/div/div/table/tbody/tr[@data-row-key="{key}"]'
                                          '/td[6]/text()'.format(key=contest_key)).get(),
                'entry_fee': resp.xpath('//div[2]/div/div/div/div/div/table/tbody/tr[@data-row-key="{key}"]'
                                        '/td[4]/text()'.format(key=contest_key)).get(),
                'total_entries': resp.xpath('//div[2]/div/div/div/div/div/table/tbody/tr[@data-row-key="{key}"]'
                                            '/td[7]/text()'.format(key=contest_key)).get(),
                'sport#': self.sport,
                'date_time': date_and_time,
                'complete': 'complete',
                'prize_pool': resp.xpath('//div[2]/div/div/div/div/div/table/tbody/tr[@data-row-key="{key}"]'
                                         '/td[3]/text()'.format(key=contest_key)).get(),
                'top_prize': resp.xpath('//div[2]/div/div/div/div/div/table/tbody/tr[@data-row-key="{key}"]'
                                        '/td[5]/text()'.format(key=contest_key)).get(),
                'cash_line': resp.xpath('//div[2]/div/div/div/div/div/table/tbody/tr[@data-row-key="{key}"]'
                                        '/td[8]/text()'.format(key=contest_key)).get(),
                'winning_score': resp.xpath('//div[2]/div/div/div/div/div/table/tbody/tr[@data-row-key="{key}"]'
                                            '/td[10]/text()'.format(key=contest_key)).get()
            }

    def standings_information(self, contest_key, index):
        params = (
            ('_contestId', contest_key),
            ('index', index),
        )
        response = requests.get('https://resultsdb-api.rotogrinders.com/api/entries', headers=self.headers, params=params)
        resp_content = response.content
        return json.loads(resp_content)

    def paginated_standings_information(self, contest_key):
        i = 0
        standings = self.standings_information(contest_key=contest_key, index=i)
        if 'prize' in standings['entries'][-1].keys():
            while standings['entries'][-1] != 'Anonymous':
                i = i + 1
                paginated_standings = self.standings_information(contest_key, i)
                paginated_standings = paginated_standings['entries']
                if not paginated_standings:
                    return standings
                for j in range(len(paginated_standings)):
                    standings['entries'].append(paginated_standings[j])
                    if i > 800:
                        return standings
                    if 'prize' not in paginated_standings[j].keys():
                        return standings
        else:
            return standings

    def ownership_information(self, contest_id):
        params = (
            ('_id', contest_id),
            ('ownership', 'true'),
        )

        response = requests.get('https://resultsdb-api.rotogrinders.com/api/contests', headers=self.headers, params=params)
        resp_content = response.content
        return json.loads(resp_content)

    def list_slates(self):
        self.driver.find_element_by_xpath('//*[@id="root"]/main/div[1]/div[3]/div[3]/div[2]/div/div/div').click()
        html_slates = self.driver.page_source
        resp_slates = Selector(text=html_slates)
        dropdown_list = resp_slates.xpath('//*[@id]/ul/li/text()').extract()
        slate_list = []
        for i in range(len(dropdown_list)):
            try:
                if dropdown_list[i].split(' ')[3] == 'Classic' or dropdown_list[i].split(' ')[3] == 'Showdown':
                    slate_list.append(dropdown_list[i])
            except IndexError:
                pass
        self.driver.find_element_by_xpath('//*[@id="root"]/main/div[1]/div[3]/div[3]/div[2]/div/div/div').click()
        return slate_list

    def payout_data(self, resp):
        params = (
            ('slates', self.get_slate_id(resp)),
            ('lean', 'true'),
        )

        response = requests.get('https://resultsdb-api.rotogrinders.com/api/contests', headers=self.headers, params=params)
        resp_content = response.content
        return json.loads(resp_content)

    def get_slate_id(self, resp):
        url_xpath = '//*[@id="root"]/main/div[3]/div[2]/div/div[3]/div[2]/div/div/div/div/div/div/table/tbody/tr[1]/td[1]/a[@href]'
        url_string = resp.xpath(url_xpath).get()
        return url_string.split('/')[9]

    def parse(self, response):
        for date in self.dates:
            self.driver.get('https://rotogrinders.com/resultsdb/site/draftkings/date/{date}/sport/mlb/'.format(date=date))
            time.sleep(3)
            for i, slate in enumerate(self.list_slates()):
                self.driver.find_element_by_xpath('//*[@id="root"]/main/div[1]/div[3]/div[3]/div[2]/div/div/div').click()
                time.sleep(1)
                self.driver.find_element_by_xpath("//*[@id]/ul/li[contains(text(), '{slate}')]".format(slate=slate)).click()
                time.sleep(3)
                try:
                    self.driver.find_element_by_xpath('//main/div[3]/div[2]/div/div[1]/div'
                                                      '/div/div/div/div/div[@role= "tab"][2]').click()
                    time.sleep(3)
                except exceptions.ElementClickInterceptedException:
                    self.driver.refresh()
                    time.sleep(10)
                    self.driver.find_element_by_xpath('//main/div[3]/div[2]/div/div[1]/div'
                                                      '/div/div/div/div/div[@role= "tab"][2]').click()
                html = self.driver.page_source
                resp = Selector(text=html)
                slate_info = self.get_slate(resp)
                payout_data = self.payout_data(resp)
                date_and_time = date + ' ' + slate_info.split(' ')[0] + ' ' + slate_info.split(' ')[1]
                num_games = slate_info.split(' ')[5]
                date_time_obj = datetime.strptime(date_and_time, '%Y-%m-%d %I:%M %p')
                date_time = date_time_obj.strftime('%Y-%m-%d_%H:%M')
                for contest_key in resp.xpath('//@data-row-key'):
                    contest_key = contest_key.get()
                    contest_pay = []
                    for payout in payout_data:
                        if payout['_id'] == contest_key:
                            contest_pay.append(payout)
                    if len(contest_key) > 3:
                        contest_url = self.driver.find_element_by_xpath('//tr[@data-row-key="{key}"]/td[1]'
                                                                        '/a'.format(key=contest_key)).get_attribute('href')
                        self.driver.get(contest_url)
                        time.sleep(3)
                        html_contest = self.driver.page_source
                        resp_contest = Selector(text=html_contest)
                        try:
                            user = resp_contest.xpath('//div[1]/div/div[1]/div[2]/div/div/div/div/div/table/thead/tr/'
                                                      'th[2]/span/div/span[1]/text()').get()
                        except exceptions.ElementClickInterceptedException:
                            self.driver.refresh()
                            time.sleep(3)
                        yield {
                            'contest_info': self.contest_information(contest_key, date_and_time=date_time, num_of_games=num_games, resp=resp),
                            'contest_standings': self.paginated_standings_information(contest_key),
                            'player_ownership': self.ownership_information(contest_key),
                            'payout_structure': contest_pay
                        }
                        self.driver.find_element_by_xpath('//*[@id="root"]/main/div[3]/div[1]/span[2]/span[1]/a').click()
                        time.sleep(3)
                        try:
                            contests_input = self.driver.find_element_by_xpath('//main/div[3]/div[2]/div/div[1]/div/div/'
                                                                               'div/div/div/div[@role= "tab"][2]')
                            contests_input.click()
                        except exceptions.NoSuchElementException:
                            self.driver.refresh()
                            time.sleep(10)
                            contests_input = self.driver.find_element_by_xpath('//main/div[3]/div[2]/div/div[1]/div/div/'
                                                                               'div/div/div/div[@role= "tab"][2]')
                            contests_input.click()
