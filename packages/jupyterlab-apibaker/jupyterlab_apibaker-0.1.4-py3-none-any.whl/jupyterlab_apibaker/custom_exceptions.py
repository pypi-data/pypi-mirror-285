class Error(Exception):
    pass


class ODSourceNotFound(Error):
    def __init__(self, od_source):
        self.od_source = od_source
        super().__init__(self.od_source)

    def __str__(self):
        return f"The source {self.od_source} has not been found."
