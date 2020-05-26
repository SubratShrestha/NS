from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.behaviors import DragBehavior
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
# You could also put the following in your kv file...
kv = '''
<DragLabel>:
    # Define the properties for the DragLabel
    drag_rectangle: self.x, self.y, self.width, self.height
    drag_timeout: 10000000
    drag_distance: 0
    canvas.before:
        Color:
            rgb:0,1,0
        Rectangle:
            size: self.size
            pos:self.pos

FloatLayout:
    # Define the root widget
    DragLabel:
        size_hint: 0.25, 0.2
        
'''


class DragLabel(DragBehavior, FloatLayout):
    pass


class TestApp(App):
    def build(self):
        return Builder.load_string(kv)

TestApp().run()