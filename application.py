import tornado.ioloop
import tornado.web

import json
from os import path
import uuid

from sec.basic import require_basic_auth
from sec import ldapauth

from store import Store
from modules.Antibiogram import Antibiogram

print 'started'

##Index page handler
@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        
#         rows = cb.query('dev_wards', 'WardList')
#         
#         rowout = ''
#         for row in rows:
#             rowout = '%s, %s' % (rowout, row.key)
        
        self.render('main.html')#,test_val=rowout)
        
#     def post(self):
#         self.set_header('Content-type', 'application/json')
#         cb.set(str(uuid.uuid4()), self.request.arguments)
#         self.write(json.dumps(self.request.arguments))

@require_basic_auth('GISMOH', ldapauth.auth_user_ldap)
class Antibiogram_Test(tornado.web.RequestHandler):
    def get(self):
        
        try:
            iso_id = float(self.get_argument('isolate_id'))
        except (tornado.web.MissingArgumentError):
            iso_id = 1.0

        
        _store = Store.Store('GISMOH', 'gismoh2')
  
        _abm = Antibiogram(_store)
        
        abs = _store.get_from_view_by_key('Results', iso_id)
        
        aaaaa = []
        ab_list = []
        
        for ab_i in abs :
            
            ab = _store.fetch(ab_i.docid).value

            ab_list = ab_list + [x['Antibiotic'] for x in ab['result']]
            
            aaaaa = _abm.get_nearest(ab, None, 11.5/12.0, gap_penalty = 0.25)
    
        self.render('antibiograms.html',antibiotics = ab_list, antibiograms=aaaaa)
    

settings = dict(
   template_path = path.join(path.dirname(__file__), "templates"),
   static_path = path.join(path.dirname(__file__), "static"),
   debug = True
)

application = tornado.web.Application([
    (r'/antibiogram_test', Antibiogram_Test),
    (r"/", MainHandler)
], **settings)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()