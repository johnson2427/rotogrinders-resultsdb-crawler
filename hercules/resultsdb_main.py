from scrapy import cmdline


def pull_resultsdb():
    cmdline.execute("scrapy crawl results_selenium".split())


if __name__ == '__main__':
    pull_resultsdb()