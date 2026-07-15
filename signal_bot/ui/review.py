import tkinter as tk

# evita finestre multiple
_window_open = False


class ReviewWindow:

    def __init__(self, signal):

        global _window_open

        if _window_open:
            raise Exception("Review window already open")

        _window_open = True

        self.signal = signal

        self.root = tk.Tk()
        self.root.title("Trading Signal Review")
        self.root.geometry("420x430")
        self.root.resizable(False, False)

        txt = tk.Text(
            self.root,
            font=("Consolas", 11),
            width=48,
            height=20
        )

        txt.pack(padx=10, pady=10)

        txt.insert("end", self.format_signal())
        txt.configure(state="disabled")

        frame = tk.Frame(self.root)
        frame.pack(pady=8)

        tk.Button(
            frame,
            text="Confirm",
            width=12,
            command=self.confirm
        ).pack(side="left", padx=5)

        tk.Button(
            frame,
            text="Cancel",
            width=12,
            command=self.cancel
        ).pack(side="left", padx=5)

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.cancel
        )

    def format_signal(self):

        s = self.signal

        lines = [

            f"Symbol      : {s['symbol']}",
            f"Side        : {s['side']}",
            f"Order Type  : {s['order_type']}",
            "",
            f"Entry       : {s['entry']}",
            f"SL          : {s['sl']}",
            f"TP1         : {s['tp1']}",
            f"TP2         : {s['tp2']}",
            f"TP3         : {s.get('tp3')}",
            f"BE          : {s.get('be')}",
            "",
            f"Distance    : {s['distance']}",
            f"Lots        : {s['lots']}",
            f"TP Lots     : {s['tp_lots']}",
            f"BE Pips     : {s['bepips']}",
        ]

        return "\n".join(lines)

    def confirm(self):

        global _window_open

        print()
        print("===================================")
        print("Signal confirmed")
        print("Use Ctrl+Shift+q on cTrader")
        print("===================================")
        print()

        _window_open = False

        self.root.destroy()

    def cancel(self):

        global _window_open

        print("Signal cancelled")

        _window_open = False

        self.root.destroy()

    def show(self):

        self.root.mainloop()