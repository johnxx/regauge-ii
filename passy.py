#!/usr/bin/env python3
# from asynccp.time import Duration
# from functools import partial
from local_utils import print_dbg

debug = False

class Passy():
    def __init__(self, task_manager=None) -> None:
        self.subscriptions = {}
        self.subscribers = {}
        self.outbox = {}
        if task_manager:
            self.task_manager = task_manager
            self.is_async = True
        
    def sub(self, subscriber, topic_pref):
        sub_id = str(id(subscriber))
        print_dbg("{} has been subscribed to {}".format(sub_id, topic_pref))
        self.subscribers[sub_id] = subscriber
        if sub_id not in self.subscriptions:
            self.subscriptions[sub_id] = set()
        self.subscriptions[sub_id].add(topic_pref)
        return (sub_id, topic_pref)

    def pub(self, topic, msg, auto_send=True):
        print_dbg("Got a message about {}".format(topic))
        for sub_id, topic_prefs in self.subscriptions.items():
            for topic_pref in topic_prefs:
                if topic.startswith(topic_pref):
                    if sub_id not in self.outbox:
                        self.outbox[sub_id] = []
                    self.outbox[sub_id].append((topic, msg))
                    if auto_send:
                        self.send(sub_id)

    async def send_async(self, sub_id):
        if sub_id in self.outbox and self.outbox[sub_id]:
            print_dbg("Got called to send {} messages async to {}".format(len(self.outbox[sub_id]), sub_id))
            self.subscribers[sub_id](self.outbox[sub_id])
            self.outbox[sub_id] = []
        raise(StopIteration)

    def schedule_send(self, sub_id):
        raise Exception("Not implemented")
        almost_immediately = Duration.of_microseconds(1)
        print_dbg("Scheduling {} messages to {} for later".format(len(self.outbox[sub_id]), sub_id))
        callback = partial(self.send_async, sub_id)
        self.task_manager.schedule(frequency=almost_immediately, coroutine_function=callback)

    def send(self, sub_id):
        if sub_id in self.outbox and self.outbox[sub_id]:
            if self.is_async:
                self.schedule_send(sub_id)
            else:
                print_dbg("Sending {} messages to {}".format(len(self.outbox[sub_id]), sub_id))
                self.subscribers[sub_id](self.outbox[sub_id])
                self.outbox[sub_id] = []

    def send_all(self):
        print_dbg("Sending all events!")
        for sub_id in self.outbox:
            # print("Sending updates for {}".format(sub_id))
            self.send(sub_id)

    def unsub(self, sub_id, topic_pref):
        print_dbg("{} wants to unsubscribe from {}".format(sub_id, topic_pref))
        if sub_id in self.subscriptions:
            if topic_pref in self.subscriptions[sub_id]:
                print_dbg("{} unsubsribed from {}".format(sub_id, topic_pref))
                self.subscriptions[sub_id].remove(topic_pref)
                if not self.subscriptions[sub_id]:
                    print_dbg("{} has no more subscriptions".format(sub_id))
                    del(self.subscriptions[sub_id])
