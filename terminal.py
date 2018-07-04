from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.effects.kinetic import KineticEffect
from shell_code import ShellText, ShellInput
from shell import Shell

class History(BoxLayout):
	def __init__(self, line_height, **kwargs):
		kwargs['orientation'] = 'vertical'
		super(History, self).__init__(**kwargs)

		self.size_hint_y = None
		self.bind(minimum_height=self.setter('height'))
		self.line_args = {'size_hint_y' : None, 'height' : line_height}

	def add_line(self, text):
		self.add_widget(ShellText(text=text, **self.line_args))

class CommandLine(ShellInput):
	def __init__(self, line_height, **kwargs):
		input_args = {'size_hint_y': None,
		 'height': line_height,
		 'on_text_validate': self.on_enter, 
		 'hint_text_color': [1]*3+[0.5],
		 'text_validate_unfocus': False}
		kwargs.update(input_args)
		super(CommandLine, self).__init__(**input_args)
		self.register_event_type('on_command')
		self.register_event_type('on_history_nav')

	def on_enter(self, instance):
		self.dispatch('on_command')

	def on_command(self):
		pass

	def keyboard_on_key_down(self, window, keycode, text, modifiers):
		if keycode[1] in ('up', 'down'):
			self.dispatch('on_history_nav', keycode[1]=='up')
			return True
		elif keycode[1] == 'tab':
			return True
		return super(CommandLine, self).keyboard_on_key_down(
			window, keycode, text, modifiers)

	def on_history_nav(self, up):
		pass

class TerminalScreen(BoxLayout):
	def __init__(self, app, **kwargs):
		kwargs['orientation'] = 'vertical'
		super(TerminalScreen, self).__init__(**kwargs)

		self.shell = Shell(app)
		
		self.line_height = 35
		self.history = History(line_height=self.line_height)
		self.history_pointer = -1
		self.latest_input = ""

		scroll_params = {'do_scroll_x':False,
			'bar_width':8, 'bar_margin':2,
			'scroll_type':['bars']}
		scroll = ScrollView(**scroll_params)
		scroll.scroll_y = 0
		scroll.add_widget(self.history)
		self.add_widget(scroll)

		self.input = CommandLine(line_height=self.line_height)
		self.input.hint_text = "write here"
		self.input.bind(on_command=self.command)
		self.input.bind(on_command=self.shell.command)
		self.input.bind(on_history_nav=self.history_nav)
		self.add_widget(self.input)
		self.input.focus = True

	def command(self, instance):
		if instance.text:
			self.history.add_line(instance.text)
			self.history_pointer = -1
			instance.text = ""

	def history_nav(self, instance, up):
		if up:
			if self.history_pointer == -1:
				self.latest_input = instance.text
			if self.history_pointer < len(self.history.children) - 1:
				self.history_pointer += 1
			instance.text = self.history.children[self.history_pointer].text
		else:
			if self.history_pointer > 0:
				self.history_pointer -= 1
				instance.text = self.history.children[self.history_pointer].text
			elif self.history_pointer == 0:
				self.history_pointer -= 1
				instance.text = self.latest_input
