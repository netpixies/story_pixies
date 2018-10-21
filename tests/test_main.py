import unittest
from os import path
import sys
import time
from kivy.clock import Clock
from functools import partial

main_path = path.dirname(path.dirname(path.abspath(__file__)))
sys.path.append(main_path)

from storypixies import StoryPixiesApp


class Test(unittest.TestCase):

    def pause(*args):
        time.sleep(0.000001)

    def run_test(self, app, *args):
        Clock.schedule_interval(self.pause, 0.000001)
        a = 1
        self.assertEquals(a, 1)
        app.stop()

    def test_example(self):
        app = StoryPixiesApp()
        p = partial(self.run_test, app)
        Clock.schedule_once(p, 0.000001)
        app.run()

    if __name__ == '__main__':
        unittest.main()
