import io


class DysregnetProgress(io.StringIO):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max = 0
        self.curr = 0
        self.set_progress = None

    def set_max(self, max: int):
        self.max = max

    def write(self, *args, **kwargs):
        try:
            self.curr = int(args[0].split("it")[0])
            self.set_progress(
                (
                    str(self.curr),
                    str(self.max),
                    f"{self.curr} ({self.curr/self.max*100:.2f}%)",
                )
            )
        except:
            self.set_progress(
                (
                    str(self.curr),
                    str(self.max),
                    f"{self.curr} ({self.curr/self.max*100:.2f}%)",
                )
            )
