import kivy


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

kivy.require('1.10.1')


class StoryHome(Screen):
    pass


class StoryLibrary(Screen):
    pass


class StoryCreator(Screen):
    pass

class StoryBook(Screen):
    pass

class StoryBase(BoxLayout):
    pass

class StorySettings(Screen):
    pass

class StoryPixiesApp(App):

    def build(self):
        return StoryBase()

    def build_config(self, config):
        pass

    def build_settings(self, settings):
        pass

    def on_config_change(self, config, section, key, value):
        pass


if __name__ == '__main__':
    StoryPixiesApp().run()
