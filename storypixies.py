import kivy


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.uix.screenmanager import Screen
from storysettings import get_settings_json
from kivy.uix.settings import SettingOptions
from kivy.uix.settings import StringProperty
from pathlib import Path

kivy.require('1.10.1')



class LibraryOptions(SettingOptions):
    function_string = StringProperty()

    def _create_popup(self, instance):
        self.options = ['foo','bar','baz']
        super(LibraryOptions, self)._create_popup(instance)


class LibrarySettings(SettingsWithTabbedPanel):
    def __init__(self, *args, **kwargs):
        super(LibrarySettings, self).__init__(*args, **kwargs)
        self.register_type('library_options', LibraryOptions)


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
    def __init__(self, *args, **kwargs):
        super(StoryPixiesApp, self).__init__(*args, **kwargs)
        # Finds all files in libraries subdir ending with .ini
        library_list = (Path(__file__).parents[0].absolute() / "libraries").glob('**/*.ini')
        self.libraries = [l.stem for l in library_list]

    def build(self):
        self.settings_cls = LibrarySettings
        self.use_kivy_settings = False

        return StoryBase()

    def build_config(self, config):
        for library in self.libraries:
            config.setdefaults(library, {
                'name': library,
                'story_dir': Path(__file__).parents[0].absolute() / "stories" / library,
                'current_library': []
            })

    def build_settings(self, settings):
        for library in self.libraries:
            settings.add_json_panel(' Settings: ' + library, self.config, data=get_settings_json(library))

    def on_config_change(self, config, section, key, value):
        print config, section, key, value



if __name__ == '__main__':
    StoryPixiesApp().run()
