import asyncio
import lib.config_tools
import machine
import random
import time
import task_handler
import lvgl
import fs_driver
from lib.local_utils import schedule
from faces.detailed import Detailed
from lib.passy import Passy
from hw.waveshare_esp32s3_lcd_1_85 import setup_hardware

from lib.local_utils import schedule

def initialize_gauge_faces(gauge_faces, resources):
    gauge_tasks = []
    name = 'default'
    gauge_face = Detailed(name, gauge_faces[name], resources)
    gauge_tasks.append(asyncio.create_task(schedule(frequency=int(gauge_face.update_freq), coroutine_function=gauge_face.update)))
    return gauge_tasks
            

async def setup_tasks(config, resources):
    tasks = {
        'data_sources': {},
        'gauge_faces': [],
        'fs': fs_drv
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
            tasks['data_sources'][data_source] = asyncio.create_task(schedule(frequency=data_source_obj.poll_freq, coroutine_function=data_source_obj.poll))
    tasks['gauge_faces'] = initialize_gauge_faces(config['gauge_faces'], resources)
    await asyncio.sleep(60)


if __name__ == "__main__":
    config = {
        'data_sources': {
            'mock': {
                'type': 'mock',
                'enabled': True,
                'poll_freq': 5,
                'send_frame_ids': [0x902]
            },
        },
        'gauge_faces': {
            'default':{
                'streams': {
                    'eng_rpm': {
                        'time_series': {
                            'upto_vals': 100,
                            'retain_for_s': 60
                        },
                        'stream_spec': {
                            'field_spec': 'eng_rpm',
                            'min_val': 0,
                            'max_val': 9999,
                        }
                    }
                }
            }
        },
        'hardware': {}
    }
    resources = setup_hardware(config['hardware'])
    fs_drv = lvgl.fs_drv_t()
    fs_driver.fs_register(fs_drv, 'S')
    resources['fs'] = fs_drv
    th = task_handler.TaskHandler()
    asyncio.run(setup_tasks(config, resources))