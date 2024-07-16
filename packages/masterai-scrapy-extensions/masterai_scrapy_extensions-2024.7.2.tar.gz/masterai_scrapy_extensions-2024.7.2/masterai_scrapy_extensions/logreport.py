# -*- coding:utf-8 -*-
import logging
import os
from datetime import datetime

import requests
from scrapy import signals
from scrapy.exceptions import NotConfigured
from twisted.internet import task

logger = logging.getLogger(__name__)


class ReportStats:
    def __init__(self, stats, interval=60.0):
        self.stats = stats
        self.interval = interval
        self.multiplier = 60.0 / self.interval
        self.task = None
        self.task_id = 0
        self.pod_name = ""
        self.report_url = ""

    @classmethod
    def from_crawler(cls, crawler):
        task_id = os.getenv("CMS_TASK_ID")
        if not task_id:
            raise NotConfigured
        pod_name = os.getenv("POD_NAME")
        if not pod_name:
            raise NotConfigured
        interval = crawler.settings.getfloat("LOGSTATS_INTERVAL", 60.0)
        report_url = crawler.settings.get("LOGREPORT_URL")
        if not report_url:
            raise NotConfigured

        o = cls(crawler.stats, interval)
        o.task_id = task_id
        o.pod_name = pod_name
        o.report_url = report_url
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(o.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(o.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(o.response_received, signal=signals.response_received)
        return o

    def log(self, spider):
        items = self.stats.get_value("item_scraped_count", 0)
        pages = self.stats.get_value("response_received_count", 0)

        items_add = items - self.itemsprev
        pages_add = pages - self.pagesprev
        self.stats.inc_value("item_scraped_add_count", items_add, spider=spider)
        self.stats.inc_value("response_received_add_count", pages_add, spider=spider)

        irate = items_add * self.multiplier
        prate = pages_add * self.multiplier
        self.pagesprev, self.itemsprev = pages, items

        crawl_detail = {}
        for key in self.stats.get_stats(spider=spider):
            if key.startswith("downloader"):
                crawl_detail[key] = self.stats.get_value(key, 0)
            elif key.startswith("item_scraped"):
                crawl_detail[key] = self.stats.get_value(key, 0)
            elif key.startswith("item_dropped"):
                crawl_detail[key] = self.stats.get_value(key, 0)
            elif key.startswith("response_received"):
                crawl_detail[key] = self.stats.get_value(key, 0)
            elif key.startswith("scheduler"):
                crawl_detail[key] = self.stats.get_value(key, 0)
            elif key.startswith("log_count"):
                crawl_detail[key] = self.stats.get_value(key, 0)
            elif key.startswith("memusage"):
                crawl_detail[key] = self.stats.get_value(key, 0)
            elif key.startswith("finish_reason"):
                crawl_detail[key] = self.stats.get_value(key, 0)
        crawl_detail.update(
            {
                "spider_name": spider.name,
                "pages_count": pages,  # 总量
                "items_count": items,  # 总量
                "pages_rate": prate,  # 速率
                "items_rate": irate,  # 速率
                "pages_add": pages_add,  # 增量
                "items_add": items_add,  # 增量
            }
        )
        report_msg = {
            "task_id": self.task_id,
            "pod_name": self.pod_name,
            "status": crawl_detail,
        }
        try:
            requests.post(self.report_url, json=report_msg)
        except Exception as e:
            logger.error(f"report error: {e}")

    def spider_opened(self, spider):
        self.start_time = datetime.now()
        self.stats.set_value("start_time", self.start_time, spider=spider)

        self.pagesprev = 0
        self.itemsprev = 0

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def spider_closed(self, spider, reason):
        finish_time = datetime.now()
        elapsed_time = finish_time - self.start_time
        elapsed_time_seconds = elapsed_time.total_seconds()
        self.stats.set_value("elapsed_time_seconds", elapsed_time_seconds, spider=spider)
        self.stats.set_value("finish_time", finish_time, spider=spider)
        self.stats.set_value("finish_reason", reason, spider=spider)

    def item_scraped(self, item, spider):
        self.stats.inc_value(f"item_scraped_count", spider=spider)
        # add item class count
        self.stats.inc_value(f"item_scraped_count/{item.__class__.__name__}", spider=spider)

    def item_dropped(self, item, spider, exception):
        self.stats.inc_value("item_dropped_count", spider=spider)
        # add item class count
        self.stats.inc_value(f"item_dropped_count/{item.__class__.__name__}", spider=spider)
        # add item class and exception count
        self.stats.inc_value(
            f"item_dropped_reasons_count/{item.__class__.__name__}/{exception.__class__.__name__}", spider=spider
        )

    def response_received(self, spider):
        self.stats.inc_value("response_received_count", spider=spider)
