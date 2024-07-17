import json
import os

class JsonMaster:
    def __init__(self, file) -> None:
        self.file = file

    def jsonread(self):
        with open(self.file, 'r', encoding='utf-8') as read:
            return json.load(read)
        
    def jsonwrite(self, dictjs: dict) -> None:
        with open(self.file, 'w', encoding='utf-8') as write:
            json.dump(dictjs, write, indent=4, ensure_ascii=True)

    def jsonadd(self, key, value) -> None:
        with open(self.file, 'r', encoding='utf-8') as read:
            result = json.load(read)
        result[key] = value
        with open(self.file, 'w', encoding='utf-8') as write:
            json.dump(result, write, indent=4, ensure_ascii=True)

    def jsondelete(self, key) -> None:
        with open(self.file, 'r', encoding='utf-8') as read:
            result = json.load(read)
        del result[key]
        with open(self.file, 'w', encoding='utf-8') as write:
            json.dump(result, write, indent=4, ensure_ascii=True)
    
    def jsonadd_dict(self, dictjs: dict) -> None:
        with open(self.file, 'r', encoding='utf-8') as read:
            result = json.load(read)
        result.update(dictjs)
        with open(self.file, 'w', encoding='utf-8') as write:
            json.dump(result, write, indent=4, ensure_ascii=True)

class JsonDC:
    def __init__(self, name) -> None:
        if not name.endswith('.json'):
            raise ValueError
        self.name = name

    def jsoncreate(self, dictjs={}) -> None:
        if os.path.exists(self.name):
            raise ValueError
        else:
            with open(self.name, 'w', encoding='utf-8') as write:
                    json.dump(dictjs, write, indent=4, ensure_ascii=True)
    
    def jsondeletefile(self) -> None:
        if os.path.exists(self.name):
            if self.name.endswith('.json'):
                os.remove(self.name)