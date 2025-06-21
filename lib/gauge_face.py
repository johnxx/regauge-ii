from lib.stream_spec import StreamSpec
from lib.time_series import TimeSeries

class GaugeFace:
    
    update_freq = 5
    
    def __init__(self, name, options, resources):
        self.name = name
        self.options = options
        self.resources = resources
        
        self.data_bus = resources['data_bus'] if 'data_bus' in resources else None
        if 'streams' in options and options['streams']:
            self.streams = {}
            for name, stream in options['streams'].items():
                self.streams[name] = TimeSeries(
                    stream_spec=StreamSpec(**stream['stream_spec']), 
                    data_bus=self.data_bus, 
                    **stream['time_series'])

        self.config_bus = resources['config_bus'] if 'config_bus' in resources else None
        if 'config_bus' in resources:
            self.config_bus.sub(self.config_updates, "config.gauge_faces.{}".format(name))
        
    @property
    def subscribed_streams(self):
        if self.streams:
            subscribed_streams = []
            for _, s in self.streams.items():
                subscribed_streams += s.subscribed_streams
            return subscribed_streams
    
    async def update(self):
        pass

    def config_updates(self, message):
        pass
