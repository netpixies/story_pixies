#!/usr/bin/env python
import kivy
from kivy.uix.settings import SettingOptions, SettingsWithTabbedPanel, SettingsWithSidebar, Settings, SettingItem, \
    SettingTitle, SettingsPanel, SettingSpacer, SettingString
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp
from pathlib import Path
from functools import partial
from storysettings import get_settings_json, get_story_settings_metadata, get_story_settings_title, \
    get_story_settings_page, get_metadata_defaults, get_page_defaults
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.config import ConfigParser
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.button import Button

kivy.require('1.10.1')


class MainMenu(GridLayout):
    pass


class LibrarySettings(SettingsWithSidebar):

    story = ObjectProperty()

    def __init__(self, **kwargs):
        super(LibrarySettings, self).__init__(**kwargs)
        self.register_type('library_options', LibraryOptions)
        self.register_type('story_text', StoryTextOptions)
        self.register_type('page_settings', PageSettings)
        self.register_type('buttons', SettingButtons)


class LibraryButton(Button):
    pass


class LibraryOptions(SettingOptions):

    def __init__(self, **kwargs):
        super(LibraryOptions, self).__init__(**kwargs)

    def _create_popup(self, instance):
        story_list = (Path(__file__).parents[0].absolute() / "libraries" / instance.section).glob('**/*.ini')
        self.options = [l.stem for l in story_list]
        super(LibraryOptions, self)._create_popup(instance)


class SettingButtons(SettingItem):

    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(SettingItem, self).__init__(**kwargs)
        o_button = Button(text=kwargs["title"], font_size='15sp')
        o_button.ID = "{}_settings_button".format(kwargs["title"])
        self.add_widget(o_button)
        o_button.bind(on_release=self.setting_button_pressed)

    def set_value(self, section, key, value):
        # set_value normally reads the configparser values and runs on an error
        # to do nothing here
        return

    def setting_button_pressed(self, instance):
        self.panel.settings.dispatch('on_config_change',
                                     self.panel.config,
                                     self.section,
                                     self.key,
                                     instance.ID)
        if instance.ID == "Title_settings_button":
            self.app.story_title_screen(self)

        if instance.ID == "Pages_settings_button":
            self.app.story_pages_screen(self)

        if instance.ID == "Metadata_settings_button":
            self.app.story_metadata_screen(self)

        print "Button hit"


class PageSettings(SettingString):
    popup = ObjectProperty(None, allownone=True)

    def on_value(self, instance, value):
        super(PageSettings, self).on_value(instance, value)
        if instance.parent is not None:
            # self.creator_grid.assemble_layout()
            print "Updated value: {}".format(value)
            print "Instance", instance


class StoryTextOptions(SettingString):
    popup = ObjectProperty(None, allownone=True)

    # Taken from SettingString... I saw no way of overriding the multiline setting
    def _create_popup(self, instance):
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            title=self.title, content=content, size_hint=(None, None),
            size=(popup_width, '250dp'))

        # create the textinput used for numeric input
        self.textinput = textinput = TextInput(
            text=self.value, font_size='24sp', multiline=True,
            size_hint_y=None, height='96sp')
        textinput.bind(on_text_validate=self._validate)
        self.textinput = textinput

        # construct the content, widget are used as a spacer
        content.add_widget(Widget())
        content.add_widget(textinput)
        content.add_widget(Widget())
        content.add_widget(SettingSpacer())

        # 2 buttons are created for accept or cancel the current value
        btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
        btn = Button(text='Ok')
        btn.bind(on_release=self._validate)
        btnlayout.add_widget(btn)
        btn = Button(text='Cancel')
        btn.bind(on_release=self._dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        # all done, open the popup !
        popup.open()


class Home(Screen):

    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)

    def on_enter(self, *args):
        print "Welcome home!"

        library_grid = self.ids.library_grid
        library_grid.clear_widgets()
        for i in self.libraries.keys():
            b = LibraryButton(text=i)
            library_grid.add_widget(b)

        library_grid.bind(minimum_height=library_grid.setter('height'))

        if self.app.menu is not None:
            self.app.menu.storybutton.state = 'normal'
            self.app.menu.creatorbutton.state = 'normal'
            self.app.menu.librarybutton.state = 'normal'


