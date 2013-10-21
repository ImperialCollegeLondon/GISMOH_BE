##Takes Result objects with Antibiograms and compares them
class Antibiogram(object):
    
    def __init__(self, store):
        self.store = store
        
    
    ## Compare 2 antibiograms and return a similarity score
    # @param ab1 Store.Result: 
    # @param ab2 Store.Result: 
    def compare(self, ab1, ab2, mismatch_penalty = 1.0, gap_penalty = 0.5):
        res1 = {}
        res2 = {}
        mismatches = 0
        gaps = 0
        ttl = 0
    
        for obj in ab1['result']:
            res1[obj['Antibiotic']] = obj['SIR']
        
        for obj in ab2['result']:
            res2[obj['Antibiotic']] = obj['SIR']  
            
        keylist = set(res1.keys() + res2.keys())
        
        
        for key in keylist:
            if not res1.has_key(key) or not res2.has_key(key):
                gaps += 1.0
            elif (res1[key] == 'I' or res2[key] == 'I' or res1[key] == '' or res2[key] == '') and res1[key] != res2[key]:
                gaps += 1.0
            elif res1[key] != res2[key]:
                mismatches += 1.0
            ttl += 1

        return 1.0 - ((mismatches * mismatch_penalty) + (gaps * gap_penalty)) / ttl

    def get_nearest(self, ab1, n = None, cutoff = 1.0, mismatch_penalty = 1.0, gap_penalty = 0.5):
        
        results = []
        
        
        for doc in self.store.get_next_from('Results'):
            ab2 = self.store.fetch(doc.docid).value
            res = self.compare(ab1, ab2, mismatch_penalty, gap_penalty)
            
            if res >= cutoff:
                results.append({ 'Result' : ab2, 'similarity' : res } )
      
        sorted_results = sorted(results, key = lambda obj : obj['similarity'], reverse = True)
        if n is not None:
            return sorted_results[0:n]
        else:
            return sorted_results
        
            
        
                
            
                
    def getAllWith(self, prop, param):
        pass
