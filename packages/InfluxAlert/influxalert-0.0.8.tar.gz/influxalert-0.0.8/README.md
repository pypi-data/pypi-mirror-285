# InfluxAlert
## 概览
以非常少的代码实现 InfluxDB 的告警
## 快速开始
### 前置需求
需要有 InfluxDB、MongoDB
### 安装模块
```bash
pip3 install InfluxAlert
```
### 运行
```python
#!/usr/bin/env python3

import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler
from nb_log import get_logger
from influx_alert.client import Client


influx = Client(influx_host='xx',
                influx_port='8086',
                influx_database='xx',
                influx_username='xx',
                influx_password='xxx',
                influx_ssl=True,
                mongo_host='xxx',
                mongo_port=27017,
                mongo_username='xxx',
                mongo_password='xxx',
                mongo_database='xxx',
                mongo_authsource='admin',
                feishu_app_id='xxx',
                feishu_app_secret='xxx',
                feishu_card_template_id='xxx',
                feishu_card_receive_id='xxx',
                wecom_webhook_url='xxx')

# 任务函数
def alert():
    '''
    任务函数
    '''
    influx.ping.unreachable()
    influx.no_data.node_exporter()
    influx.no_data.windows_exporter()
    log.debug('run 1 time')

# 创建调度器
scheduler = BlockingScheduler()

scheduler.add_job(alert, 'interval', seconds=60, max_instances=1)

# 启动调度器
scheduler.start()
```

## 功能支持
### 通知工具
- 飞书消息卡片（支持）
- 企业微信 Markdown（支持）
### 告警
支持以下告警
- Ping 不可达
- Node Exporter 无数据时告警
- Windows Exporter 无数据时告警

