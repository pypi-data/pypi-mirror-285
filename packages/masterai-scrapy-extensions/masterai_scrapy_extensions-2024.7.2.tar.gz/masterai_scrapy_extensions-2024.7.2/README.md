# Scrapy Log Report Extension

A Scrapy extension that report your log from your scraped data.

## Usage

This Scrapy extension provides a way to report your log from your scraped data. It will generate a report every `LOGSTATS_INTERVAL` seconds, and send it to your log server.

```bash
# log report demo
{
  "items_add": 0,
  "pages_add": 0,
  "items_rate": 0,
  "pages_rate": 0,
  "items_count": 0,
  "pages_count": 0,
  "spider_name": "douban",
  "log_count/INFO": 8,
  "log_count/DEBUG": 1,
  "log_count/WARNING": 2,
  "item_scraped_add_count": 0,
  "response_received_add_count": 0
}
```

## Installation

First, pip install this package:

```bash
$ pip install masterai-scrapy-extensions
```

## Usage

Enable the extension in your project's `settings.py` file, by adding the following lines:

```python
EXTENSIONS = {
    "masterai_scrapy_extensions.logreport.ReportStats": 100,
}
#
LOGSTATS_INTERVAL = 60
# set the URL to your log server
# method POST is used to send the report data
LOGREPORT_URL = "http://127.0.0.1:5000/api/v1/task/worker/status"

# log color
from masterai_scrapy_extensions import logcolor

logcolor.log_color_init()
```

That's all! Now run your job and have a look at the field stats.

## Settings

The settings below can be defined as any other Scrapy settings, as described on [Scrapy docs](https://doc.scrapy.org/en/latest/topics/settings.html#populating-the-settings).

- `LOGREPORT_URL`: set the interval in seconds to generate the report.
- `LOGSTATS_INTERVAL`: set the URL to your log server,method POST is used to send the report data.
- `COLORLOG_FORMAT`: log color format.
- `COLORLOG_COLORS`: log colors.
- `COLORLOG_DATEFORMAT`: log color date format.