class Library(Screen):

    def on_pre_enter(self):
        """
        Ensure the other buttons are unselected. For some
        reason, multiple toggle buttons wind up selected.
        """
        print "Entering library, shhhh!"
        self.ids.story_button.text = self.app.get_library_object().get_story().title
        self.ids.story_button_image.source = self.app.get_library_object().get_story().title_media_location
        self.app.menu.homebutton.state = 'normal'
        self.app.menu.creatorbutton.state = 'normal'
        self.app.menu.storybutton.state = 'normal'


class SingleLibrary(Widget):
    # Path object of the library directory
    location = ObjectProperty(None)

    # List of StoryBook objects in this library
    stories = ListProperty()

    # The name of this library
    name = StringProperty(None)

    # The currently set story, defaults to the first
    current_story = NumericProperty(None)

    # This library's directory
    library_dir = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SingleLibrary, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.location = kwargs['location']
        self.library_dir = kwargs['library_dir']
        self.stories = []
        self.current_story = 0
        self.add_stories()

    def add_stories(self):
        i = 0
        for story in self.location.iterdir():
            if story.is_file():
                new_story = StoryBook(library=self.name,
                                      title=story.stem,
                                      location=story,
                                      number=i)
                new_story.load_story_config(self.library_dir)
                self.stories.append(new_story)
            i += 1

    def add_new_story(self, name):
        new_path = self.location.joinpath(name + ".ini")
        new_story = StoryBook(library=self.name,
                              title=name,
                              location=new_path)
        new_story.load_story_config(self.library_dir)
        self.stories.append(new_story)

    def set_current_story(self, num):
        """
        Set the currently running story.
        :param num: The story number to set
        :return: Return the same number
        """
        print "Num is {}".format(num)
        num %= len(self.stories)
        print "Setting current story to {}".format(num)
        self.current_story = num
        return num

    def get_story(self, num=None):
        if num is None:
            return self.stories[self.current_story]
        else:
            num %= len(self.stories)
            return self.stories[num]

    def next_story(self):
        """
        Updates the selected story to be the next one.
        :return: The name of the story
        """
        num = self.set_current_story(self.current_story + 1)
        return self.stories[num].title

    def prev_story(self):
        """
        Updates the selected story to be the previous one.
        :return: The name of the story
        """
        num = self.set_current_story(self.current_story - 1)
        return self.stories[num].title


class Story(Screen):
    media_property = ObjectProperty(None)
    current_story = ObjectProperty(None)

    def on_pre_enter(self):
        """
        Ensure the other buttons are unselected. For some
        reason, multiple toggle buttons wind up selected.
        """
        print "Entering Story"
        self.app.menu.homebutton.state = 'normal'
        self.app.menu.creatorbutton.state = 'normal'
        self.app.menu.librarybutton.state = 'normal'
        self.current_story = self.app.get_library_object().get_story()
        self.assemble_layout()

    def on_pre_leave(self):
        if self.media_property is not None:
            self.media_property.state = 'stop'

    def assemble_layout(self):
        if self.media_property is not None:
            self.media_property.state = 'stop'

        top_grid = self.ids.story_book_grid
        top_grid.clear_widgets()
        d = self.get_story_display()
        self.media_property = self.get_media_display()
        story_back_button = Button(text="Back",
                                   bold=True,
                                   size_hint_y=0.05,
                                   background_normal='images/backgrounds/button-blue-normal.png')
        story_next_button = Button(text="Next",
                                   bold=True,
                                   size_hint_y=0.05,
                                   background_normal='images/backgrounds/button-blue-normal.png')
        story_back_button.bind(on_release=self.prev_page)
        story_next_button.bind(on_release=self.next_page)
        top_grid.add_widget(story_back_button)
        top_grid.add_widget(story_next_button)
        top_grid.add_widget(d)
        top_grid.add_widget(self.media_property)

    def prev_page(self, _):
        if self.current_story.current_page == 'title':
            self.app.library_screen(self)
        else:
            self.current_story.previous_page()
            self.assemble_layout()

    def next_page(self, _):
        page_now = self.current_story.current_page_no
        self.current_story.next_page()
        if page_now == self.current_story.current_page_no:
            self.app.library_screen(self)
        else:
            self.assemble_layout()

    def get_story_display(self):
        story_text_label = Label(text=self.current_story.get_story_text(),
                                 text_size=(None, None),
                                 font_size="20sp",
                                 pos_hint={'center_x': 0.5, 'center_y': 100.85},
                                 size_hint_y=1,
                                 halign="center",
                                 valign="middle",
                                 color=(0, 0, 0, 1),
                                 background_color=(0.98, 0.965, 0.719, 1))

        return story_text_label

    def get_media_display(self):
        media_type = self.current_story.get_story_media_type()
        if media_type == 'image':
            return Image(source=self.current_story.get_story_media(), allow_stretch=False, keep_ratio=True)
        elif media_type == 'video':
            return VideoPlayer(id=self.current_story.current_page + 'video',
                               source=self.current_story.get_story_media(), state='play',
                               options={'allow_stretch': True, 'keep_ratio': True})


