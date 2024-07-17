# from ..influx_alert.influx_alert import InfluxAlert

from influx_alert.influx_alert import InfluxAlert


influx_alert = InfluxAlert(influx_auth='', 
                           webhook_url='', 
                           mongodb_auth='')

influx_alert.ping.unreachable()
