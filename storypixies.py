import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
kivy.require('1.10.1')


class StoryCreator(Widget):
    pass


class StoryLibrary(Widget):
    pass


class StoryBook(Widget):
    pass


class StoryBase(BoxLayout):
    def get_title(self):
        return 'Story base title'

    def create_story(self):
        pass


class StoryPixiesApp(App):

    def build(self):
        story_base = StoryBase()
        self.title = 'Welcome to Story Pixies!'
        return story_base

    def build_config(self, config):
        pass

    def build_settings(self, settings):
        pass

    def on_config_change(self, config, section, key, value):
        pass


if __name__ == '__main__':
    StoryPixiesApp().run()
