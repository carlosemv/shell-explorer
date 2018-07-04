import kivy
kivy.require('1.11.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from os.path import expanduser

from terminal import TerminalScreen
from explorer import ExplorerScreen

class ShellExplorer(App):

    path = StringProperty(expanduser('~'))

    def __init__(self, **kwargs):
        super(ShellExplorer, self).__init__(**kwargs)

    def build(self):
        Window.size = (1100, 600)
        Window.top = 100
        Window.left = 100
        Window.bind(on_keyboard=self.on_keypress)

        root = BoxLayout(orientation='horizontal')
        self.explorer_screen = ExplorerScreen(app=self)
        self.terminal_screen = TerminalScreen(app=self, size_hint_x=0.5)

        event_widget = self.explorer_screen.explorer.file_plane
        event_widget.bind(on_remove=self.terminal_screen.on_remove)
        event_widget.bind(on_paste=self.terminal_screen.on_paste)
        event_widget.bind(on_move=self.terminal_screen.on_move)
        
        root.add_widget(self.explorer_screen)
        root.add_widget(self.terminal_screen)

        return root

    def on_keypress(self, window, key, scancode, codepoint, modifier):
        if set(modifier) & {'meta', 'ctrl'} and codepoint in ('q', 'w'):
            self.stop()


if __name__ == '__main__':
    ShellExplorer().run()