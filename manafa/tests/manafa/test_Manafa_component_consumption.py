import time
from unittest import TestCase

from manafa.emanafa import EManafa


class TestManafaComponents(TestCase):

    '''def test_bluetooth_detection(self):
        manafa = EManafa()
        input("please turn on bluetooth and press enter")
        manafa.init()
        manafa.start()
        print("profiling...")
        time.sleep(8)  # do work
        print("stopping profiler...")
        manafa.stop()
        begin = manafa.perf_events.events[0].time  # first sample from perfetto
        end = manafa.perf_events.events[-1].time  # last sample from perfetto
        total, per_c, timeline = manafa.get_consumption_in_between(begin, end)
        self.assertGreater(per_c['bluetooth'] if 'bluetooth' in per_c else 0, 0)'''

    def test_wifi_detection_on(self):
        manafa = EManafa()
        input("please turn on wifi and press enter")
        manafa.init()
        manafa.start()
        print("profiling...")
        time.sleep(8)  # do work
        print("stopping profiler...")
        manafa.stop()
        begin = manafa.perf_events.events[0].time  # first sample from perfetto
        end = manafa.perf_events.events[-1].time  # last sample from perfetto
        total, per_c, timeline = manafa.get_consumption_in_between(begin, end)
        self.assertGreater(per_c['wifi'] if 'wifi' in per_c else 0, 0)