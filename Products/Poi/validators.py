from Products.validation.interfaces import ivalidator


class AtLeastOneValidator:
    # For the DataGridFields, making them required is not enough as
    # there is always a hidden entry.  So we check if there is least
    # one normal entry and one hidden entry, so more than 1 entry in
    # total.

    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        length = len(value) - 1
        if length > 0:
            return 1
        return ("Validation failed(%s): Need at least one entry."
                % self.name)
