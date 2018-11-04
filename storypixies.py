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
        for i in self.libraries:
            print "Library is: " + main_app.get_library(i)
            b = LibraryButton(text=i)
            library_grid.add_widget(b)

        library_grid.bind(minimum_height=library_grid.setter('height'))


class StoryButton(Button):
    pass


class StoryLibrary(Screen):
    books = NumericProperty(10)

    def __init__(self, **kwargs):
        super(StoryLibrary, self).__init__(**kwargs)

    def on_enter(self, *args):
        story_grid = self.ids.story_grid
        for story in main_app.get_stories():
            button_media = main_app.get_story_media('title', str(story))
            b = StoryButton(text=story, background_normal=button_media)
            story_grid.add_widget(b)

        story_grid.bind(minimum_height=story_grid.setter('height'))



class StoryCreator(Screen):
    pass


class StoryBook(Screen):

    media_property = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(StoryBook, self).__init__( **kwargs)

    def on_pre_enter(self, *args):
        self.assemble_layout()

    def assemble_layout(self):
        if self.media_property is not None:
            self.media_property.state = 'stop'

        topgrid = self.ids.story_book_grid
        topgrid.clear_widgets()
        d = self.get_story_display(topgrid)
        self.media_property = self.get_media_display()
        back = Button(text="Back",
                      size_hint_y=0.1,
                      background_normal='images/backgrounds/button.png',
                      bold=True)
        next = Button(text="Next",
                      size_hint_y=0.1,
                      background_normal='images/backgrounds/button.png',
                      bold=True)
        back.bind(on_release=self.prev_page)
        next.bind(on_release=self.next_page)
        topgrid.add_widget(d)
        topgrid.add_widget(self.media_property)
        topgrid.add_widget(back)
        topgrid.add_widget(next)

    def prev_page(self, instance):
        if self.current_page == 'title':
            self.manager.current = 'story_library'
        else:
            main_app.previous_page()
            self.assemble_layout()

    def next_page(self, instance):
        page_now = self.current_page_no
        main_app.next_page()
        if page_now == self.current_page_no:
            self.manager.current = 'story_library'
        else:
            self.assemble_layout()

    def get_story_display(self, topgrid):
        l = Label(text=main_app.get_story_text(),
                  text_size=(None,None),
                  font_size="20sp",
                  pos_hint={'center_x':0.5, 'center_y': 100.85},
                  size_hint_y=1,
                  halign="center",
                  valign="middle")


        return l

    def get_media_display(self):
        media_type = main_app.get_story_media_type()
        if media_type == 'image':
            return Image(source=main_app.get_story_media(), allow_stretch=False, keep_ratio=True)
        elif media_type == 'video':
            return VideoPlayer(id=self.current_page + 'video', source=main_app.get_story_media(), state='play', options={'allow_stretch': True, 'keep_ratio': True})


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
    selected_story = StringProperty("default")
    template_config = ObjectProperty(None)
    story_config = ObjectProperty(None)
    current_page = StringProperty("title")
    current_page_no = NumericProperty(0)
    current_pages = ListProperty([])
    libraries = ListProperty([])
    templates = ListProperty([])

    def __init__(self, **kwargs):
        super(StoryPixiesApp, self).__init__(**kwargs)
        self.set_property_defaults()

    def set_property_defaults(self):
        self.selected_library = "default"
        self.selected_story = "default"
        self.template_config = ConfigParser()
        self.story_config = ConfigParser()
        self.current_page = "title"
        self.current_page_no = 0
        self.current_pages = []
        self.libraries = self.get_libraries()
        self.templates = self.get_templates()

    def set_selected_library(self, library, force=False):
        if library not in self.libraries:
            return

        if self.selected_library == library:
            return

        self.set_property_defaults()
        self.selected_library = library

    def set_selected_story(self, book, force=False):
        if book == self.selected_story and not force:
            print "Not updating story without force flag."
            return

        self.selected_story = book
        self.current_page = "title"
        self.current_page_no = 0

        # Get individual story defaults
        story_dir = (Path(__file__).parents[0].absolute() / "libraries" / self.selected_library)
        story_config = ConfigParser()
        story_config.read(str(story_dir) + '/' + self.selected_story + '.ini')
        self.story_config = story_config

        # Get templatized values
        template_dir = self.config.get('global', 'template_dir')
        template_config = ConfigParser()

        # Interpolate individual story defaults into templatized config
        template_config.setall('DEFAULT', dict(self.story_config.items('values')))
        template_config.read(template_dir + '/' + self.selected_story + '.ini')

        # Set updated config as the current config
        self.template_config = template_config

        # Set the pages in the story
        pages = template_config.get('title', 'pages')
        self.current_pages = ['title'] + [x.strip() for x in pages.split(',')]

    def set_current_page(self, page):
        self.current_page = page

    def next_page(self):
        self.current_page_no = min(self.current_page_no + 1, len(self.current_pages)- 1)
        self.current_page = self.current_pages[self.current_page_no]

    def previous_page(self):
        new_page = min(self.current_page_no - 1, len(self.current_pages)-1)

        self.current_page_no = new_page
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
                'current_book' : ''
            })

    def build_settings(self, settings):
        settings.add_json_panel('Global', self.config, data=get_settings_json('global'))
        for library in self.libraries:
            settings.add_json_panel(library.capitalize(), self.config, data=get_settings_json(library))

    def on_config_change(self, config, section, key, value):
        print config, section, key, value

    @staticmethod
    def get_library_background(library_num=None):
        if library_num is None:
            return "images/backgrounds/" + str(randint(1,4)) + ".png"

    @staticmethod
    def get_templates():
        template_list = (Path(__file__).parents[0].absolute() / "templates")
        return [t.stem for t in template_list.iterdir() if t.is_file()]

    @staticmethod
    def get_libraries():
        library_list = (Path(__file__).parents[0].absolute() / "libraries")
        return [l.stem for l in library_list.iterdir() if l.is_dir()]

    def get_library(self, num=0):
        print "Num is: " + str(num)
        if len(self.libraries) > num:
            return self.libraries[num]
        else:
            return ""

    def get_stories(self, library=None):
        if library is None:
            library = self.selected_library

        story_list = (Path(__file__).parents[0].absolute() / "libraries" / library)
        return [s.stem for s in story_list.iterdir() if s.is_file()]

    def get_story_media(self, page=None, story=None, library=None):
        if page is None:
            page = self.current_page

        if library is None:
            library = self.selected_library

        if story is not None:
            story_dir = (Path(__file__).parents[0].absolute() / "libraries" / library)
            story_config = ConfigParser()
            story_config.read(str(story_dir) + '/' + story + '.ini')
            return story_config.get('values', '_title_media_location')
        else:
            return self.template_config.get(page, 'media_location')

    def get_story_orientation(self, page=None, story=None, library=None):
        if page is None:
            page = self.current_page

        if story is None:
            story = self.selected_story

        if library is None:
            library = self.selected_library

        if self.template_config is None:
            return 'horizontal'
        else:
            return self.template_config.get(page, 'orientation')

    def get_story_media_type(self, page=None, story=None, library=None):
        if page is None:
            page = self.current_page

        if story is None:
            story = self.selected_story

        if library is None:
            library = self.selected_library

        if self.template_config is None:
            return 'images/background.png'
        else:
            return self.template_config.get(page, 'media')

    def get_story_config(self, story=None, library=None):
        print self.template_config.get('defaults', 'name')
        print self.story_config.get('values', '_title_media_location')

    def get_story_text(self, page=None, story=None, library=None):
        if page is None:
            page = self.current_page
        if story is None:
            story = self.selected_story
        if library is None:
            library = self.selected_library

        if self.template_config is None:
            return 'Default Text'
        else:
            print "current page: " + self.current_page
            print "current page no: " + str(self.current_page_no)
            return self.template_config.get(page, 'text')

    def get_story_title(self, story=None, library=None):
        if story is None:
            return self.template_config.get('title', 'name')






if __name__ == '__main__':
    main_app = StoryPixiesApp()
    main_app.run()
