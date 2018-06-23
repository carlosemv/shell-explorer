import kivy
kivy.require('1.11.0')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

from terminal import TerminalScreen
from explorer import ExplorerScreen

class ShellExplorer(App):

	def build(self):
		Window.size = (1000, 600)
		Window.top = 100
		Window.left = 100
		Window.bind(on_keyboard=self.on_keypress)

		root = BoxLayout(orientation='horizontal')
		self.explorer = ExplorerScreen()
		self.shell = TerminalScreen(size_hint_x=0.5)
		root.add_widget(self.explorer)
		root.add_widget(self.shell)

		return root

	def on_keypress(self, window, key, scancode, codepoint, modifier):
		if set(modifier) & {'meta', 'ctrl'} and codepoint in ('q', 'w'):
			self.stop()


if __name__ == '__main__':
	ShellExplorer().run()