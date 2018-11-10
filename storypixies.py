import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton

from pathlib import Path
from functools import partial
from storysettings import get_settings_json

from kivy.app import App
from kivy.config import ConfigParser

from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.button import Button

kivy.require('1.10.1')


class MainMenu(GridLayout):
    pass


class LibraryButton(Button):
    pass


class Home(Screen):
    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        library_grid = self.ids.library_grid
        library_grid.clear_widgets()
        for i in self.libraries:
            b = LibraryButton(text=i)
            library_grid.add_widget(b)

        library_grid.bind(minimum_height=library_grid.setter('height'))




class Library(Screen):
    def on_enter(self, *args):
        print "Entering library, shhhh!"
    #def __init__(self, **kwargs):
    #    super(Library, self).__init__(**kwargs)

    #def on_pre_enter(self, *args):
    #    print "Pre enter"
    #    self.ids.story_button.text = self.main_app.get_story_title()
    #    self.ids.story_button_image.source = self.main_app.get_story_media()
    #    print self.ids.story_button.text



class Story(Screen):
    def on_enter(self, *args):
        print "Entering Story"


class Creator(Screen):
    def on_enter(self, *args):
        print "Entering Creator"


class StoryPixiesApp(App):
    manager = ObjectProperty(None)
    home = ObjectProperty(None)
    library = ObjectProperty(None)
    creator = ObjectProperty(None)
    story = ObjectProperty(None)
    menu = ObjectProperty(None)
    top_grid = ObjectProperty(None)

    libraries = ListProperty()
    selected_library = StringProperty(None)

    stories = ListProperty()
    selected_story = StringProperty(None)
    selected_story_no = NumericProperty(0)

    current_page = StringProperty("title")
    current_page_no = NumericProperty(0)
    current_pages = ListProperty()

    template_config = ObjectProperty(None)

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

    def build(self):
        self.title = 'Story Pixies'
        self.manager = ScreenManager(transition=FadeTransition())

        # Add a home screen where the user can change libraries
        self.home = Home(name='home')
        self.manager.add_widget(self.home)

        # Add a library screen where the user can browse their stories
        self.library = Library(name='library')
        self.manager.add_widget(self.library)

        # Add a stories screen where the user can read stories
        self.story = Story(name='story')
        self.manager.add_widget(self.story)

        # Add a creator screen where the user can create new stories and templates
        self.creator = Creator(name='creator')
        self.manager.add_widget(self.creator)

        self.menu = MainMenu()
        self.top_grid = GridLayout(cols=1)
        self.top_grid.add_widget(self.menu)
        self.top_grid.add_widget(self.manager)

        # Initialize the selected library
        self.set_selected_library(self.selected_library)

        return self.top_grid

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

    def home_screen(self, button):
        button = self.menu.homebutton
        self.switch_screen('home', button)

    def library_screen(self, _):
        button = self.menu.librarybutton
        self.switch_screen('library', button)

    def story_screen(self, _):
        button = self.menu.storybutton
        self.switch_screen('story', button)

    def creator_screen(self, _):
        button = self.menu.creatorbutton
        self.switch_screen('creator', button)

    def switch_screen(self, screen_name, button):
        print "Switching"
        #if self.manager and screen_name in self.manager.screen_names:
        button.state = 'down'

        self.manager.current = screen_name

    def set_selected_library(self, library):
        """
        Resets the defaults.
        Stores passed library as selected.
        Gets stories for this library.
        Sets selected story to the first.
        :param library: the library to set as current
        """
        print "Setting selected library to {}".format(library)
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
        print "Getting title"
        return self.get_story_value('title', 'name')

    def get_story_media(self):
        return self.get_story_value(self.current_page, 'media_location')

    def get_story_media_type(self):
        return self.get_story_value(self.current_page, 'media')

    def get_story_text(self):
        return self.get_story_value(self.current_page, 'text')


if __name__ == '__main__':
    StoryPixiesApp().run()
