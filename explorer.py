from kivy.uix.button import Button
from kivy.uix.behaviors.drag import DragBehavior
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle

class FileDir(DragBehavior, BoxLayout):
	def __init__(self, **kwargs):
		kwargs['orientation'] = 'vertical'
		super(FileDir, self).__init__(**kwargs)

		with self.canvas:
			Color(0, 0, 0, 1)
			self.rect = Rectangle(pos=self.pos, size=self.size)
		self.bind(pos=self.update_rect, size=self.update_rect)

		self.image = Image(source="resources/dir.png", mipmap=True)
		self.name = Label(text="lalal")

		self.add_widget(self.image)
		self.add_widget(self.name)

	def update_rect(self, *args):
		self.rect.pos = self.pos
		self.rect.size = self.size

class Explorer(StackLayout):
	def __init__(self, **kwargs):
		fixed_args = {'orientation':'lr-tb',
		'padding':30, 'spacing':30}
		kwargs.update(fixed_args)
		super(Explorer, self).__init__(**kwargs)

		for i in range(18):
			d = FileDir(size_hint=(None, None), size=(100,100))
			self.add_widget(d)

class ExplorerScreen(BoxLayout):
	def __init__(self, **kwargs):
		kwargs['orientation'] = 'vertical'
		super(ExplorerScreen, self).__init__(**kwargs)

		self.explorer = Explorer()
		self.explorer.size_hint_y = None
		self.explorer.bind(minimum_height=self.explorer.setter('height'))

		scroll_params = {'do_scroll_x':False, 'bar_width':8,
			'bar_margin':2, 'scroll_type':['bars']}
		scroll = ScrollView(**scroll_params)
		scroll.add_widget(self.explorer)
		self.add_widget(scroll)
