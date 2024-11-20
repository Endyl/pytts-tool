class Types:
    def __init__(self):
        self.save_all = set()
        self.save_common = None
        self.save_types = {}
        self.save_subtypes = {}

        self.object_all = set()
        self.object_common = None
        self.object_types = {}
        self.object_subtypes = {}


    def extract_save(self, data):
        self.save_all |= set(data.keys())
        if self.save_common is None:
            self.save_common = set(data.keys())
        else:
            self.save_common &= set(data.keys())

        for k, v in data.items():
            if k == 'ObjectStates':
                continue

            if k not in self.save_types:
                self.save_types[k] = set()

            self.save_types[k].add(type(v).__name__)
            if isinstance(v, dict):
                self.extract_save_subtypes(k, v)
            elif isinstance(v, list):
                for i in v:
                    if isinstance(i, dict):
                        self.extract_save_subtypes(k, i)


        for object in data['ObjectStates']:
            self.extract_object(object)


    def extract_save_subtypes(self, key, data):
        for k, v in data.items():
            ck = f'{key}-{k}'
            if ck not in self.save_subtypes:
                self.save_subtypes[ck] = set()
            self.save_subtypes[ck].add(type(v).__name__)


    def extract_object(self, data):
        self.object_all |= set(data.keys())
        if self.object_common is None:
            self.object_common = set(data.keys())
        else:
            self.object_common &= set(data.keys())

        name = data['Name']
        if name not in self.object_types:
            self.object_types[name] = {}

        for k, v in data.items():
            if k == 'ContainedObjects':
                continue

            if k not in self.object_types[name]:
                self.object_types[name][k] = set()

            self.object_types[name][k].add(type(v).__name__)
            if isinstance(v, dict):
                self.extract_object_subtypes(name, k, v)
            elif isinstance(v, list):
                for i in v:
                    if isinstance(i, dict):
                        self.extract_object_subtypes(name, k, i)

        for object in data.get('ContainedObjects', []):
            self.extract_object(object)


    def extract_object_subtypes(self, name, key, data):
        if name not in self.object_subtypes:
            self.object_subtypes[name] = {}

        for k, v in data.items():
            ck = f'{key}-{k}'
            if ck not in self.object_subtypes:
                self.object_subtypes[name][ck] = set()
            self.object_subtypes[name][ck].add(type(v).__name__)


    def serialize(self):
        floatset = set(['int', 'float'])
        def normlist(v):
            v = list(v)
            if 1 == len(v):
                return v[0]
            elif 1 < len(v):
                if v == floatset:
                    return 'float'
                return sorted(v)
            else:
                return None

        def sortdict(v):
            return dict(sorted(v.items()))

        object_types = {}
        for name, typedict in self.object_types.items():
            objdict = sortdict({k: normlist(v) for k, v in typedict.items()})
            objdict['#common'] = {}
            for k in (self.object_common or []):
                objdict['#common'][k] = objdict.pop(k, None)
            object_types[name] = objdict

        object_subtypes = {}
        for name, typedict in self.object_subtypes.items():
            object_subtypes[name] = sortdict({k: normlist(v) for k, v in typedict.items()})

        return {
            'save_all': sorted(list(self.save_all)),
            'save_common': sorted(list(self.save_common or [])),
            'save_types': sortdict({k: normlist(v) for k, v in self.save_types.items()}),
            'save_subtypes': sortdict({k: normlist(v) for k, v in self.save_subtypes.items()}),

            'object_all': sorted(list(self.object_all)),
            'object_common': sorted(list(self.object_common or [])),
            'object_types': sortdict(object_types),
            'object_subtypes': sortdict(object_subtypes),
        }
