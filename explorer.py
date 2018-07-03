from kivy.uix.button import Button
from kivy.uix.behaviors.drag import DragBehavior
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from shell import Shell
from os.path import join

class FileDir(DragBehavior, BoxLayout):
    def __init__(self, text="", is_dir=False, **kwargs):
        kwargs['orientation'] = 'vertical'
        super(FileDir, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (100, 100)

        self.is_dir = is_dir
        self.register_event_type('on_drop')

        with self.canvas:
            Color(1, 0, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        img_src = "dir.png" if self.is_dir else "file.png"
        self.image = Image(source="resources/"+img_src, mipmap=True)
        self.name = Label(text=text)

        self.add_widget(self.image)
        self.add_widget(self.name)

        self.update_drag()
        self.bind(pos=self.update_drag, size=self.update_drag)

        self.original_idx = None
        self.stackp = None
        self.plane = None

        self.phantom = None

    def update_drag(self, *args):
        self.drag_rectangle = (*self.pos, *self.size)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    # put down
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.phantom:
            print("put down", self.name.text)
            self.release(True, touch.pos)
        return super(FileDir, self).on_touch_up(touch)

    # pick up
    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y) and \
                isinstance(self.parent, StackLayout):
            self.stackp = self.parent
            self.plane = self.stackp.parent

            # deal with bug where label is picked up 
            # but not dragged, leaving it floating
            if len(self.plane.children) > 1:
                floaters = (w for w in self.plane.children if 
                    isinstance(w, FileDir))
                for f in floaters:
                    f.release()

            self.original_idx = self.stackp.children.index(self)
            self.phantom = FileDir(text="boo", opacity=0.5)

            print("picked up", self.name.text)
            self.stackp.remove_widget(self)
            self.plane.add_widget(self)
            self.stackp.add_widget(self.phantom, index=self.original_idx)
        return super(FileDir, self).on_touch_down(touch)

    def release(self, check_collision=False, touch_pos=None):
        self.stackp.remove_widget(self.phantom)
        self.phantom = None
        if check_collision:
            for child in self.stackp.children:
                if child.collide_point(*touch_pos):
                    print("collide with", child.name.text)
                    if child.is_dir:
                        self.dispatch('on_drop', child)
        self.plane.remove_widget(self)
        self.stackp.add_widget(self, index=self.original_idx)

    def on_drop(src, dst):
        pass

class Explorer(ScrollView):
    def __init__(self, app, **kwargs):
        scroll_params = {'do_scroll_x':False, 'bar_width':8,
            'bar_margin':2, 'scroll_type':['bars']}
        kwargs.update(scroll_params)
        super(Explorer, self).__init__(**kwargs)

        self.app = app
        self.app.bind(path=self.update)

        self.stack = StackLayout(padding=30, spacing=30)
        self.stack.size_hint_y = None
        self.stack.bind(minimum_height=self.stack.setter('height'))

        floating = FloatLayout()
        floating.size_hint_y = None
        self.stack.bind(height=floating.setter('height'))
        floating.add_widget(self.stack)

        self.add_widget(floating)
        self.update(self.app, self.app.path)

    def move(self, src, dst):
        src, dst = src.name.text, dst.name.text
        print("dropped", src, "on", dst)
        # self.app.path = join(self.app.path, dst)

    def update(self, app, new_path):
        for file, is_dir in Shell.list_dir(new_path).items():
            if file[0] != '.':            
                f = FileDir(text=file, is_dir=is_dir)
                f.bind(on_drop=self.move)
                self.stack.add_widget(f)

class ExplorerScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        kwargs['orientation'] = 'vertical'
        super(ExplorerScreen, self).__init__(**kwargs)

        self.app = app
        self.explorer = Explorer(app=app)
        self.add_widget(self.explorer)