class StoryBook(Widget):
    # This story's title
    title = StringProperty(None)

    # The story's library
    library_parent = StringProperty(None)

    # The story's library number
    story_number = NumericProperty(None)

    # The current set page by name
    current_page = StringProperty("title")

    # The current set page by number
    current_page_no = NumericProperty(0)

    # List of all pages by name
    pages = ListProperty()

    # The parsed story config
    story_config = ObjectProperty(None)

    # The defaults file
    story_config_file = StringProperty(None)

    # Where is the title media?
    title_media_location = StringProperty(None)

    # What kind of media does the title have, image or video?
    title_media = StringProperty(None)

    def __init__(self, **kwargs):
        """
        Initialize starting values. Set kwargs values.
        Set current page to title and page number to 0.
        :param kwargs:
        title: The title of this story
        library: The name of this story's library
        story_number: This story's library number
        """
        super(StoryBook, self).__init__(**kwargs)
        self.title = kwargs['title']
        self.library_parent = kwargs['library']
        self.story_number = kwargs['number']

        self.current_page = "title"
        self.current_page_no = 0
        self.pages = []
        self.story_config_file = ""

    def load_story_config(self, library_dir):
        self.story_config = ConfigParser()
        story_file_loc = library_dir.joinpath(self.title + '.ini')
        if not story_file_loc.is_file():
            self.story_config.setdefaults('metadata',
                                          get_metadata_defaults(self.title, self.library_parent))
            self.story_config.setdefaults('title',
                                          get_page_defaults(self.title))

        self.story_config_file = str(story_file_loc)
        print ""

        # Set config from story's config file.
        self.story_config.read(str(self.story_config_file))

        # Find the media type (image, video) for this story's title page
        self.title_media = self.story_config.get('title', 'media')

        # Find the media location for this story's title page
        self.title_media_location = self.story_config.get('title', 'media_location')

        # Find all the pages
        self.pages = ['title'] + [x.strip() for x in self.story_config.get('metadata', 'pages').split(',')]

    def next_page(self):
        """
        Updates the current page to be the next page
        """
        self.current_page_no = min(self.current_page_no + 1, len(self.pages) - 1)
        self.current_page = self.pages[self.current_page_no]

    def previous_page(self):
        """
        Updates the current page to be the previous page
        """
        self.current_page_no = min(self.current_page_no - 1, len(self.pages) - 1)
        self.current_page = self.pages[self.current_page_no]

    def get_story_value(self, page, value):
        return self.story_config.get(page, value)

    def get_story_media(self):
        return self.get_story_value(self.current_page, 'media_location')

    def get_story_media_type(self):
        return self.get_story_value(self.current_page, 'media')

    def get_story_text(self):
        return self.get_story_value(self.current_page, 'text')


