import json
from .json_attributdict import AttributDict

class setup():



    def __init__(self, paths: dict[str: str], encode: str = 'utf-8', newline: str = ''):

        self._proprietes_dynamiques = {}
        self.paths = paths
        self.encode = encode
        self.newline = newline

        for i in paths.keys():
            self.__load_json(i, paths[i])


    def __load_json(self, name, path_):
        with open('../'+path_, 'r', encoding=self.encode, newline=self.newline, errors='ignore') as f:
            file = json.load(f)

            self._proprietes_dynamiques[name] = AttributDict(file)


    def __getattr__(self, key):

        # Cette méthode est appelée uniquement si l'attribut n'est pas trouvé normalement
        if key in self._proprietes_dynamiques:
            return self._proprietes_dynamiques[key]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


    def __delattr__(self, item):
        if item in self._proprietes_dynamiques:
            del self._proprietes_dynamiques[item]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")


    def write(self):

        for i in self.paths.keys():

            with open('../'+self.paths[i], 'w', encoding=self.encode, newline=self.newline, errors='ignore') as f:
                json.dump(self._proprietes_dynamiques[i], f, indent=2)

        return True

