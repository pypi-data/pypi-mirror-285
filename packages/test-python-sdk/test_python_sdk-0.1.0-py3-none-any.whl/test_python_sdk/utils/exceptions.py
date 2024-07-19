class QueryFailedException(Exception):
    """Raised when the query status is not 'success'"""

    def __init__(self, message="Query failed"):
        self.message = message
        super().__init__(self.message)
        
        
class ExecuteFailedException(Exception):
    """Raised when the execute status is not 'success'"""

    def __init__(self, message="Execute failed"):
        self.message = message
        super().__init__(self.message)