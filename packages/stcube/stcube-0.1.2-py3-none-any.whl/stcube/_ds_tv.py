class KVTree:
    def __init__(self, hashble_data, *, parent=None):
        try:
            hash(hashble_data)
        except:
            raise ValueError("[TreeV Init]: The data must be hashable.")
        self.value = hashble_data
        self.children = {}
        self.parent = parent

    def add_child(self, hashble_data: TreeV | object) -> 'KVTree':
        if isinstance(hashble_data, KVTree):
            self.children[hashble_data.value] = hashble_data
            hashble_data.parent = self
            return hashble_data
        else:
            _tv = KVTree(hashble_data, parent=self)
            self.children[_tv.value] = _tv
            return _tv

    def remove_child(self, hashble_data: TreeV | object) -> 'KVTree' | None:
        if isinstance(hashble_data, KVTree):
            self.children.pop(hashble_data.value, None)
            hashble_data.parent = None
            return hashble_data
        else:
            _tv = self.children.pop(hashble_data, None)
            if _tv:
                _tv.parent = None
            return _tv

    def change_parent(self, new_parent: 'KVTree'):
        if self.parent:
            self.parent.remove_child(self)
        new_parent.add_child(self)

    @property
    def item(self):
        return self.value, self.children

    def keys(self):
        return self.children.keys()

    def values(self):
        return self.children.values()

    def items(self):
        return self.children.items()

    @classmethod
    def from_dict(cls, hashble_data, data: dict) -> 'KVTree':
        _tv = cls(hashble_data)
        if not isinstance(data, dict):
            _tv.add_child(data)
            return _tv
        for k, v in data.items():
            _tv.add_child(cls.from_dict(k, v))
        return _tv

    @property
    def dict(self):
        return {self.value: [v.dict for v in self.children.values()]}

    def __repr__(self):
        return f"{self.value}"

    def __str__(self):
        return f"{self.chirldren}"

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, value):
        assert isinstance(value, (KVTree, dict)), "The value must be TreeV or dict."
        if isinstance(value, dict):
            value = KVTree.from_dict(key, value)
        self.add_child(value)

    def __delitem__(self, key):
        self.remove_child(key)

    def __contains__(self, key):
        return key in self.children

    def __len__(self):
        return len(self.children)

    def __bool__(self):
        return bool(self.children)

class KVLTree(KVTree):
    """
    The KVLTree is a key-List[value] linked tree.
    """
    def add_child(self, hashble_data: TreeV | object) -> 'KVLTree':
        if isinstance(hashble_data, KVLTree):
            _old = self.children.get(hashble_data.value)
            if _old and isinstance(_old, list):
                _old.append(hashble_data)
            else:
                self.children[hashble_data.value] = [_old, hashble_data]
            self.children[hashble_data.value] = hashble_data
            hashble_data.parent = self
            return hashble_data
        else:
            _tv = KVLTree(hashble_data, parent=self)
            self.children[_tv.value] = _tv
            return _tv

    def remove_child(self, hashble_data: TreeV | object) -> 'KVLTree' | None:
        if isinstance(hashble_data, KVLTree):
            self.children.pop(hashble_data.value, None)
            hashble_data.parent = None
            return hashble_data
        else:
            _tv = self.children.pop(hashble_data, None)
            if _tv:
                _tv.parent = None
            return _tv

    @property
    def item(self):
        return self.value, [v.item for v in self.children]

    def keys(self):
        return self.children.keys()

    def values(self):
        return self.children.values()

    def items(self):
        return self.children.items()

    @classmethod
    def from_dict(cls, hashble_data, data: dict) -> 'KVLTree':
        _tv = cls(hashble_data)
        if not isinstance(data, dict):
            _tv.add_child(data)
            return _tv
        for k, v in data.items():
            _tv.add_child(cls.from_dict(k, v))
        return _tv
