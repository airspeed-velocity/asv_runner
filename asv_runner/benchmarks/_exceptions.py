class NotRequired(ImportError):
    """Raised when a requirement is not met"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
