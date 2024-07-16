from ptodata2406cConfig import JGTML240615Config

class JGTML240615Request:
    """
    Request class for the JGTML240615 prototype.
    """

    def __init__(self,
                 config: JGTML240615Config,
                 ):
        """
        Initialize the JGTML240615Request object.

        Args:
            config: The configuration object for the prototype.
        """

        self.config = config