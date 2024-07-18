import os

def build_path_tree(rel_paths):
    def cross_union(path_parts) -> dict:
        _res = {'_': []}
        for parts in path_parts:
            _len = len(parts)
            if _len == 0:
                continue
            elif _len == 1:
                _res['_'].append(parts[0])
            else:
                level = parts[0]
                if level not in _res:
                    _res[level] = []
                _res[level].append(parts[1:])

        for k, v in _res.items():
            if k == '_':
                continue
            if isinstance(v, list):
                _res[k] = cross_union(v)
        return _res


    path_parts = [os.path.normpath(path).split(os.sep) for path in rel_paths]

    return cross_union(path_parts)

# 示例用法
rel_paths = [
    'a/b/c.txt',
    'a/000.txt',
    '12.txt',
    'a/256.txt',
    'a/b/d.txt'
]

path_tree = build_path_tree(rel_paths)
print(path_tree)
