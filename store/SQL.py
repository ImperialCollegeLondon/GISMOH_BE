class SQLStore:
    def get(self, cls, key):
        keyfield = cls().get_key_field() 
        qry = self.createSelectQuery(cls, keyfield)
        
        obj = False
        print qry

        for row in self.db.execute(qry, [key]) :

            obj = cls()
            obj.from_dict(dict(zip(self.mapping.get_fields(cls.__name__), list(row))))

        if not obj:
            raise NotFoundException()

        return obj
    
    def save(self, obj):
        qry = self.createInsertQuery(obj)
        self.db.execute(qry, obj.get_dict().values())
        self.db.commit()
        
    
    ## find and item of type cls where 
    def find(self, cls, *clauses):
        print clauses
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
            fields = [fld for fld in obj.get_dict()]
            qmarks = ['?' for fld in fields]
        else:
            cls = type(obj)
            table_name = self.mapping.get_table_name(cls.__name__)
            fields = [self.mapping.object_to_db(cls.__name__, fld) for fld in obj.get_dict()]
            qmarks = ['?' for fld in fields]
        
        return 'INSERT INTO %s (%s) VALUES (%s)' % (table_name, ','.join(fields), ','.join(qmarks))
    
    def createUpdateQuery(self, obj):
        if self.mapping is None:
            table_name = type(obj).__name__
            fields = ['%s = ?' % fld for fld in obj.get_dict()]
        else:
            cls = type(obj)
            table_name = self.mapping.get_table_name(cls.__name__)
            fields = ['%s = ?' % self.mapping.object_to_db(cls.__name__, fld) for fld in obj.get_dict()]
            
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
        
class MSSQLStore (SQLStore):
    db = None
    mapping = None
    
    def __init__(self, dbname, mapping = None):
        import pyodbc
        self.db = pyodbc.connect('DSN=%s&Trusted_Connection=True' % dbname)
        self.mapping = mapping

class NotFoundException(Exception):
    def __init__(self, msg = "Item not found"):
        super(Exception, self).__init__(msg)
