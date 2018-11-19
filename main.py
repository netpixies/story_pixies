from storypixies import StoryPixiesApp
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'kid-mode':
        StoryPixiesApp(creator_disabled=True).run()
    else:
        StoryPixiesApp().run()
