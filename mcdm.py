class Mcdm:
    """m = Mcdm(opts)

    Multicriteria decision making aid
    following the 'Pugh' scoring approach
    starting with 'opts' as a tuple of option
    identifiers.

    Example:
      m = Mcdm(('Car', 'Bus', 'Train'))"""

    def __init__(self,opts):
        self.options = opts
        self.scores = {}
    
    def set_score(self,opt,cri,val):
        """m.set_score(opt,cri,val)

        Set score for option against criterion.
        Will introduce new criterion if not scored
        before, but will fail if option was not
        included at initialization."""
        assert (opt in self.options), "No such option: {}".format(opt)
        self.scores[(opt,cri)]=val
            
    def criteria(self):
        return(set([cri for (opt,cri) in self.scores]))

    def get_score(self,opt,cri):
        assert (opt in self.options), "No such option: {}".format(opt)
        assert (cri in self.criteria()), "No such criterion: {}".format(cri)
        val = 0.0
        if self.scores.has_key((opt,cri)):
            val = self.scores[(opt,cri)]
        return(val)

    def max_score(self):
        return(max([max([self.get_score(opt,cri) for opt in self.options])
 for cri in self.criteria()]))

    def min_score(self):
        return(min([min([self.get_score(opt,cri) for opt in self.options])
 for cri in self.criteria()]))

    def rescale(self):
        """Rescale all scores linearly to range [0,1]"""
        mn = self.min_score()
        rg = self.max_score() - mn
        for opt in self.options:
            for cri in self.criteria():
                new_val = (self.get_score(opt,cri) - mn)/rg
                self.set_score(opt,cri,new_val)

    def weight_criteria(self,name,weights):
        for cri in weights.keys():
            assert cri in self.criteria(), "No such criterion: {}".format(cri)
        for opt in self.options:
            new_score = sum([weights[cri]*self.get_score(opt,cri) for cri in weights.keys()])
            self.set_score(opt,name,new_score)

    def weight_mixture(self):
        num_cri = len(self.criteria())
        for cri in self.criteria():
            this_name = str(cri)+"_High"
            this_weight = {c: 1.0/(1.0+num_cri) for c in self.criteria()}
            this_weight[cri] = this_weight[cri]*2.0
            self.weight_criteria(this_name,this_weight)

    def __repr__(self):
        sep = ' : '
        header = 'Option' + sep + sep.join(self.criteria()) + '\n'
        rows = '\n'.join([str(opt) + sep + sep.join([str(self.get_score(opt,cri)) for cri in self.criteria()]) for opt in self.options])
        return(header+rows)

travel = Mcdm(('Car','Bus','Train'))
travel.set_score('Car','Fuel',-1.0)
travel.set_score('Train','Price',1.0)
print(travel)

travel.rescale()
print(travel)

travel.weight_mixture()
travel.weight_criteria('Intuit',{'Fuel': 1.0, 'Price': 0.1})
print(travel)
