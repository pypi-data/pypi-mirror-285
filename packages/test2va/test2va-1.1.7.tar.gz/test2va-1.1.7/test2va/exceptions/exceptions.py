class MasterError(Exception):
    def __init__(self, message: str, events):
        self.message = message
        events.on_error.fire(message, self)
        events.on_finish.fire()


class NoJavaData(MasterError):
    pass


class CapTypeMismatch(MasterError):
    pass


class NodeNotInstalled(MasterError):
    pass


class ExecutionStopped(MasterError):
    pass


class AppiumInstallationError(MasterError):
    pass


class AppiumServerError(MasterError):
    pass


class SRCMLError(MasterError):
    pass


class JSONError(MasterError):
    pass


class ParseError(MasterError):
    pass


class MutatorError(MasterError):
    pass


class GeneratorError(MasterError):
    pass
