from .ping_alert_strategy import PingAlertStrategy
from .vmware_cpu_alert_strategy import VMwareCpuAlertStrategy


class InfluxAlert:
    def __init__(self, influx_auth, webhook_url, mongodb_auth):
        self.influx_auth = influx_auth
        self.webhook_url = webhook_url
        self.mongodb_auth = mongodb_auth

        # 初始化告警策略
        self.ping = PingAlertStrategy(influx_auth, webhook_url)
        self.vmware = VMwareCpuAlertStrategy(influx_auth, webhook_url, mongodb_auth)
        
        

if __name__ == '__main__':
    main()