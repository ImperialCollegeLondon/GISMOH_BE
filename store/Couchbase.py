from couchbase import Couchbase, views

## Connection to a database
class CouchbaseStore:
    db = None
    
    def __init__(self, bucket, password=None, host='127.0.0.1'):
        self.db = Couchbase.connect(bucket=bucket,host=host, password=password)
    
    def save(self, obj):
        obj_dict = obj.get_dict()
        obj_dict['type'] = self.get_type()
        
        self.db.set(u"%s:%s" % (obj.get_type() ,obj.get_key()), obj_dict)
    
    def fetch(self, cls, key):
        #edit 
        if type(key).__name__ == 'list' :
            return self.db.get_multi(key)
        else:
            key = '%s:%s' % (cls.__name__, key)
            return self.db.get(key)

    def fetch_objects(self, keys):
        get_class = lambda x: globals()[x]

        _dicts = self.fetch(keys)

        objs = []
        for _dict in _dicts.values():

            cls = get_class(_dict.value['type'])
            obj = cls()
            obj.from_dict(_dict.value)
            objs.append(obj)

        return objs

      
    def get_view(self, name, query = None, limit = None, dev = False):
        
        doc = 'gismoh'
        
        if dev:
            doc = 'dev_gismoh'
        _view = views.iterator.View(self.db, doc, name, query = query)
        return _view
    
    def create_query(self):
        return views.params.Query(full_set=True)
    
    def get_next_from(self, name, limit=None, dev = False, query = None):
        
        _view = self.get_view(name, query, limit, dev = True)
        
        for doc in _view:
            yield doc

    def get_from_view_by_key(self, name, key):
        
        _query = self.create_query()
        _query.mapkey_single = key
        _view = self.get_view(name, _query)
        
        return _view