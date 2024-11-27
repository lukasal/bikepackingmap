class InteractiveSetting:
    def __init__(self, id, group, label, value):
        self.id = id
        self.value = value
        self.group = group
        self.label = label


class BooleanSetting(InteractiveSetting):

    def __init__(self, id, group, label, value):
        super().__init__(id, group, label, value)


class ColorSetting(InteractiveSetting):

    def __init__(self, id, group, label, value):
        super().__init__(id, group, label, value)


class LineColorSetting(InteractiveSetting):

    def __init__(self, id, group, label, value):
        super().__init__(id, group, label, value)


class NumberSetting(InteractiveSetting):

    def __init__(self, id, group, label, value, min_value=0, max_value=100):
        super().__init__(id, group, label, value)
        self.min_value = min_value
        self.max_value = max_value


class TextSetting(InteractiveSetting):

    def __init__(self, id, group, label, value, options=None):
        super().__init__(id, group, label, value)
        self.options = options
