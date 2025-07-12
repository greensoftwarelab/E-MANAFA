import os
import time
from unittest import TestCase

from manafa.services.AmProfilerService import AmProfilerService
from manafa.services.perfettoService import PerfettoService, device_has_perfetto
from manafa.utils.Utils import execute_shell_command


# python -m unittest  manafa/tests/services/test_AMProfilerService.py
class AMProfilerService(TestCase):
    package = "com.example.sampleapp"
    service = AmProfilerService(package)

    def test_start(self):
        res = self.service.start()
        print(res)
        self.assertTrue(res, "am service class starts")
        is_running, _, _ = execute_shell_command(f"adb shell ps | grep {self.package}")
        self.assertEqual(is_running, 0, "am started app")
        self.service.stop()
        self.service.clean()

    def test_stop(self):
        print("testing stop")
        self.service.start()
        time.sleep(5)
        res = self.service.stop()
        self.assertRegex(res, r".*app_.*\.csv$", "unable to get a trace file")
        self.assertTrue(os.path.exists(res), "trace file does not exists")
        self.assertGreater(os.stat(res).st_size, 4, "file is empty")
        self.service.clean()

    def test_export(self):
        self.service.start()
        time.sleep(5)
        self.service.stop()
        res = self.service.export()
        print(f'exported file {res}')
        self.assertTrue(os.path.exists(res), msg='results file exists')
        self.service.clean()


