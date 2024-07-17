def alias(attr):
    def alias_get(self):
        return getattr(self, attr)

    def alias_set(self, value):
        return setattr(self, attr, value)

    return property(alias_get, alias_set)
