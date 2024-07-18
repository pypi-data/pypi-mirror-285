class AttributDict(dict):
    def __getattr__(self, key):
        if key in self:
            value = self[key]
            if isinstance(value, dict):
                return AttributDict(value)  # Convertir les sous-dictionnaires aussi
            return value
        raise AttributeError(f"'AttributDict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(f"'AttributDict' object has no attribute '{key}'")
