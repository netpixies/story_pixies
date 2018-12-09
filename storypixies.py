#!/usr/bin/env python
import kivy
import sys
import imghdr

from kivy.lang import Builder
from kivy.uix.settings import SettingOptions, SettingsWithSidebar, SettingItem, SettingSpacer, SettingString
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from pathlib2 import Path
from functools import partial

from kivymd.card import MDCard
from kivymd.grid import SmartTileWithLabel
from storysettings import get_story_settings_title, get_story_settings_page, get_metadata_defaults, get_page_defaults
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.config import ConfigParser
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button

from kivymd.button import MDRaisedButton
from kivymd.label import MDLabel
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager

kivy.require('1.10.1')


class LibrarySettings(SettingsWithSidebar):
    story = ObjectProperty()

    def __init__(self, **kwargs):
        super(LibrarySettings, self).__init__(**kwargs)
        self.register_type('library_options', LibraryOptions)
        self.register_type('story_text', StoryTextOptions)
        self.register_type('page_settings', PageSettings)
        self.register_type('buttons', SettingButtons)


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
            self.app.story_title_screen()

        if instance.ID == "Pages_settings_button":
            self.app.story_pages_screen()

        if instance.ID == "Add_settings_button":
            self.app.creator.add_page(self.panel.config)


class PageSettings(SettingString):
    popup = ObjectProperty(None, allownone=True)

    def on_value(self, instance, value):
        super(PageSettings, self).on_value(instance, value)


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


