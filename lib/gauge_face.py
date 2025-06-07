from stream_spec import StreamSpec
from timeseries import TimeSeries

class GaugeFace:
    
    update_freq = 30
    
    def __init__(self, name, options, resources):
        self.name = name
        self.options = options
        self.resources = resources
        
        self.data_bus = resources['data_bus'] if 'data_bus' in resources else None
        if 'streams' in options and options['streams']:
            for name, stream in options['streams'].items():
                self.streams[name] = TimeSeries(
                    stream_spec=StreamSpec(
                        **stream['stream_spec'], 
                        **stream['time_series'],
                    data_bus=self.data_bus))

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
