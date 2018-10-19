import kivy


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.uix.screenmanager import Screen
from storysettings import settings_json

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
        self.settings_cls = SettingsWithTabbedPanel
        self.use_kivy_settings = False

        return StoryBase()

    def build_config(self, config):
        config.setdefaults('library', {
            'name': 'default',
            'story_dir': '.'
        })

    def build_settings(self, settings):
        settings.add_json_panel('Story Settings',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section, key, value):
        print config, section, key, value


if __name__ == '__main__':
    StoryPixiesApp().run()
