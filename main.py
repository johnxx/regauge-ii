import asyncio
import config_tools
import machine
import random
import time
import task_handler
from local_utils import schedule
from detailed import Detailed
from passy import Passy
from waveshare_esp32s3_lcd_1_85 import setup_hardware

from local_utils import schedule

def initialize_gauge_faces(gauge_faces, resources):
    gauge_tasks = []
    for gauge_name, block in gauge_faces.items():
        gauge_face = Detailed(gauge_name, block, resources)
        gauge_tasks.append(schedule(frequency=int(gauge_face.update_freq), coroutine_function=gauge_face.update))
    return gauge_tasks
            

def setup_tasks(config, resources):
    tasks = {
        'data_sources': {},
        'gauge_faces': [],
    }
    msg_bus = None
    for data_source, options in config['data_sources'].items():
        if 'type' not in options:
            print("Failed to infer type for {}".format(data_source))
            raise Exception
        if 'enabled' not in options:
            print("Automatically enabled {}".format(data_source))
            options['enabled'] = True
        if options['enabled']:
            options.pop('enabled')
            print("Loading: {}".format('sources.' + options['type']))
            data_source_module = __import__('sources.' + options['type'])
            if 'config_source' in options and options['config_source']:
                data_source_class = getattr(data_source_module, options['type']).ConfigSource
                del options['type']
                options.pop('config_source')
                if 'config_bus' not in resources: 
                    if not msg_bus:
                        msg_bus = Passy()
                    resources['config_bus'] = msg_bus
                data_source_obj = data_source_class(data_source, resources, config, **options)
            else:
                data_source_class = getattr(data_source_module, options['type']).DataSource
                del options['type']
                if 'data_bus' not in resources:
                    if not msg_bus:
                        msg_bus = Passy()
                    resources['data_bus'] = msg_bus
                data_source_obj = data_source_class(data_source, resources, **options)
            tasks['data_sources'][data_source] = schedule(frequency=data_source_obj.poll_freq, coroutine_function=data_source_obj.poll)
    tasks['gauge_faces'] = initialize_gauge_faces(config['gauge_faces'], resources)
    return tasks
        


if __name__ == "__main__":
    config = {
        'data_sources': {},
        'gauge_faces': {},
        'hardware': {}
    }
    resources = setup_hardware(config['hardware'])
    th = task_handler.TaskHandler()
    setup_tasks(config, resources)