import customtkinter as ctk

text = "Run Tool"
stop_fg = "red"


class RunPageRunButtonWidget(ctk.CTkButton):
    def __init__(self, parent):
        super().__init__(parent, text=text, command=self.run)

        self.root = self.winfo_toplevel()
        self.og_fg = self._fg_color

        self.root.run_butt_ref = self

    def run(self):
        self.configure(text="Stop", fg_color=stop_fg, command=self.stop)
        self.root.run()

    def stop(self):
        self.root.stop()

    def reset(self):
        self.configure(text=text, fg_color=self.og_fg, command=self.run, state="normal")