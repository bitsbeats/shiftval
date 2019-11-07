from inspect import cleandoc


class LintError(Exception):
    """LintError with description."""
    def __init__(self, message, description=None):
        self.set_desc(description)
        super().__init__(message)

    def set_desc(self, description):
        self.description = cleandoc(description or '')