class Creator(Screen):
    creator_grid = ObjectProperty()
    stories = DictProperty()
    settings_panel = ObjectProperty(allownone=True)
    set_story = ObjectProperty()
    set_library = StringProperty()

    def __init__(self, **kwargs):
        super(Creator, self).__init__(**kwargs)
        self.stories = {}

    def on_pre_enter(self):
        """
        Ensure the other buttons are unselected. For some
        reason, multiple toggle buttons wind up selected.
        """
        print "Welcome to the Creator!"

        self.app.menu.homebutton.state = 'normal'
        self.app.menu.storybutton.state = 'normal'
        self.app.menu.librarybutton.state = 'normal'
        self.settings_panel = None
        self.assemble_layout()

    def get_box_title(self, text='Title'):
        return Button(text=text, bold=True, size_hint_y=0.04,
                                  background_normal='images/backgrounds/button-blue-down.png')

    def get_edit_story_box(self):
        # Edit story Box
        edit_story_box = BoxLayout(orientation='horizontal', padding=20, spacing=10, size_hint_y=0.1)

        edit_story_spinner = Spinner(text='Select Story', bold=True,
                                     values=self.stories.keys(),
                                     background_normal='images/backgrounds/button-blue-normal.png')
        edit_story_submit = Button(text="Submit", bold=True,
                                   background_normal='images/backgrounds/button-blue-normal.png')
        edit_story_submit.bind(on_release=partial(self.load_story, edit_story_spinner))
        edit_story_box.add_widget(Widget())
        edit_story_box.add_widget(Widget())
        edit_story_box.add_widget(edit_story_spinner)
        edit_story_box.add_widget(edit_story_submit)
        return edit_story_box

    def get_copy_story_box(self):
        # Copy Story Box
        copy_story_box = BoxLayout(orientation='horizontal', padding=20, spacing=10, size_hint_y=0.1)
        copy_story_text = TextInput(text='New Story Name')
        copy_story_library_selector = Spinner(text='Library Destination',
                                              values=self.app.libraries.keys(),
                                              bold=True,
                                              background_normal='images/backgrounds/button-blue-normal.png')
        copy_story_story_selector = Spinner(text='Select Story',
                                            values=['New Story'] + self.stories.keys(),
                                            bold=True,
                                            background_normal='images/backgrounds/button-blue-normal.png')
        copy_story_submit = Button(text="Submit", bold=True,
                                   background_normal='images/backgrounds/button-blue-normal.png')
        copy_story_submit.bind(on_release=partial(self.load_copy_story,
                                                  copy_story_story_selector,
                                                  copy_story_library_selector))
        copy_story_box.add_widget(copy_story_text)
        copy_story_box.add_widget(copy_story_story_selector)
        copy_story_box.add_widget(copy_story_library_selector)
        copy_story_box.add_widget(copy_story_submit)
        return copy_story_box

    def assemble_layout(self, **kwargs):
        print "Assembling layout"
        self.creator_grid = self.ids.creator_grid
        self.creator_grid.clear_widgets()
        self.stories = {}

        for library in self.app.libraries.keys():
            for story in self.app.libraries[library].stories:
                self.stories["{}: {}".format(library, story.title)] = {'library': library,
                                                                       'story': story}

        self.creator_grid.add_widget(self.get_box_title(text='Edit a Story!'))
        self.creator_grid.add_widget(self.get_edit_story_box())
        self.creator_grid.add_widget(BoxLayout(orientation='horizontal', size_hint_y=0.04))

        self.creator_grid.add_widget(BoxLayout(orientation='horizontal', size_hint_y=0.04))

        self.creator_grid.add_widget(self.get_box_title(text='Create or Copy Story'))
        self.creator_grid.add_widget(self.get_copy_story_box())

        self.creator_grid.add_widget(BoxLayout(orientation='horizontal', size_hint_y=0.8))

    def load_copy_story(self, story, library, _):
        if story.text == 'Select Story' or story.text == 'Invalid Selection':
            print "Bad value selected"
            story.text = 'Invalid Selection'
            return

        if library.text == 'Library Destination' or library.text == 'Invalid Selection':
            print "Bad value selected"
            library.text = 'Invalid Selection'

        if story.text == 'New Story':
            self.create_new_story(library.text)
        else:
            self.copy_story(story, library.text)

        self.setup_settings_panel()

    def setup_settings_panel(self):
        self.settings_panel = LibrarySettings()

        self.settings_panel.bind(on_close=self.dismiss_settings_panel)
        self.settings_panel.bind(on_config_change=partial(self.story_config_change))

    def dismiss_settings_panel(self, _):
        self.app.creator_screen(self)

    def story_config_change(self, _, config, section, key, value):
        print "Changing config {} {} {} {}".format(config, section, key, value)
        if section == "metadata" and key == "pages":
            print "Changed value is: {}".format(value)
            if value in self.set_story.pages:
                config.set(section, key, value)
            else:
                self.set_story.pages = value.split(',')
            print ""

    def load_story(self, story, _):
        if story.text == 'Select Story' or story.text == 'Invalid Selection':
            print "Bad value selected"
            story.text = 'Invalid Selection'
            return

        self.set_story = self.stories[story.text]['story']
        self.set_library = self.stories[story.text]['library']
        self.setup_settings_panel()

        self.app.story_metadata_screen(self)


