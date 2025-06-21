import json
import time
from local_utils import print_dbg

dump_cfg = False
debug = False

class TimeSeries():
    def __init__(self, stream_spec, data_bus=None, upto_vals=1, retain_for_s=0) -> None:
        if dump_cfg:
            print("stream_spec: {}".format(json.dumps(stream_spec.__dict__)))
            print("upto: {}, retain_for_s: {}".format(upto_vals, retain_for_s))
        self.upto_vals = upto_vals
        self.retain_for_s = retain_for_s
        print("upto_vals: {}, retain_for_s: {}".format(upto_vals, retain_for_s))

        self.stream_spec = stream_spec
        self.min_val = self.max_val = self.stream_spec.min_val
        self.data = [(time.ticks_ms(), self.stream_spec.min_val)]
        
        if data_bus:
            data_bus.sub(self.stream_updated, "data.{}".format(stream_spec.field_spec))

    @property
    def subscribed_streams(self):
        return [self.stream_spec.field_spec]

    def stream_updated(self, updates):
        tstamp = time.ticks_ms()
        for topic, value in updates:
            (prefix, field_spec) = topic.split(".")
            if prefix == 'data' and self.stream_spec.field_spec == field_spec:
                val = value * self.stream_spec.units['conversion_factor']
                self.latest = (tstamp, val)

    @property
    def value(self):
        return self.data[-1][1]
    
    @property
    def values(self):
        return [x[1] for x in self.data]
    
    @property
    def earliest(self):
        return self.data[0]

    @property
    def latest(self):
        return self.data[-1]

    @latest.setter
    def latest(self, tstamp_val):
        if self.upto_vals == 1:
            self.data[0] = tstamp_val
            self.min_val = self.max_val = tstamp_val[1]
            #print("early return")
            return

        #print("long way round")
        if tstamp_val[1] > self.stream_spec.max_val:
            tstamp_val = (tstamp_val[0], self.stream_spec.max_val)
        elif tstamp_val[1] < self.stream_spec.min_val:
            tstamp_val = (tstamp_val[0], self.stream_spec.min_val)
        self.data.append(tstamp_val)
        self.trim()
        self.update_aggregates()
                
    def trim(self):
        cur_time = time.ticks_ms()
        if self.upto_vals > 0 and len(self.data) > self.upto_vals:
            print("Trimmed due to too many values!")
            del self.data[:-self.upto_vals]
        if self.retain_for_s > 0:
            for n, v in enumerate(self.data):
                if v[0] < (cur_time - self.retain_for_s * 1000):
                    print("Trimmed old value!")
                    del self.data[n]
                else:
                    break

    def update_aggregates(self):
        self.min_val = self.stream_spec.max_val
        self.max_val = self.stream_spec.min_val
        for ts, val in self.data:
            #print("{}/{}: {} >= {} => {}".format(len(self.data), self.upto_vals, self.max_val, self.value, self.min_val))
            if val < self.min_val:
                #print(val)
                self.min_val = val
            if val > self.max_val:
                #print(val)
                self.max_val = val
        #print([x[1] for x in self.data])
        #print("min: {}, max: {}".format(self.min_val, self.max_val))

                
    def since(self, tstamp):
        return [self.data[i] for i, _ in enumerate(self.data) if self.data[i][0] > tstamp]
