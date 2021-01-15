from multiprocessing import Process
from crawler.mirror import crawler_mirror
from crawler.otx import crawler_otx

if __name__ == '__main__':
    process_crawler_mirror = Process(target=crawler_mirror)
    process_crawler_mirror.start()
    process_crawler_otx = Process(target=crawler_otx)
    process_crawler_otx.start()