class StoryMetadata(Screen):
    story = ObjectProperty()
    library = StringProperty()

    def __init__(self, **kwargs):
        super(StoryMetadata, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.story = self.app.creator.set_story
        self.library = self.app.creator.set_library
        self.assemble_layout()

    def assemble_layout(self, **kwargs):
        print "start"
        story_metadata_grid = self.ids.story_metadata_grid
        story_metadata_grid.clear_widgets()
        self.app.creator.setup_settings_panel()
        self.app.creator.settings_panel.add_json_panel('metadata', self.story.story_config,
                                                       data=get_story_settings_metadata(self.story.title,
                                                                                        self.library))
        story_metadata_grid.add_widget(self.app.creator.settings_panel)
        print "done"

    def add_new_page(self, **kwargs):
        page = kwargs['page']
        story = kwargs['story']
        library = kwargs['library']

        story.story_config.setdefaults(page, {'name': 'New page', 'text': 'New page text',
                                              'media': 'image', 'media_location': 'images/page.png'})
        self.app.creator.settings_panel.create_json_panel(page, story.story_config,
                                                          data=get_story_settings_page(story.title, page, library))
        story.story_config.adddefaultsection(page)
        all_pages = story.story_config.get('metadata', 'pages')

        story.story_config.set('metadata', 'pages', all_pages + ",foobar")
        story.story_config.write()
        self.assemble_layout(story=story, library=library)


class StoryTitle(Screen):
    story = ObjectProperty()
    library = StringProperty()

    def __init__(self, **kwargs):
        super(StoryTitle, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.story = self.app.creator.set_story
        self.library = self.app.creator.set_library
        self.assemble_layout()

    def assemble_layout(self):
        story_title_grid = self.ids.story_title_grid
        story_title_grid.clear_widgets()
        self.app.creator.setup_settings_panel()
        self.app.creator.settings_panel.add_json_panel('title', self.story.story_config,
                                                       data=get_story_settings_title(self.story.title,
                                                                                     self.library))
        story_title_grid.add_widget(self.app.creator.settings_panel)


class StoryPages(Screen):
    pages = StringProperty(None)
    story = ObjectProperty()
    library = StringProperty()

    def __init__(self, **kwargs):
        super(StoryPages, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.story = self.app.creator.set_story
        self.library = self.app.creator.set_library
        self.pages = ','.join(self.story.pages[1:])
        self.assemble_layout()

    def assemble_layout(self):
        story_pages_grid = self.ids.story_pages_grid
        story_pages_grid.clear_widgets()
        self.app.creator.setup_settings_panel()
        for page in self.story.pages[1:]:
            self.app.creator.settings_panel.add_json_panel(page, self.story.story_config,
                                                           data=get_story_settings_page(self.story.title,
                                                                                        page,
                                                                                        self.library))
        story_pages_grid.add_widget(self.app.creator.settings_panel)

    def assemble_edit_story(self, **kwargs):
        story = kwargs['story']
        library = kwargs['library']
        self.setup_settings_panel()

        pages = story.story_config.get('metadata', 'pages').split(',')
        self.app.creator.settings_panel.add_json_panel('title', story.story_config,
                                                       data=get_story_settings_title(story.title, library))
        for page in pages:
            self.app.creator.settings_panel.add_json_panel(page, story.story_config,
                                                           data=get_story_settings_page(story.title, page, library))
        self.creator_grid.add_widget(self.settings_panel)

    def load_story(self, _, text):
        library = self.stories[text]['library']
        story = self.stories[text]['story']

        print "Loading story. Library: {}, story: {}".format(library, story.title)
        self.assemble_layout(story=story, library=library)


class StoryPixiesApp(App):
    manager = ObjectProperty(None)
    home = ObjectProperty(None)
    library = ObjectProperty(None)
    creator = ObjectProperty(None)
    story = ObjectProperty(None)
    story_metadata = ObjectProperty(None)
    story_title = ObjectProperty(None)
    story_pages = ObjectProperty(None)
    menu = ObjectProperty(None)
    top_grid = ObjectProperty(None)

    libraries = DictProperty()
    selected_library = StringProperty(None)

    library_dir = ObjectProperty(None)

    def __init__(self, **kwargs):
        """
        Initializes the root widget.
        Sets property defaults.
        Sets selected library as the first found library.
        :param kwargs:
        """
        super(StoryPixiesApp, self).__init__(**kwargs)

        # Initialize libraries from files
        self.library_dir = (Path(__file__).parents[0].absolute() / "libraries")
        self.add_libraries()

    def add_libraries(self):
        self.libraries = {}

        for library in self.library_dir.iterdir():
            if library.stem != 'Templates':
                print "Adding library {}".format(library.stem)
                self.libraries[library.stem] = SingleLibrary(name=library.stem,
                                                             location=library,
                                                             library_dir=self.library_dir.joinpath(library.stem))

        if len(self.libraries.keys()) == 0:
            self.set_selected_library(None)
        else:
            self.set_selected_library(self.libraries.keys()[0])

    def get_library_object(self, library=None):
        if library is None:
            return self.libraries.get(self.selected_library)
        else:
            return self.libraries.get(library)

    def set_selected_library(self, library=None):
        """
        Stores passed library as selected.
        :param library: the library to set as current
        """
        print "Setting selected library to {}".format(library)
        if library in self.libraries.keys():
            self.selected_library = library
        else:
            self.selected_library = None
        print "Library set"

    def build(self):
        self.title = 'Story Pixies'
        # self.settings_cls = LibrarySettings
        self.use_kivy_settings = False

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

        # Add a creator screen where the user can create new stories
        self.creator = Creator(name='creator')
        self.manager.add_widget(self.creator)

        self.story_metadata = StoryMetadata(name='story_metadata')
        self.manager.add_widget(self.story_metadata)

        self.story_title = StoryTitle(name='story_title')
        self.manager.add_widget(self.story_title)

        self.story_pages = StoryPages(name='story_pages')
        self.manager.add_widget(self.story_pages)

        self.menu = MainMenu()
        self.top_grid = GridLayout(cols=1)
        self.top_grid.add_widget(self.menu)
        self.top_grid.add_widget(self.manager)

        # Initialize the selected library
        self.set_selected_library(self.selected_library)

        return self.top_grid

    def build_config(self, config):
        config.setdefaults('global', {'color': "0,0,0"})
        for library in self.libraries:
            config.setdefaults(library, {
                'name': library,
                'story_dir': str((Path(__file__).parents[0].absolute() / "libraries").joinpath(library))
            })

    def build_settings(self, settings):
        settings.add_json_panel('Global', self.config, data=get_settings_json('global'))

        for library in self.libraries:
            settings.add_json_panel(library.capitalize(), self.config, data=get_settings_json(library))

    def on_config_change(self, config, section, key, value):
        print "Config change of {}. Section: {}, key: {}, value: {}".format(config, section, key, value)

    # Screen switching methods
    def home_screen(self, _):
        self.switch_screen('home', self.menu.homebutton)

    def library_screen(self, _):
        self.switch_screen('library', self.menu.librarybutton)

    def story_screen(self, _):
        self.switch_screen('story', self.menu.storybutton)

    def creator_screen(self, _):
        self.switch_screen('creator', self.menu.creatorbutton)

    def story_metadata_screen(self, _):
        self.creator.setup_settings_panel()
        self.switch_screen('story_metadata', self.menu.creatorbutton)

    def story_title_screen(self, _):
        self.creator.setup_settings_panel()
        self.switch_screen('story_title', self.menu.creatorbutton)

    def story_pages_screen(self, _):
        self.creator.setup_settings_panel()
        self.switch_screen('story_pages', self.menu.creatorbutton)

    def switch_screen(self, screen_name, button):
        print "Switching"
        button.state = 'down'

        self.manager.current = screen_name

    def intro_text(self):
        return """
========================
Welcome to Storypixies!
========================
***************
About
***************
Storypixies is a tool to create video self-modeling stories to help children master partially
learned skills. It is particuarly helpful for autistic children, but it can work for all!

It can also be used to assemble stories of upcoming events to help children pre-adjust for a big
change. Going on a long trip? Check out *Taking a Trip* stories.

***************
Get Started!
***************
1. Choose a library on the right to view the available stories.
2. Choose a story to read.
3. Select 'Creator' to edit current stories, or create your own!

**********************
Note to Peer Reviewers
**********************
Still on the roadmap:

- GUI Refinement
- Default story content
- Start/stop points in videos to eliminate some pre-editing
- Add media from direct capture or from url
- New stories from scratch
- Known bug: occassional freeze on startup, wait or restart it

        """


if __name__ == '__main__':
    StoryPixiesApp().run()
