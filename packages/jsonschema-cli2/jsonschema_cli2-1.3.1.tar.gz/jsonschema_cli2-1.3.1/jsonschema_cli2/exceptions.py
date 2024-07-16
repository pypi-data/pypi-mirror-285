class JsonschemaCliException(Exception):
    def __str__(self):
        return " ".join(self.args)