class Creator(Screen):
    stories = DictProperty()
    settings_panel = ObjectProperty(allownone=True)
    set_story = ObjectProperty()
    set_library = StringProperty()
    story_items = ListProperty()

    def __init__(self, **kwargs):
        super(Creator, self).__init__(**kwargs)
        self.stories = {}
        self.story_items = {}

    def on_pre_enter(self):
        self.settings_panel = None
        self.stories = {}

        for library in self.app.libraries.keys():
            for story in self.app.libraries[library].stories:
                self.add_story(library, story)

        for library in self.app.templates.keys():
            for story in self.app.templates[library].stories:
                self.add_story(library, story)

    def add_page(self, config):
        pages = self.set_story.pages
        if len(pages) == 0:
            new_page = "1"
        else:
            new_page = str(int(pages[-1]) + 1)

        self.set_story.pages.append(new_page)
        title = config.get('metadata', 'story')
        library = config.get('metadata', 'library')
        config.set('metadata', 'pages', "{}".format(','.join(pages[1:])))
        config.setdefaults(new_page, get_page_defaults(new_page))
        self.settings_panel.add_json_panel(new_page, config,
                                           data=get_story_settings_page(title,
                                                                        new_page,
                                                                        library))
        config.write()

    '''
    Settings Panel Methods Start
    '''
    def setup_settings_panel(self):
        self.settings_panel = LibrarySettings()
        self.settings_panel.bind(on_close=self.dismiss_settings_panel)

    def dismiss_settings_panel(self, _):
        self.app.manager.current = 'creator'

    '''
    Edit Story Methods Start
    '''
    def set_edit_selections(self, library, story, _):
        self.edit_story_id.text = "{}: {}".format(library, story.title)
        self.edit_story_id.story = story
        self.edit_story_id.library = library

    def get_edit_stories(self):
        story_item_list = []
        for library in self.app.libraries.keys():
            for story in self.app.libraries[library].stories:
                story_item_list.append({'viewclass': 'MDMenuItem',
                                        'text': "{}: {}".format(library, story.title),
                                        'callback': partial(self.set_edit_selections, library, story)})

        for library in self.app.templates.keys():
            for story in self.app.templates[library].stories:
                story_item_list.append({'viewclass': 'MDMenuItem',
                                        'text': "{}: {}".format(library, story.title),
                                        'callback': partial(self.set_edit_selections, library, story)})
        return story_item_list

    def edit_story(self, edit_story_id):
        if edit_story_id.library is None or edit_story_id.story is None:
            Snackbar("Please select a story to edit first.").show()
            return

        self.set_library = edit_story_id.library
        self.set_story = edit_story_id.story


        self.setup_settings_panel()
        self.app.story_title_screen()

    '''
    Create Story Methods Start
    '''
    def set_new_selections(self, library, _):
        self.new_story_library_id.library = library

    def get_libraries(self):
        library_item_list = []
        for library in self.app.libraries.keys():
            library_item_list.append({'viewclass': 'MDMenuItem',
                                      'text': "{}".format(library),
                                      'callback': partial(self.set_new_selections, library)})
        for library in self.app.templates.keys():
            library_item_list.append({'viewclass': 'MDMenuItem',
                                      'text': "{}".format(library),
                                      'callback': partial(self.set_new_selections, library)})

        return library_item_list

    def add_story(self, library, story):
        self.stories["{}: {}".format(library, story.title)] = {'library': library,
                                                               'story': story}

    def create_new_story(self, name, library):
        if len(name) == 0:
            Snackbar("Please enter a new story name first!").show()
            return

        if library is None:
            Snackbar("Please select a library to add your new story!").show()
            return

        self.set_library = library
        if "{}: {}".format(library, name) in self.stories:
            Snackbar("Cannot create story. '{}' already exists in {}.".format(name, library)).show()
            return

        new_story = self.app.libraries[library].add_new_story(name)

        if new_story is None:
            Snackbar("Could not create new story.").show()
            return

        self.set_story = name

        self.add_story(library, new_story)
        self.set_story = new_story
        self.set_library = library
        self.setup_settings_panel()

        new_page = str(int(self.set_story.pages[-1]))

        self.set_story.story_config.setdefaults(new_page, get_page_defaults(new_page))
        self.settings_panel.add_json_panel(new_page, self.set_story.story_config,
                                           data=get_story_settings_page(self.set_story.title,
                                                                        new_page,
                                                                        library))
        self.set_story.story_config.write()
        self.setup_settings_panel()
        self.app.story_title_screen()

    '''
    Copy Story Methods Start
    '''
    def set_copy_library_selections(self, library, _):
        self.copy_story_library_id.library = library

    def get_copy_libraries(self):
        library_item_list = []
        for library in self.app.libraries.keys():
            library_item_list.append({'viewclass': 'MDMenuItem',
                                      'text': "{}".format(library),
                                      'callback': partial(self.set_copy_library_selections, library)})
        for library in self.app.templates.keys():
            library_item_list.append({'viewclass': 'MDMenuItem',
                                      'text': "{}".format(library),
                                      'callback': partial(self.set_copy_library_selections, library)})

        return library_item_list

    def set_copy_selections(self, library, story, _):
        self.copy_story_from_box.text = "{}: {}".format(library, story.title)
        self.copy_story_from_box.story = story
        self.copy_story_from_box.library = library

    def get_copy_stories(self):
        story_item_list = []
        for library in self.app.libraries.keys():
            for story in self.app.libraries[library].stories:
                story_item_list.append({'viewclass': 'MDMenuItem',
                                        'text': "{}: {}".format(library, story.title),
                                        'callback': partial(self.set_copy_selections, library, story)})

        for library in self.app.templates.keys():
            for story in self.app.templates[library].stories:
                story_item_list.append({'viewclass': 'MDMenuItem',
                                        'text': "{}: {}".format(library, story.title),
                                        'callback': partial(self.set_copy_selections, library, story)})
        return story_item_list

    def copy_story_from_ids(self, copy_story_from_box, copy_story_library_id, copy_story_box):
        source_story = copy_story_from_box.text
        dest_library = copy_story_library_id.library
        new_name = copy_story_box.text

        if source_story is None:
            Snackbar("Please select a source story to copy.").show()
            return

        if dest_library is None:
            Snackbar("Please select a destination library.").show()
            return

        if len(new_name) == 0:
            Snackbar("Please enter a new story name.").show()
            return

        self.copy_story(source_story, dest_library, new_name)

    def copy_story(self, story, library, new_name):
        if "{}: {}".format(library, new_name) in self.stories:
            Snackbar("Cannot create story. '{}' already exists in {}.".format(new_name, library)).show()
            return

        if self.stories[story]['library'] == library:
            source_story_file = Path(self.stories[story]['story'].story_config_file)
            dest_story_file = source_story_file.parent.joinpath("{}.ini".format(new_name))
            dest_story_file.write_bytes(source_story_file.read_bytes())
            new_story = self.app.libraries[library].add_new_story(new_name)
            if new_story is None:
                return None

            self.add_story(library, new_story)
            self.set_story = new_story
            self.set_library = library
            self.setup_settings_panel()
        else:
            source_story_file = Path(self.stories[story]['story'].story_config_file)
            dest_story_file = self.app.library_dir.joinpath(library).joinpath("{}.ini".format(new_name))
            dest_story_file.write_bytes(source_story_file.read_bytes())
            new_story = self.app.libraries[library].add_new_story(new_name)
            if new_story is None:
                return None

            self.add_story(library, new_story)
            self.set_story = new_story
            self.set_library = library
            self.setup_settings_panel()

        self.setup_settings_panel()
        self.app.story_title_screen()

    '''
    Create Library Methods Start
    '''
    def create_new_library(self, library):
        if len(library) == 0:
            Snackbar("Please enter a new library name.").show()
            return

        library_path = self.app.library_dir.joinpath(library)
        if library_path.exists():
            Snackbar("Library already exists. Select new name.").show()
            return

        library_path.mkdir()

        self.app.libraries[library] = SingleLibrary(name=library, library_dir=library_path)
        self.copy_story("Templates: All About You", library, "All About You")
        self.setup_settings_panel()
        self.app.story_title_screen()


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
        story_title_grid = self.story_title_grid
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
        story_pages_grid = self.story_pages_grid
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


