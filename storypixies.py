#!/usr/bin/env python
import kivy
import sys

from kivy.lang import Builder
from kivy.uix.settings import SettingOptions, SettingsWithSidebar, SettingItem, SettingSpacer, SettingString
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from pathlib2 import Path
from functools import partial

from kivymd.menu import MDDropdownMenu
from storysettings import get_settings_json, get_story_settings_title, \
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

from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton, MDRaisedButton
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch, BaseListItem
from kivymd.material_resources import DEVICE_TYPE
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationDrawerHeaderBase
from kivymd.selectioncontrols import MDCheckbox
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager

kivy.require('1.10.1')


root_kv = '''
#:import partial functools.partial
#:import Toolbar kivymd.toolbar.Toolbar
#:import ThemeManager kivymd.theming.ThemeManager
#:import MDNavigationDrawer kivymd.navigationdrawer.MDNavigationDrawer
#:import NavigationLayout kivymd.navigationdrawer.NavigationLayout
#:import NavigationDrawerDivider kivymd.navigationdrawer.NavigationDrawerDivider
#:import NavigationDrawerToolbar kivymd.navigationdrawer.NavigationDrawerToolbar
#:import NavigationDrawerSubheader kivymd.navigationdrawer.NavigationDrawerSubheader
#:import MDCheckbox kivymd.selectioncontrols.MDCheckbox
#:import MDSwitch kivymd.selectioncontrols.MDSwitch
#:import MDList kivymd.list.MDList
#:import OneLineListItem kivymd.list.OneLineListItem
#:import TwoLineListItem kivymd.list.TwoLineListItem
#:import ThreeLineListItem kivymd.list.ThreeLineListItem
#:import OneLineAvatarListItem kivymd.list.OneLineAvatarListItem
#:import OneLineIconListItem kivymd.list.OneLineIconListItem
#:import OneLineAvatarIconListItem kivymd.list.OneLineAvatarIconListItem
#:import MDTextField kivymd.textfields.MDTextField
#:import MDSpinner kivymd.spinner.MDSpinner
#:import MDCard kivymd.card.MDCard
#:import MDSeparator kivymd.card.MDSeparator
#:import MDDropdownMenu kivymd.menu.MDDropdownMenu
#:import get_color_from_hex kivy.utils.get_color_from_hex
#:import colors kivymd.color_definitions.colors
#:import SmartTile kivymd.grid.SmartTile
#:import MDSlider kivymd.slider.MDSlider
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab
#:import MDProgressBar kivymd.progressbar.MDProgressBar
#:import MDAccordion kivymd.accordion.MDAccordion
#:import MDAccordionItem kivymd.accordion.MDAccordionItem
#:import MDAccordionSubItem kivymd.accordion.MDAccordionSubItem
#:import MDThemePicker kivymd.theme_picker.MDThemePicker
#:import MDBottomNavigation kivymd.tabs.MDBottomNavigation
#:import MDBottomNavigationItem kivymd.tabs.MDBottomNavigationItem


NavigationLayout:
    id: nav_layout

    MDNavigationDrawer:
        id: nav_drawer
        NavigationDrawerToolbar:
            title: "Navigation Drawer"
        NavigationDrawerIconButton:
            icon: 'checkbox-blank-circle'
            text: 'Help'
            on_release: app.root.ids.manager.current = 'help'
        NavigationDrawerIconButton:
            icon: 'checkbox-blank-circle'
            text: 'Select Library'
            on_release: app.root.ids.manager.current = 'library'
        NavigationDrawerIconButton:
            icon: 'checkbox-blank-circle'
            text: 'Creator'
            on_release: app.root.ids.manager.current = 'creator'
        NavigationDrawerIconButton:
            icon: 'checkbox-blank-circle'
            text: 'Colors'
            on_release: app.root.ids.manager.current = 'colors'

    BoxLayout:
        orientation: 'vertical'
        Toolbar:
            id: toolbar
            title: 'Storypixies'
            md_bg_color: app.theme_cls.primary_color
            background_palette: 'Primary'
            background_hue: '500'
            left_action_items: [['menu', lambda x: app.root.toggle_nav_drawer()]]
            right_action_items: [['dots-vertical', lambda x: app.root.toggle_nav_drawer()]]
        
        ScreenManager:
            id: manager
            Screen:
                name: 'help'
                ScrollView:
                    RstDocument:
                        text: app.intro_text()
            
            Library:
                name: 'library'
                ScrollView:
                    do_scroll_x: False
                    GridLayout:
                        id: 'library_grid'
                        cols: 3
                        row_default_height: (self.width - self.cols*self.spacing[0])/self.cols
                        row_force_default: True
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(4), dp(4)
                        spacing: dp(4)
                        SmartTile:
                            mipmap: True
                            source: 'images/storypixies.png'
                        SmartTile:
                            mipmap: True
                            source: 'images/storypixies.png'
                        SmartTile:
                            mipmap: True
                            source: 'images/storypixies.png'
                        SmartTile:
                            mipmap: True
                            source: 'images/storypixies.png'
                        SmartTile:
                            mipmap: True
                            source: 'images/storypixies.png'
                        SmartTile:
                            mipmap: True
                            source: 'images/storypixies.png'
                        SmartTile:
                            mipmap: True
                            source: 'images/storypixies.png'

            Creator:
                name: 'creator'
                ScrollView:
                    do_scroll_x: False
                    MDList:
                        id: creator_list
                        TwoLineAvatarIconListItem:
                            text: "Edit Stories"
                            secondary_text: "Select a story to edit images, text, pages"
                            CreatorImage:
                                source: './assets/avatar.png'
                            CreatorMenuButton:
                                id: ri_icon
                                icon: 'comment-text'

                        TwoLineListItem:
                            text: "Create or Copy a Story"
                            secondary_text: "Enter a story name, then select 'New Story' to create or choose a story to copy from"                    
            Screen:
                name: 'colors'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(80)
                    center_y: self.parent.center_y
                    MDRaisedButton:
                        size_hint: None, None
                        size: 3 * dp(48), dp(48)
                        center_x: self.parent.center_x
                        text: 'Change theme'
                        on_release: MDThemePicker().open()
                        opposite_colors: True
                        pos_hint: {'center_x': 0.5}
                    MDLabel:
                        text: "Current: " + app.theme_cls.theme_style + ", " + app.theme_cls.primary_palette
                        theme_text_color: 'Primary'
                        pos_hint: {'center_x': 0.5}
                        halign: 'center'

<CreatorMenuButton>:
    app: app
'''



