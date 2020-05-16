import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout

class HomeLayout(FloatLayout):
    def __init__(self):
        super(HomeLayout, self).__init__()

class NeuroStimApp(App):
    def build(self):
        return HomeLayout()


if __name__ == "__main__":
    NeuroStimApp().run()
