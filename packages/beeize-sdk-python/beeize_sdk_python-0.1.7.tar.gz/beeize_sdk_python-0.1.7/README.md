# beeize-sdk-python

beeize-sdk-python是专为在beeize平台开发者设计的官方库。它主要提供了数据集、文件集、请求集的读写功能，且特定的存储路径帮助开发者与用户实现统一管理使用，能够更高效地构建和维护他们的网络爬虫项目。。

## 使用说明
为了能够在本地开发网络爬虫，平台提供的存储服务在本地文件系统上进行了模拟。

存储内容从爬虫的主文件夹中加载，并保存到该文件夹。每种存储类型都存储在自己的子文件夹中，例如数据集存储在 `storage/datasets` 文件夹中。

每个存储又存放在以存储命名的文件夹中，如果是默认存储，则命名为 `default`。例如，名为 `my-queue `的请求队列将被存储在 `storage/request_queues/my-queue` 文件夹中。

每个数据集项目、键值存储记录或请求队列中的请求，都存储在存储文件夹中的自己的文件里。数据集项目和请求队列请求总是 JSON 文件，键值存储记录可以是任何文件类型，基于其内容类型。

### 数据存储
SDK 提供了一个简单的接口来存储抓取的数据，无论是单个数据项还是批量数据，都可以轻松存入指定的数据库或存储系统中。

若要将数据写入数据集，可以使用 `scraper.push_data()` 方法。

#### 存储采集结果
```python
from beeize.scraper import Scraper
scraper = Scraper()
for i in range(10):
    data = {'number': i}
    scraper.push_data(data)
```

### 使用文件存储
支持文件存储，包括文本和 JSON 格式，使得保存抓取的媒体文件或文档变得简单。

要从键值存储中读取记录，可以使用 `kv_store.get_value()` 方法。

若要将记录写入键值存储，可以使用 `kv_store.set_value()`方法。

#### 存储为txt文件
```python
from beeize.scraper import Scraper

scraper = Scraper()
kv_store = scraper.key_value_store

kv_store.set_value('filename', 'value')

kv_store.set_value('filename', {'key': 'value'})
```

#### 存储为json文件
```python
kv_store.set_value('filename', {'key': 'value'}, extension='json')
```

#### 存储为xlsx文件
```python
value = open('demo.xlsx', 'r').read()
kv_store.set_value('filename', value, extension='xlsx')
```

#### 存储为图片
```python
value = open('demo.jpg', 'r').read()
kv_store.set_value('filename', value)
```

#### 存储为视频
```python
value = open('demo.mp4', 'r').read()
kv_store.set_value('filename', value)
```


### 使用请求队列
SDK 提供的请求队列管理功能，可以帮助开发者组织和调度网络请求，对成功和失败的请求进行标记。

#### 将请求添加到队列
要将请求添加到队列中，可以使用 `RequestQueue.add_request()`  方法。

您可以使用 的请求来唯一标识请求。如果您尝试使用相同的唯一键添加更多请求， 只会添加第一个 。

#### 读取请求
要从队列中获取下一个请求进行处理， 您可以使用 `queue.fetch_next_request() `方法。

若要从队列中获取有关特定请求的信息，请执行以下操作： 您可以使用 `queue.get_request() `方法。

#### 处理请求
若要将请求标记为已处理，可以使用 `queue.mark_request_as_handled() `方法。

要将请求标记为未处理，以便重试该请求， 您可以使用 `queue.reclaim_request()`方法。

要检查队列中的所有请求是否都已处理， 您可以使用 `queue.is_finished()`方法。

### 完整示例
```python
import json

import requests
from beeize.scraper import Scraper
from loguru import logger

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ('
                  'KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
}


def fetch(url, retry_count=0):
    try:
        response = requests.get(
            url=url,
            headers=headers
        )
        return response.json()
    except (Exception,):
        if retry_count < 3:
            return fetch(url, retry_count + 1)


def main():
    scraper = Scraper()
    queue = scraper.request_queue
    kv_store = scraper.key_value_store
    visit_user_token = 'MS4wLjABAAAAiAce5qhH31TeuB3UdpFMV8u-uwy2LnoiqI10uZHqAt8'
    start_url = f'https://www.toutiao.com/api/pc/feed/?category=profile_all&utm_source=toutiao&visit_user_token={visit_user_token}&max_behot_time=0&_signature='

    # 添加初始请求任务到队列
    queue.add_request({'url': start_url, 'type': 'profile'})

    while queue.is_finished():
        # 消费队列中的请求任务
        request = queue.fetch_next_request()
        if not request:
            break

        logger.info(request)
        url = request['url']
        # 下载请求
        resp = fetch(url)
        if not resp:
            # 对失败请求进行标记
            queue.reclaim_request(request)
            continue
        # 对成功请求进行标记
        queue.mark_request_as_handled(request)

        # 解析列表页
        if request['type'] == 'profile':
            for item in resp.get('data'):
                item_id = item.get('item_id')
                item['type'] = 'basic'
                # 存储到 datasets
                scraper.push_data(item)
                logger.info(item)
                # 添加详情页请求任务到队列
                queue.add_request({
                    'url': f'https://m.toutiao.com/i{item_id}/info/',
                    'type': 'detail',
                    'item_id': item_id,
                })

        # 解析详情页
        if request['type'] == 'detail':
            item = resp.get('data')
            item['url'] = url
            item['type'] = 'complete'
            # 存储到 datasets
            scraper.push_data(item)
            item_id = request.get('item_id')
            # 存储文件到 kv_store
            kv_store.set_value(item_id, json.dumps(item, ensure_ascii=False, indent=4))
            logger.info(item)  # 日志


if __name__ == '__main__':
    main()
```

## 存储结果的查看与导出
### 本地
```
storage/
    request_queues/
        default/
    datasets/
        default/
    kv_stores/
        default/
```

### 云上查看
进入运行结果详情页可在数据栏查看统计信息与数据概览。

### 云上导出
导出可以直接点击下载JSON或下载CSV。

还可以通过WebHook进行数据传输。