class CreatorMenuButton(IRightBodyTouch, MDIconButton):
    def on_release(self):
        MDDropdownMenu(items=self.app.story_items, width_mult=4).open(self)

class CreatorImage(ILeftBody, Image):
    pass


class Library(Screen):
    pass


class Creator(Screen):
    pass


class SingleLibrary(Widget):

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
        self.library_dir = kwargs['library_dir']
        self.stories = []
        self.current_story = 0
        self.add_stories()

    def add_stories(self):
        i = 0
        for story in self.library_dir.iterdir():
            if story.is_file():
                new_story = StoryBook(library=self.name,
                                      title=story.stem,
                                      location=story,
                                      number=i)
                new_story.load_story_config(self.library_dir)
                self.stories.append(new_story)
            i += 1

    def add_new_story(self, name):
        new_path = self.library_dir.joinpath(name + ".ini")

        new_story = StoryBook(library=self.name,
                              title=name,
                              location=new_path,
                              number=len(self.stories))
        new_story.load_story_config(self.library_dir)

        self.stories.append(new_story)
        return new_story

    def set_current_story(self, num):
        """
        Set the currently running story.
        :param num: The story number to set
        :return: Return the same number
        """
        num %= len(self.stories)
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

        # Set config from story's config file.
        self.story_config.read(str(self.story_config_file))
        if self.story_config.get('metadata', 'story') != self.title:
            self.story_config.set('metadata', 'story', self.title)
            self.story_config.write()

        if self.story_config.get('metadata', 'library') != self.library_parent:
            self.story_config.set('metadata', 'library', self.library_parent)
            self.story_config.write()

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


class StoryPixiesApp(App):
    theme_cls = ThemeManager()
    title = 'Story Pixies'
    manager = ObjectProperty(None)

    story = ObjectProperty(None)
    story_title = ObjectProperty(None)
    story_pages = ObjectProperty(None)

    libraries = DictProperty()
    templates = DictProperty()
    selected_library = StringProperty(None)

    library_dir = ObjectProperty(None)

    story_items = ListProperty(None)

    def __init__(self, **kwargs):
        """
        Initializes the root widget.
        Sets property defaults.
        Sets selected library as the first found library.
        :param kwargs:
        """
        super(StoryPixiesApp, self).__init__(**kwargs)

        # Initialize libraries from files
        self.creator_disabled = kwargs.get('creator_disabled')
        self.library_dir = (Path(__file__).parents[0].absolute()).joinpath("libraries")
        self.add_libraries()
        self.story_items = self.get_edit_stories()

    def build(self):
        root_widget = Builder.load_string(root_kv)
        self.title = 'Story Pixies'
        # self.settings_cls = LibrarySettings
        self.use_kivy_settings = False
        return root_widget

    def get_edit_stories(self):
        story_item_list = []
        for library in self.libraries.keys():
            for story in self.libraries[library].stories:
                story_item_list.append({'viewclass': 'MDMenuItem',
                                        'text': "{}: {}".format(library, story.title)})
        for library in self.templates.keys():
            for story in self.templates[library].stories:
                story_item_list.append({'viewclass': 'MDMenuItem',
                                        'text': "{}: {}".format(library, story.title)})
        return story_item_list

    def add_libraries(self):
        self.libraries = {}
        self.templates = {}

        for library in self.library_dir.iterdir():
            if library.stem != 'Templates':
                self.libraries[library.stem] = SingleLibrary(name=library.stem,
                                                             library_dir=library)
            else:
                self.templates[library.stem] = SingleLibrary(name=library.stem,
                                                             library_dir=library)
        if len(self.libraries.keys()) == 0:
            self.set_selected_library(None)
        else:
            self.set_selected_library(self.libraries.keys()[0])

    def set_selected_library(self, library=None):
        """
        Stores passed library as selected.
        :param library: the library to set as current
        """
        if library in self.libraries.keys():
            self.selected_library = library
        else:
            self.selected_library = None


    @staticmethod
    def intro_text():
        return """
========================
Welcome to Storypixies!
========================
***************
About
***************
Storypixies is a tool to create video self-modeling stories to help children master partially
learned skills. It is particuarly helpful for autistic children, but it can work for anyone!

It can also be used to assemble stories of upcoming events to help children pre-adjust for a big
change. Going on a long trip? Check out *Taking a Trip* stories.

***************
Get Started!
***************
1. Navigate using the menu drop down.
2. Select a library to start reading stories.
3. Select creator to create your own libraries and stories!


**********************
Notes
**********************

- Known bug: Occassionally, the app will take a long time to
 respond upon startup. You can either wait a minute or restart it.
 This is an issue with the kivy app.

        """


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'kid-mode':
        StoryPixiesApp(creator_disabled=True).run()
    else:
        StoryPixiesApp().run()
