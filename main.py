from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from hercules.spiders.results_selenium import ResultsSpiderSelenium


process = CrawlerProcess(get_project_settings())
process.crawl(ResultsSpiderSelenium)
process.start()
