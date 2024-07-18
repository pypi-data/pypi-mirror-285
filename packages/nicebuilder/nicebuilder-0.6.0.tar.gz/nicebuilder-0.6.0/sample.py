from nicegui import ui
from nicebuilder import NiceApp, NiceViewBuilder


class TestView(NiceViewBuilder):
    def view(self):
        ui.label("{}".format(self.viewName))


@ui.page("/")
def view():
    app = NiceApp()
    app.addView(TestView(), default=True)
    app.view()


ui.run()

if __name__ == "__mp_main__":
    print("Start")
