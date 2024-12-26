import pathlib
import json

def w(path, mode='w', encoding='utf-8'):
    index = path.rfind('/')
    file = path
    if index != -1:
        path = path[:index]
        file = file[index+1:]
        pathlib.Path(path).mkdir(parents=True, exist_ok=True) 
        return open(path+"/"+file, mode, encoding=encoding)
    return open(path, mode, encoding=encoding)

def r(path, mode='r', encoding='utf-8'):
    with w(path, mode=mode, encoding=encoding) as f:
        return json.load(f)