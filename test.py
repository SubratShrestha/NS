import matplotlib as mpl
from kivy.app import App
import numpy as np
from kivy.lang import Builder
from kivy_matplotlib import MatplotFigure, MatplotNavToolbar
kv = """
BoxLayout:
orientation: 'vertical'

MatplotFigure:
    id: figure_wgt
    size_hint: 1, 0.7
MatplotNavToolbar:
    id: navbar_wgt
    size_hint: 1, 0.3
    figure_widget: figure_wgt
"""

class testApp(App):
    title = "Test Matplotlib"

    def build(self):

        # Matplotlib stuff, figure and plot
        fig = mpl.figure.Figure(figsize=(2, 2))
        t = np.arange(0.0, 100.0, 0.01)
        s = np.sin(0.08 * np.pi * t)
        axes = fig.gca()
        axes.plot(t, s)
        axes.set_xlim(0, 50)
        axes.grid(True)

        # Kivy stuff
        root = Builder.load_string(kv)
        figure_wgt = root.ids['figure_wgt']  # MatplotFigure
        figure_wgt.figure = fig

        return root

testApp().run()