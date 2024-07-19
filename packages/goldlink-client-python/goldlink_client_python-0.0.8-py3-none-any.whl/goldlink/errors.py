"""The Errors thrown by the GoldLink Client."""


class GoldLinkError(Exception):
    """Base error class for all exceptions raised in this library.
    Will never be raised naked; more specific subclasses of this exception will
    be raised when appropriate."""


class TransactionReverted(GoldLinkError):
    '''
    Class representing transaction reverted error.
    '''

    def __init__(self, transaction_receipt):
        self.transaction_receipt = transaction_receipt
