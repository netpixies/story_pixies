import kivy

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.uix.screenmanager import Screen
from storysettings import get_settings_json
from kivy.uix.settings import SettingOptions
from kivy.uix.settings import StringProperty, NumericProperty, ObjectProperty, DictProperty, ListProperty
from pathlib import Path
from kivy.config import ConfigParser
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

kivy.require('1.10.1')


class LibraryOptions(SettingOptions):
    function_string = StringProperty()

    def _create_popup(self, instance):
        story_list = (Path(__file__).parents[0].absolute() / "libraries" / instance.section).glob('**/*.ini')
        self.options = [l.stem for l in story_list]
        super(LibraryOptions, self)._create_popup(instance)


class LibrarySettings(SettingsWithTabbedPanel):
    def __init__(self, *args, **kwargs):
        super(LibrarySettings, self).__init__(*args, **kwargs)
        self.register_type('library_options', LibraryOptions)


class StoryHome(Screen):
    def __init__(self, *args, **kwargs):
        super(StoryHome, self).__init__(*args, **kwargs)

    def navigate_to_library(self, instance):
        main_app.set_selected_library(instance.text)
        self.manager.current = 'story_library'

    def on_enter(self, *args):
        topscreen = self.ids.story_home_id
        topscreen.clear_widgets()
        topgrid = GridLayout(cols=2, spacing='2dp')
        topscreen.add_widget(topgrid)
        for i in self.libraries:
            b = Button(text=i)
            b.bind(on_release=self.navigate_to_library)
            topgrid.add_widget(b)


class StoryLibrary(Screen):
    books = NumericProperty(10)

    def __init__(self, *args, **kwargs):
        super(StoryLibrary, self).__init__(*args, **kwargs)
        #print main_app.config.get('sylvia', 'current_book')

    def navigate_to_book(self, book):
        main_app.set_selected_book(book.text)
        self.manager.current = 'story_book'

    def on_pre_enter(self, *args):
        topscreen = self.ids.story_lib
        topscreen.clear_widgets()
        topgrid = GridLayout(cols=2, spacing='2dp')
        topscreen.add_widget(topgrid)
        for story in main_app.get_stories():
            b = Button(text=str(story))
            b.bind(on_release=self.navigate_to_book)
            topgrid.add_widget(b)


class StoryCreator(Screen):
    pass


class StoryBook(Screen):
    currentBook = DictProperty()
    currentValues = DictProperty()

    def __init__(self, *args, **kwargs):
        super(StoryBook, self).__init__(*args, **kwargs)
        self.story_config = ConfigParser()
        self.story_config.read('/Users/ahardy/Desktop/storypixies/libraries/sylvia/Hello World.ini')

    def get_story_config(self):
        print self.story_config.get('values', 'name')


class StoryBase(BoxLayout):
    pass


class StorySettings(Screen):
    pass


class StoryFront(Screen):
    pass


class StoryTemplate(BoxLayout):
    pass


class CustomData(BoxLayout):
    pass


class StoryPixiesApp(App):
    selected_library = StringProperty("default")
    selected_book = StringProperty("default")

    def __init__(self, *args, **kwargs):
        super(StoryPixiesApp, self).__init__(*args, **kwargs)
        # Finds all files in libraries subdir ending with .ini
        self.libraries = self.get_libraries()
        self.templates = self.get_templates()

    def set_selected_library(self, library):
        self.selected_library = library

    def set_selected_book(self, book):
        self.selected_book = book

    def build(self):
        self.settings_cls = LibrarySettings
        self.use_kivy_settings = False
        return StoryBase()

    def build_config(self, config):
        config.setdefaults('global', {'template_dir': Path(__file__).parents[0].absolute() / "templates"})
        for library in self.libraries:
            config.setdefaults(library, {
                'name': library,
                'story_dir': Path(__file__).parents[0].absolute() / "libraries" / library,
                'current_book' : ''
            })

    def build_settings(self, settings):
        settings.add_json_panel('Global', self.config, data=get_settings_json('global'))
        for library in self.libraries:
            settings.add_json_panel(library.capitalize(), self.config, data=get_settings_json(library))

    def on_config_change(self, config, section, key, value):
        print config, section, key, value

    @staticmethod
    def get_templates():
        template_list = (Path(__file__).parents[0].absolute() / "templates")
        return [t.stem for t in template_list.iterdir() if t.is_file()]

    @staticmethod
    def get_libraries():
        library_list = (Path(__file__).parents[0].absolute() / "libraries")
        return [l.stem for l in library_list.iterdir() if l.is_dir()]

    def get_stories(self):
        story_list = (Path(__file__).parents[0].absolute() / "libraries" / self.selected_library)
        return [s.stem for s in story_list.iterdir() if s.is_file()]

def populate_story_from_template(template, story):
    pass




if __name__ == '__main__':
    main_app = StoryPixiesApp()
    main_app.run()
