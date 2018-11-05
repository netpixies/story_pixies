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
from kivy.uix.image import Image
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from random import randint
from kivy.uix.carousel import Carousel

kivy.require('1.10.1')


class LibraryOptions(SettingOptions):
    function_string = StringProperty()

    def _create_popup(self, instance):
        story_list = (Path(__file__).parents[0].absolute() / "libraries" / instance.section).glob('**/*.ini')
        self.options = [l.stem for l in story_list]
        super(LibraryOptions, self)._create_popup(instance)


class LibrarySettings(SettingsWithTabbedPanel):
    def __init__(self, **kwargs):
        super(LibrarySettings, self).__init__(**kwargs)
        self.register_type('library_options', LibraryOptions)


class LibraryButton(Button):
    pass


class StoryHome(Screen):
    def __init__(self, **kwargs):
        super(StoryHome, self).__init__(**kwargs)

    def on_enter(self, *args):
        library_grid = self.ids.library_grid
        library_grid.clear_widgets()
        for i in self.libraries:
            b = LibraryButton(text=i)
            library_grid.add_widget(b)

        library_grid.bind(minimum_height=library_grid.setter('height'))


class StoryLibrary(Screen):

    def __init__(self, **kwargs):
        super(StoryLibrary, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.ids.story_button.text = main_app.get_story_title()
        self.ids.story_button_image.source = main_app.get_story_media()

class StoryCreator(Screen):
    pass


class StoryBook(Screen):
    media_property = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(StoryBook, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.assemble_layout()

    def assemble_layout(self):
        if self.media_property is not None:
            self.media_property.state = 'stop'

        top_grid = self.ids.story_book_grid
        top_grid.clear_widgets()
        d = self.get_story_display()
        self.media_property = self.get_media_display()
        story_back_button = Button(text="Back",
                                   size_hint_y=0.1,
                                   background_normal='images/backgrounds/button.png',
                                   bold=True)
        story_next_button = Button(text="Next",
                                   size_hint_y=0.1,
                                   background_normal='images/backgrounds/button.png',
                                   bold=True)
        story_back_button.bind(on_release=self.prev_page)
        story_next_button.bind(on_release=self.next_page)
        top_grid.add_widget(d)
        top_grid.add_widget(self.media_property)
        top_grid.add_widget(story_back_button)
        top_grid.add_widget(story_next_button)

    def prev_page(self):
        if self.current_page == 'title':
            self.manager.current = 'story_library'
        else:
            main_app.previous_page()
            self.assemble_layout()

    def next_page(self):
        page_now = self.current_page_no
        main_app.next_page()
        if page_now == self.current_page_no:
            self.manager.current = 'story_library'
        else:
            self.assemble_layout()

    @staticmethod
    def get_story_display():
        story_text_label = Label(text=main_app.get_story_text(),
                                 text_size=(None, None),
                                 font_size="20sp",
                                 pos_hint={'center_x': 0.5, 'center_y': 100.85},
                                 size_hint_y=1,
                                 halign="center",
                                 valign="middle")

        return story_text_label

    def get_media_display(self):
        media_type = main_app.get_story_media_type()
        if media_type == 'image':
            return Image(source=main_app.get_story_media(), allow_stretch=False, keep_ratio=True)
        elif media_type == 'video':
            return VideoPlayer(id=self.current_page + 'video', source=main_app.get_story_media(), state='play',
                               options={'allow_stretch': True, 'keep_ratio': True})


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
    selected_library = StringProperty(None)
    libraries = ListProperty()

    stories = ListProperty()
    selected_story_no = NumericProperty(0)
    selected_story = StringProperty(None)

    template_config = ObjectProperty(None)

    current_page = StringProperty("title")
    current_page_no = NumericProperty(0)
    current_pages = ListProperty()

    def __init__(self, **kwargs):
        """
        Initializes the root widget.
        Sets property defaults.
        Sets selected library as the first found library.
        :param kwargs:
        """
        super(StoryPixiesApp, self).__init__(**kwargs)
        self.libraries = self.get_libraries()

        self.selected_library = self.libraries[0]

    def set_property_defaults(self):
        """
        Sets/resets the default values for properties
        """
        self.selected_story_no = 0
        self.template_config = ConfigParser()
        self.current_page = "title"
        self.current_page_no = 0
        self.current_pages = []

    def set_selected_library(self, library):
        """
        Resets the defaults.
        Stores passed library as selected.
        Gets stories for this library.
        Sets selected story to the first.
        :param library: the library to set as current
        """
        if library in self.libraries:
            self.set_property_defaults()
            self.selected_library = library
            self.stories = self.get_stories(self.selected_library)
            self.set_selected_story(0)

    def set_selected_story(self, num):
        """
        Mods passed number so it wraps selected story num.
        Sets the selected story and story number.
        Sets the current page to the title page.
        Sets the current page number to 0.
        Parses configs using template and library.
        Sets current pages.
        :param num:
        :return: Returns name of selected story.
        """
        num %= len(self.stories)

        self.selected_story = self.stories[num]
        self.selected_story_no = num
        self.current_page = "title"
        self.current_page_no = 0
        self.parse_story_configs()

        # Set the pages in the story
        pages = self.template_config.get('title', 'pages')
        self.current_pages = ['title'] + [x.strip() for x in pages.split(',')]
        return self.template_config.get('title', 'name')

    def parse_story_configs(self):
        """
        Parses story configs based on its template. It will interpolate individual
        story defaults into templatized config.
        """
        # Get individual story defaults
        story_dir = (Path(__file__).parents[0].absolute() / "libraries" / self.selected_library)
        story_config = ConfigParser()
        story_config.read(str(story_dir) + '/' + self.selected_story + '.ini')

        # Get templatized values
        template_dir = self.config.get('global', 'template_dir')
        self.template_config = ConfigParser()

        # Interpolate individual story defaults into templatized config
        self.template_config.setall('DEFAULT', dict(story_config.items('values')))
        self.template_config.read(template_dir + '/' + self.selected_story + '.ini')

    def next_story(self):
        """
        Updates the selected story to be the next one.
        :return: The name of the story
        """
        return self.set_selected_story(self.selected_story_no + 1)

    def prev_story(self):
        """
        Updates the selected story to be the previous one.
        :return: The name of the story
        """
        return self.set_selected_story(self.selected_story_no - 1)

    def next_page(self):
        """
        Updates the current page to be the next page
        """
        self.current_page_no = min(self.current_page_no + 1, len(self.current_pages) - 1)
        self.current_page = self.current_pages[self.current_page_no]

    def previous_page(self):
        """
        Updates the current page to be the previous page
        """
        self.current_page_no = min(self.current_page_no - 1, len(self.current_pages) - 1)
        self.current_page = self.current_pages[self.current_page_no]

    def build(self):
        self.settings_cls = LibrarySettings
        self.use_kivy_settings = False
        self.title = 'Story Pixies'
        return StoryBase()

    def build_config(self, config):
        config.setdefaults('global', {'template_dir': Path(__file__).parents[0].absolute() / "templates"})
        for library in self.libraries:
            config.setdefaults(library, {
                'name': library,
                'story_dir': Path(__file__).parents[0].absolute() / "libraries" / library,
                'current_book': ''
            })

    def build_settings(self, settings):
        settings.add_json_panel('Global', self.config, data=get_settings_json('global'))
        for library in self.libraries:
            settings.add_json_panel(library.capitalize(), self.config, data=get_settings_json(library))

    def on_config_change(self, config, section, key, value):
        print config, section, key, value

    @staticmethod
    def get_libraries():
        library_list = (Path(__file__).parents[0].absolute() / "libraries")
        return [l.stem for l in library_list.iterdir() if l.is_dir()]

    def get_stories(self, library=None):
        if library is None:
            library = self.selected_library

        story_list = (Path(__file__).parents[0].absolute() / "libraries" / library)
        return [s.stem for s in story_list.iterdir() if s.is_file()]

    def get_story_value(self, page, value):
        return self.template_config.get(page, value)

    def get_story_title(self):
        return self.get_story_value('title', 'name')

    def get_story_media(self):
        return self.get_story_value(self.current_page, 'media_location')

    def get_story_media_type(self):
        return self.get_story_value(self.current_page, 'media')

    def get_story_text(self):
        return self.get_story_value(self.current_page, 'text')


if __name__ == '__main__':
    main_app = StoryPixiesApp()
    main_app.run()
