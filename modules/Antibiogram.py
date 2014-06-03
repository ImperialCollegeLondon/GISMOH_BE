##Takes Result objects with Antibiograms and compares them
##
from store.Store import GISMOH_Object

class Antibiogram(GISMOH_Object):
    instance_id = None
    isolate_id = None
    organism = None

    sir_results = {}
    sir_result_identifier = ''

    zone_size_results = {}

    is_resistant = False

    print_number = None
    date_tested = None

    def get_key_field(self):
        return 'instance_id'

    def get_key(self):
        return self.instance_id

    #must always produce the same md5 with the same antibiotics
    def get_result_identifier(self):
        import md5

        res = sorted(self.sir_results, key = lambda x : x)
        h = md5.new()

        for res in self.sir_results:
            h.update('%s:%s' % (res, self.sir_results[res]))

        return h.hexdigest()

    def from_dict(self, _dict):
        import json

        super(Antibiogram, self).from_dict(_dict)

        if type(self.sir_results) == str or type(self.sir_results) == unicode:
            self.sir_results = json.loads(self.sir_results)
        elif self.sir_results is None:
            self.sir_results = {}

        if type(self.zone_size_results) == str or type(self.zone_size_results) == unicode:
            self.zone_size_results = json.loads(self.zone_size_results)
        elif self.zone_size_results is None:
            self.zone_size_results = {}

    def get_dict(self, date_strings = False, obj_strings = False):

        self.sir_result_identifier = self.get_result_identifier()

        self.is_resistant = 'R' in self.sir_results.values()

        pre_dict = super(Antibiogram, self).get_dict(date_strings, obj_strings)

        return pre_dict


    def save(self, store):
        import json

        self.sir_result_identifier = self.get_result_identifier()

        if self.instance_id is None:
            super(Antibiogram, self).save(store)
        else:
            super(Antibiogram, self).update(store)


    @staticmethod
    def find(store, isolate_id, date = None):
        if date is not None:
            ab_list = store.find(Antibiogram, {"field" : "isolate_id", "op":"=", "value" : isolate_id},{"field" : "date_tested", "op":"=", "value" : date})
        else:
            ab_list = store.find(Antibiogram, {"field" : "isolate_id", "op":"=", "value" : isolate_id})

        if len(ab_list) > 0 :
            return ab_list[0]
        else:
            return None


    ## Compare 2 antibiograms and return a similarity score
    # @param ab1 {Antibiogram.Antibiogram}:
    # @param ab2 {Antibiogram.Antibiogram}:
    @staticmethod
    def compare(ab1, ab2, mismatch_penalty = 1.0, gap_penalty = 0.5):

        res1 = ab1.sir_results
        res2 = ab2.sir_results
        mismatches = 0
        gaps = 0
        ttl = 0

        keylist = set(res1.keys() + res2.keys())

        for key in keylist:
            if not res1.has_key(key) or not res2.has_key(key):
                gaps += 1.0
            elif (res1[key] == 'I' or res2[key] == 'I' or res1[key] == '' or res2[key] == '') and res1[key] != res2[key]:
                gaps += 1.0
            elif res1[key] != res2[key]:
                mismatches += 1.0
            ttl += 1

        if len(keylist) < 6 :
            penalty = (6 - len(keylist)) * gap_penalty
        else:
            penalty = 0

        return (1.0 - ((mismatches * mismatch_penalty) + (gaps * gap_penalty)) / ttl) - penalty if ttl > 0 else 0

    @staticmethod
    def get_nearest(db, ab1, n = None, cutoff = 1.0, mismatch_penalty = 1.0, gap_penalty = 0.5):

        results = []

        # replace with one call to self.store.get(Result)
        # we need to somehow narrow down the search? Otherwise this will just take longer and longer to run

        for ab2 in Antibiogram.get_by(db, 'is_resistant', True):

            res = Antibiogram.compare(ab1, ab2, mismatch_penalty, gap_penalty)

            if res >= cutoff:
                results.append({ 'Antibiogram' : ab2, 'similarity' : res })

        if n is not None:
            sorted_results = sorted(results, key = lambda obj : obj['similarity'], reverse = True)
            return sorted_results[0:n]
        else:
            return results


    def getAllWith(self, prop, param):
        pass
