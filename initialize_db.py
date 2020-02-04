from DiseasePedia.netease import NetEaseHealthScraper


if __name__ == "__main__":
    scraper = NetEaseHealthScraper()
    scraper.db.flush()
    scraper.work_by_chain()
