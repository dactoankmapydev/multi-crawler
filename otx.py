import json
import math
from datetime import datetime

import pika
import requests
import pytz
from crawler import helper

OTX_API_KEY = "779cc51038ddb07c5f6abe0832fed858a6039b9e8cdb167d3191938c1391dbba"

headers = {
    "X-OTX-API-KEY": OTX_API_KEY
}

proxies = {
    "http": "http://127.0.0.1:3131",
    "https": "http://127.0.0.1:3131",
}


def send_indicator(channel, message):
    channel.basic_publish(exchange="",
                          routing_key="ioc_collect_queue",
                          body=json.dumps(message),
                          properties=pika.BasicProperties(priority=5))
    print("Sent %r" % message)


def get_total_page_otx():
    results = requests.get("https://otx.alienvault.com/api/v1/pulses/subscribed", headers=headers,
                           proxies=proxies).json()
    total_page = math.ceil(results["count"] / 50)
    return total_page


def crawler_otx():
    connection, channel = helper.setup("ioc_collect_queue")
    ist = pytz.timezone("Asia/Ho_Chi_Minh")
    try:
        total_page = get_total_page_otx()

        sample = {"sample": ["FileHash-MD5", "FileHash-PEHASH", "FileHash-SHA256", "FileHash-IMPHASH", "FileHash-MD5"]}
        url = {"url": ["URL", "URI"]}
        domain = {"domain": ["hostname", "domain"]}
        ipaddress = {"ipaddress": ["IPv6", "IPv4", "BitcoinAddress"]}

        for page in range(1, total_page + 1):
            data = requests.get("https://otx.alienvault.com/api/v1/pulses/subscribed?limit=50&page={}".format(page),
                                headers=headers, proxies=proxies).json()
            for item in data["results"]:
                category = item["tags"]
                for value in item["indicators"]:
                    ioc_id = value["id"]
                    ioc = value["indicator"]
                    created_time = value["created"]
                    ioc_type = value["type"]

                    if ioc_type in sample["sample"]:
                        ioc_type = "sample"
                    if ioc_type in url["url"]:
                        ioc_type = "url"
                    if ioc_type in domain["domain"]:
                        ioc_type = "domain"
                    if ioc_type in ipaddress["ipaddress"]:
                        ioc_type = "ipaddress"

                    indicator = {
                        "ioc_id": ioc_id,
                        "ioc": ioc,
                        "ioc_type": ioc_type,
                        "created_time": created_time,
                        "crawled_time": datetime.now(ist).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                        "source": "otx-alienvault",
                        "category": category
                    }
                    send_indicator(channel, indicator)
        connection.close()
    except Exception as e:
        print('crawler otx-alienvault failed. See exception:')
        print(e)