class SingleLibrary(Widget):
    # List of StoryBook objects in this library
    stories = ListProperty()

    # The name of this library
    name = StringProperty(None)

    # The currently set story, defaults to the first
    current_story = ObjectProperty(None)

    # This library's directory
    library_dir = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SingleLibrary, self).__init__(**kwargs)
        self.name = kwargs['name']
        self.library_dir = kwargs['library_dir']
        self.stories = []
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

    def set_current_story(self, story):
        story.current_page_no = 0
        self.current_story = story
        return story

    def get_story(self):
        return self.current_story


class LibraryList(Screen):
    def __init__(self, **kwargs):
        """
        Initializes the root widget.
        Sets property defaults.
        Sets selected library as the first found library.
        :param kwargs:
        """
        super(LibraryList, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        library_list_grid = self.library_list_grid
        library_list_grid.clear_widgets()
        for i in self.app.libraries.keys():
            b = SmartTileWithLabel(mipmap=True, source='images/storypixies.png',
                                   text=i, halign='center')
            b._box_label.theme_text_color = 'Custom'
            b._box_label.halign='center'
            b._box_label.font_style='Body1'
            b._box_label.text_color = (1, 1, 1, 1)
            b.bind(on_press=partial(self.app.set_selected_library, i))
            b.bind(on_release=partial(self.app.library_screen))
            library_list_grid.add_widget(b)


class Library(Screen):
    def on_pre_enter(self, *args):
        library_grid = self.library_grid
        library_grid.clear_widgets()
        for story in self.app.get_library_object().stories:
            b = SmartTileWithLabel(mipmap=True, source=story.get_title_image(),
                                   text=story.title)
            b._box_label.theme_text_color = 'Custom'
            b._box_label.text_color = (1, 1, 1, 1)
            b.bind(on_release=partial(self.set_story, story))
            library_grid.add_widget(b)

    def set_story(self, story, _):
        self.app.get_library_object().set_current_story(story)
        self.app.story_screen()


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

        if self.story_config.get('metadata', 'library') != self.library_parent:
            self.story_config.set('metadata', 'library', self.library_parent)

        # Find the media location for this story's title page
        self.title_media_location = self.story_config.get('title', 'media_location')

        # Find all the pages
        self.pages = ['title'] + [x.strip() for x in self.story_config.get('metadata', 'pages').split(',')]
        self.story_config.write()

    def start_page(self):
        """
        Updates the current page to be the first page
        :return:
        """
        self.current_page_no = 0
        self.current_page = self.pages[0]

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

    def get_title_image(self):
        media_location = self.get_story_value(self.pages[0], 'media_location')
        if len(media_location) == 0:
            media_location = 'images/background.png'

        return media_location

    def get_story_media(self):
        media_location = self.get_story_value(self.current_page, 'media_location')
        if len(media_location) == 0:
            media_location = 'images/background.png'

        return media_location

    def get_story_text(self):
        return self.get_story_value(self.current_page, 'text')


class Story(Screen):
    media_property = ObjectProperty(None)
    current_story = ObjectProperty(None)

    def on_pre_enter(self):
        self.current_story = self.app.get_library_object().get_story()
        self.current_story.start_page()
        self.assemble_layout()

    def on_pre_leave(self):
        if self.media_property is not None:
            self.media_property.state = 'stop'

    def assemble_layout(self):
        if self.media_property is not None:
            self.media_property.state = 'stop'

        story_screen = self.story_screen
        story_screen.clear_widgets()

        story_screen.add_widget(self.get_nav_bar())
        story_screen.add_widget(self.get_media_page())
        story_screen.add_widget(self.get_text_page())

    def get_nav_bar(self):
        main_bar = MDCard(size_hint=(1.0, 0.08),
                          pos_hint={'center_x': 0.5, 'center_y': 0.05})
        bar_box = BoxLayout(orientation='horizontal', padding=dp(8))
        back_button = MDRaisedButton(text='Back', theme_text_color='Secondary',
                                     font_style='Title', size_hint_x=None,
                                     width=dp(36), height=self.parent.height,
                                     pos_hint={'center_x': 0.2, 'center_y': 0.5},
                                     on_release=partial(self.prev_page))
        title_label = MDLabel(disabled=True, theme_text_color='Primary', halign='center',
                              height=self.parent.height,
                              pos_hint={'center_x': 0.2, 'center_y': 0.5})
        title_label.text = self.current_story.title
        next_button = MDRaisedButton(text='Next', theme_text_color='Secondary',
                                     font_style='Title', size_hint_x=None,
                                     width=dp(36), height=self.parent.height,
                                     pos_hint={'center_x': 0.2, 'center_y': 0.5},
                                     on_release=partial(self.next_page))

        bar_box.add_widget(back_button)
        bar_box.add_widget(title_label)
        bar_box.add_widget(next_button)
        main_bar.add_widget(bar_box)
        return main_bar

    def get_media_page(self):
        media_card = MDCard(size_hint=(0.5, 0.9),
                            pos_hint={'center_x': 0.75, 'center_y': 0.55})

        source = self.current_story.get_story_media()
        try:
            if len(source) == 0:
                self.media_property = Image(source='images/background.png',
                                        allow_stretch=False, keep_ratio=True)
            if imghdr.what(source) is not None:
                self.media_property = Image(source=source,
                                            allow_stretch=False, keep_ratio=True)
            else:
                self.media_property = VideoPlayer(id=self.current_story.current_page + 'video',
                                                  source=source, state='play',
                                                  options={'allow_stretch': True, 'keep_ratio': True})
        except Exception:
            self.media_property = Image(source='images/background.png',
                                        allow_stretch=False, keep_ratio=True)

        media_card.add_widget(self.media_property)
        return media_card

    def get_text_page(self):
        text_card = MDCard(size_hint=(0.5, 0.9),
                           pos_hint={'center_x': 0.25, 'center_y': 0.55})
        text_label = MDLabel(disabled=True, pos_hint={'center_x': 0.5, 'center_y': 0.5},
                             halign='center', valign='top', theme_color='Secondary',
                             font_style='Body1', size_hint_y=None)
        text_label.text = self.current_story.get_story_text()
        text_card.add_widget(text_label)
        return text_card

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


class StoryPixiesApp(App):
    theme_cls = ThemeManager()
    title = 'Story Pixies'
    manager = ObjectProperty(None)
    creator = ObjectProperty(None)

    story = ObjectProperty(None)
    story_title = ObjectProperty(None)
    story_pages = ObjectProperty(None)

    libraries = DictProperty()
    templates = DictProperty()
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
        self.creator_disabled = kwargs.get('creator_disabled')
        self.library_dir = (Path(__file__).parents[0].absolute()).joinpath("libraries")
        self.add_libraries()

    def build(self):
        kv_file = (Path(__file__).parents[0].absolute()).joinpath("layout.kv")
        root_widget = Builder.load_file(str(kv_file))
        self.title = 'Story Pixies'
        # self.settings_cls = LibrarySettings
        self.use_kivy_settings = False
        self.creator = root_widget.ids.creator
        self.manager = root_widget.ids.manager
        self.use_kivy_settings = False
        return root_widget

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

    def get_library_object(self):
        return self.libraries.get(self.selected_library)

    def set_selected_library(self, library, _=None):
        if library in self.libraries.keys():
            self.selected_library = library
        else:
            self.selected_library = None

    def creator_screen(self):
        if not self.creator_disabled:
            self.switch_screen('creator')
        else:
            Snackbar(text="Creator mode is disabled").show()

    def switch_screen(self, screen_name):
        self.manager.current = screen_name

    def library_screen(self, _):
        self.switch_screen('library_screen')

    def story_screen(self):
        self.switch_screen('story_screen')

    def story_title_screen(self):
        self.switch_screen('story_title')

    def story_pages_screen(self):
        self.creator.setup_settings_panel()
        self.switch_screen('story_pages')

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

Known bug Occassionally, the app will take a long time to
respond upon startup. You can either wait a minute or restart it.
This is an issue with the kivy app.
        """


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'kid-mode':
        StoryPixiesApp(creator_disabled=True).run()
    else:
        StoryPixiesApp().run()
