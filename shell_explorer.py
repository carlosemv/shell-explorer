import kivy
kivy.require('1.11.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.config import Config
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

        explorer = self.explorer_screen.explorer
        plane = explorer.file_plane
        terminal = self.terminal_screen

        plane.bind(on_remove=terminal.on_remove)
        plane.bind(on_paste=terminal.on_paste)
        plane.bind(on_move=terminal.on_move)
        plane.bind(on_cd=terminal.on_cd)
        plane.bind(on_file=terminal.on_file)
        plane.bind(on_dir=terminal.on_dir)

        terminal.shell.bind(on_update=explorer.update)

        root.add_widget(self.explorer_screen)
        root.add_widget(self.terminal_screen)

        return root

    def on_keypress(self, window, key, scancode, codepoint, modifier):
        if set(modifier) & {'meta', 'ctrl'} and codepoint in ('q', 'w'):
            self.stop()


if __name__ == '__main__':
    Config.set('postproc', 'double_tap_time', 350)
    Config.write()
    ShellExplorer().run()
