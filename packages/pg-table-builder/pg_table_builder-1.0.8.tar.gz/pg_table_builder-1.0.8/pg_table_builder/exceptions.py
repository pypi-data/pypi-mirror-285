class ConnectionError(Exception):
    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None
    
    def __str__(self) -> str:
        if self.message is not None:
            return self.message
        else:
            return 'Error connection'

class DisconnectError(Exception):
        def __init__(self, *args) -> None:
            if args:
                self.message = args[0]
            else:
                self.message = None
    
        def __str__(self) -> str:
            if self.message is not None:
                return self.message
            else:
                return 'Connection already closed'


class TablesCreatingError(Exception):
    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        if self.message is not None:
            return self.message
        else:
            return 'Failed to create tables'


class DataTypeError(Exception):
    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        return 'Data type error{}'.format((': ' + self.message)
                                          if self.message is not None else '')


class IncompatibleParameters(Exception):
    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        if self.message is not None:
            'Incompatible parameters{}'.format((': ' + self.message)
                                               if self.message is not None else '')
