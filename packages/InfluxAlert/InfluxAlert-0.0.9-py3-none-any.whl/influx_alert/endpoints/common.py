from ..endpoint import Endpoint
from nb_log import get_logger

log = get_logger('no_data')


ALARM_NAME_NO_DATA = '无监控数据'
ALARM_NAME_UPS_BATTERY_NEEDS_REPLACING = 'UPS 电池需更换'

class CommonEndpoint(Endpoint):
    
    def no_data_node_exporter(self):
        query = """select
    *
    from node_uname_info 
    where time > now() - 1d 
    group by "url"
    order by desc
    limit 1"""
        
        log.debug(f'query: [{query.strip()}]')
        for results in self.parent.influx_client.query(query=query):
            diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
            log.debug(diff_now)
            
            if diff_now > 3:
                nodename = results['nodename']
                
                for url_dict in self.parent.influx_client.query(f"""select * from node_uname_info where "nodename" = '{nodename}' order by time desc limit 1"""):
                    url = url_dict['url']
                
                self.parent.extensions.tool_check_insert_send_mongo(
                    restore_influx=f"""select last(*) from node_uname_info where "url" = '{url}'""",
                    alarm_content= results['nodename'] + ' ' + url.replace('http://', '').replace(':9100/metrics', '') + ' ' + ALARM_NAME_NO_DATA,
                    alarm_name=ALARM_NAME_NO_DATA,
                    priority='高',
                    alarm_time=self.parent.extensions.time_get_now_time_mongo(),
                    entity_name=nodename,
                    is_notify=True)


        for mongo_item in self.parent.extensions.mongo_query_trigger(alarm_name=ALARM_NAME_NO_DATA):
            log.debug('恢复语法: ' + mongo_item['restore_influx'])
            
            for results in self.parent.influx_client.query(mongo_item['restore_influx']):
                log.debug(results)
                
                diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
                nodename = mongo_item['entity_name']
                
                if diff_now < 3:
                    self.parent.extensions.tool_check_insert_send_mongo(mongo_id = mongo_item['_id'],
                        event_type='trigger',
                        alarm_content= mongo_item['alarm_content'],
                        alarm_name=ALARM_NAME_NO_DATA,
                        priority='高',
                        entity_name=nodename,
                        is_notify=True)
                    
    def no_data_windows_exporter(self):
        query = """select
*
from windows_cs_hostname 
where time > now() - 1d 
group by "url"
order by desc
limit 1"""
        
        log.debug(f'query: [{query.strip()}]')
        for results in self.parent.influx_client.query(query=query):
            hostname = results['hostname']
            diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
            log.debug(f'{hostname} {diff_now}')
            if diff_now > 5:
                
                
                for url_dict in self.parent.influx_client.query(f"""select * from windows_cs_hostname where "hostname" = '{hostname}' order by time desc limit 1"""):
                    url = url_dict['url']
                
                self.parent.extensions.tool_check_insert_send_mongo(
                    restore_influx=f"""select last(*) from windows_cs_hostname where "url" = '{url}'""",
                    alarm_content= results['hostname'] + ' ' + url.replace('http://', '').replace(':9182/metrics', '') + ' ' + ALARM_NAME_NO_DATA,
                    alarm_name=ALARM_NAME_NO_DATA,
                    priority='高',
                    entity_name=hostname,
                    is_notify=True)

        for mongo_item in self.parent.extensions.mongo_query_trigger(alarm_name=ALARM_NAME_NO_DATA):
            log.debug('恢复语法: ' + mongo_item['restore_influx'])
            
            for results in self.parent.influx_client.query(mongo_item['restore_influx']):
                log.debug(results)
                
                diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
                hostname = mongo_item['entity_name']
                
                if diff_now < 3:
                    self.parent.extensions.tool_check_insert_send_mongo(
                        mongo_id = mongo_item['_id'],
                        event_type='resolved',
                        alarm_content= mongo_item['alarm_content'],
                        alarm_name=ALARM_NAME_NO_DATA,
                        priority='高',
                        entity_name=hostname,
                        is_notify=True)
    
    def not_resolved_trigger(self):
        query = {
            'resolved_time': {'$exists': False}
        } 
        for results in self.parent.mongo_client.find(query):
            print(results)
    
    def ups_apc_advbattery_replace_indicator(self, suggestion):
        query= """
    SELECT "sysName", "upsAdvBatteryReplaceIndicator"  FROM "ups" WHERE time > now() - 10m group by "sysName" order by time desc limit 5
    """
        for results in self.parent.influx_client.query(query=query):
            # log.debug(results)
            has_loss = all(result['upsAdvBatteryReplaceIndicator'] == 'batteryNeedsReplacing' for result in results)
            if has_loss:
                log.debug(results)
                sysname = results[0]['sysName']
            # ups_common(query=query_upsBasicBatteryStatus,
            #         check_field='upsBasicBatteryStatus',
            #         check_value='batteryNormal',
            #         priority=const.PRIORITY_WARNING,
            #         alarm_name=const.ALARM_NAME_UPS_STATUS, 
            #         suggestion='')
                self.parent.extensions.tool_check_insert_send_mongo(
                    restore_influx=f"""SELECT last("upsAdvBatteryReplaceIndicator")  FROM "ups" WHERE "sysName" = '{sysname}'""",
                    url=sysname,
                    alarm_name=ALARM_NAME_UPS_BATTERY_NEEDS_REPLACING,
                    entity_name=sysname,
                    alarm_content=f'{sysname} {ALARM_NAME_UPS_BATTERY_NEEDS_REPLACING}',
                    alarm_time=self.parent.extensions.time_get_now_time_mongo(),
                    priority='warning',
                    is_notify=True,
                    suggestion=suggestion)
                break
    