from nicegui import ui, app, events
import threading
import queue


class NiceViewThread(threading.Thread):
    def __init__(self, processFunc=None, *args, **kwargs):
        super().__init__(daemon=True, *args, **kwargs)
        self.queue = queue.Queue()
        self.event = threading.Event()
        self.process = processFunc

    def run(self):
        """
        Main thread loop
        """
        print("Thread started")
        self.process(self.queue)


class NiceViewBuilder:
    def __init__(self):
        self.viewName = self.__class__.__name__
        self.thread: NiceViewThread = None
        self.timer: ui.timer = None

    def __del__(self):
        if self.timer:
            self.timer.stop()
            self.timer.remove()

    def _timerfunc(self):
        while True:
            try:
                msg = self.thread.queue.get_nowait()
                self.receiver(self.thread.queue, msg)
                self.thread.queue.task_done()
            except queue.Empty:
                if not self.thread.is_alive():
                    self.timer.delete()
                    self.timer = None
                break

    def run_process(self):
        """
        Start the async process
        """
        if self.thread:
            if self.thread.is_alive():
                raise RuntimeError("Thread is already running")

        if self.timer:
            try:
                self.timer.delete()
            except Exception as e:
                print(e)
            self.timer = None
        self.timer = ui.timer(interval=0.2, callback=self._timerfunc)

        self.thread = NiceViewThread(processFunc=self.process)
        self.thread.start()

    def process(self, queue: queue.Queue):
        """
        Async process
        """
        pass

    def receiver(self, queue: queue.Queue, message):
        """
        Queue message receiver
        """
        pass

    @ui.refreshable
    def view(self):
        ui.label("{}".format(__class__))


class NiceApp:
    DEBUG = True
    APP_NAME = "NiceApp"

    def __init__(self, shutdownMenu: bool = True):
        self.shutdownMenu = shutdownMenu
        self.builders: list[NiceViewBuilder] = []
        self.headerLabel: ui.label = None
        self.footerLabel: ui.label = None
        self.defaultView: NiceViewBuilder = None

    def _shutdown(self):
        """
        Shutdown the application
        """
        try:
            app.shutdown()
        except Exception as e:
            ui.notification("Reload有効時はshutdownできません", type="negative")

    def _viewHeader(self):
        """
        Header view
        """
        with ui.header().classes("q-pa-sm"):
            with ui.button(icon="menu").props("size=sm flat color=white"):
                with ui.menu():
                    if self.shutdownMenu:
                        for builder in self.builders:
                            ui.menu_item(
                                builder.viewName,
                                on_click=lambda e: self._viewMain.refresh(
                                    e.sender.text
                                ),
                            )
                        ui.separator()
                        ui.menu_item("Exit", on_click=lambda: self._shutdown())
            self.headerLabel = ui.label("Header")

    @ui.refreshable
    def _viewMain(self, viewName: str = None):
        """
        Main view
        """
        if viewName == None:
            self.defaultView.view()
        else:
            for builder in self.builders:
                if builder.viewName == viewName:
                    builder.view()
                    break

    def _viewFooter(self):
        """
        Footer view
        """
        return
        with ui.footer().classes("q-pa-sm"):
            self.footerLabel = ui.label("Footer")

    def addView(self, builder: NiceViewBuilder, default=True):
        if default:
            self.defaultView = builder
        self.builders.append(builder)

    def view(self):
        self._viewHeader()
        self._viewMain()
        self._viewFooter()
