from kivy.graphics import Color, Rectangle

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors.drag import DragBehavior

from kivy.uix.button import Button
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.label import Label
from kivy.uix.image import Image

from shell import Shell
from os.path import join

class File(DragBehavior, BoxLayout):
    def __init__(self, text="", is_dir=False, is_phantom=False, **kwargs):
        kwargs['orientation'] = 'vertical'
        if is_phantom:
            kwargs['opacity'] = 0.5
            text = "boo"
        super(File, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (100, 100)

        self.is_dir = is_dir
        self.register_event_type('on_drop')
        self.register_event_type('on_enter')

        with self.canvas:
            self.rect_color = Color(1, 0, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        img_src = "dir.png" if self.is_dir else "file.png"
        self.image = Image(source="resources/"+img_src, mipmap=True)
        self.name = Label(text=text, halign='center',
            shorten=True, text_size=(self.width, None))

        self.add_widget(self.image)
        self.add_widget(self.name)

        self.update_drag()
        self.bind(pos=self.update_drag, size=self.update_drag)

        self.original_idx = None
        self.stackp = None
        self.plane = None

        self.phantom = None
        self.is_phantom = is_phantom

    def update_drag(self, *args):
        self.drag_rectangle = (*self.pos, *self.size)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    # put down
    def on_touch_up(self, touch):
        if self.is_phantom:
            return True

        if self.collide_point(*touch.pos):
            # check if still has phantom to protect
            # against doubled on_touch_up events
            if self.phantom and not touch.is_double_tap:
                self.release(True, touch.pos)
        return super(File, self).on_touch_up(touch)

    # pick up
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or \
                not isinstance(self.parent, StackLayout):
            return super(File, self).on_touch_down(touch)
        
        if self.is_phantom:
            return True

        if touch.is_double_tap:
            if self.is_dir:
                self.dispatch('on_enter')
            # else try open
            return True

        self.stackp = self.parent
        self.plane = self.stackp.parent

        # deal with bug where object is picked up 
        # but not dragged, leaving it floating
        if len(self.plane.children) > 1:
            floaters = (w for w in self.plane.children if 
                isinstance(w, File))
            for f in floaters:
                f.release()

        self.original_idx = self.stackp.children.index(self)
        self.phantom = File(is_phantom=True)

        self.stackp.remove_widget(self)
        self.plane.add_widget(self)
        self.stackp.add_widget(self.phantom, index=self.original_idx)

        return super(File, self).on_touch_down(touch)

    def release(self, check_collision=False, touch_pos=None):
        self.stackp.remove_widget(self.phantom)
        self.phantom = None

        moved = False
        if check_collision:
            for child in self.stackp.children:
                if child.collide_point(*touch_pos) and child.is_dir:
                    self.dispatch('on_drop', child)
                    moved = True

        self.plane.remove_widget(self)
        if not moved:
            self.stackp.add_widget(self, index=self.original_idx)

    def on_drop(src, dst):
        pass

    def on_enter(tgt):
        pass

class FilePlane(FloatLayout):
    def __init__(self, **kwargs):
        super(FilePlane, self).__init__(**kwargs)

        self.stack = StackLayout(padding=30, spacing=25)
        self.stack.size_hint_y = None
        self.stack.bind(minimum_height=self.stack.setter('height'))

        self.size_hint_y = None
        self.stack.bind(height=self.setter('height'))

        self.add_widget(self.stack)
        self.menu = None
        self.menu_file = None

        self.file_opts = ('copy', 'remove')
        self.root_opts = ('paste', 'create file', 'create folder')

    def on_touch_down(self, touch):
        if self.menu:
            on_menu = False
            for btn in self.menu.content.children:
                if btn.collide_point(*touch.pos):
                    btn.dispatch('on_press')
                    on_menu = True
                    break

            self.remove_widget(self.menu)
            self.menu = None
            self.menu_file = None
            if on_menu:
                return True

        if touch.button != 'right':
            return super(FilePlane, self).on_touch_down(touch)

        self.menu = Bubble(orientation='vertical',
            size_hint=(None, None), width=200,
            limit_to=self, show_arrow=False)

        opt_height = 30
        btn_params = {'size_hint_y':None, 'height':opt_height,
            'background_normal':'resources/bar.png',
            'background_color':(0.5,0.5,0.5,0.8)}
        
        for file in self.stack.children:
            if file.collide_point(*touch.pos):
                self.menu_file = file
                break

        menu_options = self.file_opts if self.menu_file else self.root_opts

        for option in menu_options:
            btn = BubbleButton(text=option, **btn_params)
            btn.bind(on_press=self.option)
            self.menu.add_widget(btn)

        self.menu.height = opt_height*len(self.menu.content.children)

        self.menu.pos = (touch.x, touch.y-self.menu.height)
        self.add_widget(self.menu)

        return True

    def option(self, button):
        if self.menu_file:
            print(button.text, self.menu_file.name.text)
        else:
            print(button.text)


class Explorer(BoxLayout):
    def __init__(self, app, **kwargs):
        kwargs['orientation'] = 'vertical'
        super(Explorer, self).__init__(**kwargs)

        self.app = app
        self.app.bind(path=self.update)

        floating = FilePlane()
        self.stack = floating.stack

        self.scroll = ScrollView(do_scroll_x=False, bar_width=8,
            bar_margin=2, scroll_type=['bars'])
        self.scroll.add_widget(floating)

        self.nav_bar = BoxLayout(orientation='horizontal',
            size_hint_y=0.05)

        self.add_widget(self.nav_bar)
        self.add_widget(self.scroll)
        self.update()

    def move(self, src, dst):
        with dst.canvas:
            dst.rect_color = Color(0, 0, 0, 1)

        src, dst = src.name.text, dst.name.text
        print("move", src, "to", dst)
        self.update()

    def enter(self, tgt):
        tgt = tgt.name.text
        self.app.path = join(self.app.path, tgt)

    def navigate(self, button):
        path = ""
        for btn in self.nav_bar.children[::-1]:
            path = join(path, btn.text)
            if btn == button:
                break
        self.app.path = path


    def update(self, app=None, new_path=None):
        if not new_path:
            new_path = self.app.path

        self.nav_bar.clear_widgets()
        for directory in ['/']+new_path.split('/'):
            if directory:
                btn = Button(text=directory)
                btn.bind(on_press=self.navigate)
                self.nav_bar.add_widget(btn)

        self.stack.clear_widgets()
        for file, is_dir in Shell.list_dir(new_path).items():
            if file[0] != '.':            
                f = File(text=file, is_dir=is_dir)
                f.bind(on_drop=self.move)
                f.bind(on_enter=self.enter)
                self.stack.add_widget(f)

class ExplorerScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        kwargs['orientation'] = 'vertical'
        super(ExplorerScreen, self).__init__(**kwargs)

        self.app = app
        self.explorer = Explorer(app=app)
        self.add_widget(self.explorer)
