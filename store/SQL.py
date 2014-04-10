class SQLStore(object):
    def get(self, cls, key):
        keyfield = cls().get_key_field() 
        qry = self.createSelectQuery(cls, keyfield)
        
        obj = False

        for row in self.db.execute(qry, [key]) :

            obj = cls()
            obj.from_dict(dict(zip(self.mapping.get_fields(cls.__name__), list(row))))

        if not obj:
            return None

        return obj
    
    def get_by(self, cls, fld, val):
        qry = self.createSelectQuery(cls, fld)
        
        objs = []

        for row in self.db.execute(qry, [val]) :

            obj = cls()
            obj.from_dict(dict(zip(self.mapping.get_fields(cls.__name__), list(row))))
            objs.append(obj)

        return objs
    
    def save(self, obj):
        import json
        qry = self.createInsertQuery(obj)
        
        cur = self.db.execute(qry, [obj.get_dict(obj_strings=True).values()])
        self.db.commit()
        return cur
    
    def update(self, obj):
        qry = self.createUpdateQuery(obj)
        
        d = obj.get_dict(obj_strings=True)
        d.pop(obj.get_key_field(), None)
        
        cur = self.db.execute(qry,  d.values() + [obj.get_key()])
        self.db.commit()
        return cur
        
    
    ## find and item of type cls where 
    def find(self, cls, *clauses):
        
        qry = self.createSelectQuery(cls, *clauses)

        objs = []

        for row in self.db.execute(qry, [clause['value'] for clause in clauses]):
            obj = cls()
            obj.from_dict(dict(zip(self.mapping.get_fields(cls.__name__), list(row))))
            objs.append(obj)

        return objs


    def createInsertQuery(self, obj):
        if self.mapping is None:
            table_name = type(obj).__name__
            
            _dict = obj.get_dict()
            
            fields = [fld for fld in _dict if _dict[fld] is not None]
            qmarks = ['?' for fld in fields]
        else:
            cls = type(obj)
            table_name = self.mapping.get_table_name(cls.__name__)
            fields = [self.mapping.object_to_db(cls.__name__, fld) for fld in obj.get_dict()]
            qmarks = ['?' for fld in fields]
        
        return 'INSERT INTO %s (%s) VALUES (%s)' % (table_name, ','.join(fields), ','.join(qmarks))
    
    def createUpdateQuery(self, obj):
        d = obj.get_dict()
        d.pop(obj.get_key_field(), None)
        
        if self.mapping is None:
            table_name = type(obj).__name__
            fields = ['%s = ?' % fld for fld in d]
        else:
            cls = type(obj)
            table_name = self.mapping.get_table_name(cls.__name__)
            fields = ['%s = ?' % self.mapping.object_to_db(cls.__name__, fld) for fld in d]
            
        return 'Update %s SET %s WHERE %s = ?' % (table_name, ','.join(fields), obj.get_key_field())
    
    def createSelectQuery(self, cls, *args):
        if self.mapping is None: #if no mapping is specified for this class then infer the fields from the object
            table_name = cls.__name__
            fields = [fld for fld in cls.__dict__ if type(cls.__dict__[fld]).__name__ != 'function' and type(cls.__dict__[fld]).__name__ != 'staticmethod' and fld[0:2] != '__']
            
        else: # if there is a mapping
            table_name = self.mapping.get_table_name(cls.__name__)
            fields = self.mapping.get_columns(cls.__name__)


        where_clause = [self.get_where_clause(cls, a) for a in args]
        
        return 'SELECT %s FROM %s WHERE %s' % (','.join(fields), table_name, ' and '.join(where_clause))
    
    def get_where_clause(self, cls, arg):

        if type(arg) == str or type(arg) == unicode:
            return u'%s = ?' % (self.mapping.object_to_db(cls.__name__, arg) if self.mapping is not None else arg)
        else:
            return u'%s %s ?' %  (self.mapping.object_to_db(cls.__name__, arg['field']) if self.mapping is not None else arg['field'], arg['op'])

class SQLiteStore (SQLStore):
    db = None
    mapping = None
    
    def __init__(self, dbname, mapping = None):
        import sqlite3
        self.db = sqlite3.connect('%s.db' % dbname)
        self.mapping = mapping
        
    def save(self, obj):
        cur = super(SQLiteStore, self).save(obj)
        
        return cur.lastrowid
    
    def executescript(self, sql):
        return self.db.executescript(sql)
        
class MSSQLStore (SQLStore):
    db = None
    mapping = None
    
    def __init__(self, dbname, mapping = None):
        import pyodbc
        self.db = pyodbc.connect('DSN=%s&Trusted_Connection=True' % dbname)
        self.mapping = mapping
        
    def save(self, obj):
        super(MSSQLStore, self).save(obj)
        
        _id = None
        for row in self.db.execute("SELECT @@IDENTITY as id"):
            _id = row['id']
            
        return _id

class NotFoundException(Exception):
    def __init__(self, msg = "Item not found"):
        super(Exception, self).__init__(msg)
