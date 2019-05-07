import matplotlib.pyplot as plt

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
        if (opt,cri) in self.scores.keys():
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

    def weight_mixture(self, cri_list=None):
        if cri_list is None:
            cri_list=self.criteria()
        for cri in cri_list:
            assert cri in self.criteria(), "No such criterion: {}".format(cri)
        num_cri = len(cri_list)
        for cri in cri_list:
            this_name = str(cri)+"_High"
            this_weight = {c: 1.0/(1.0+num_cri) for c in cri_list}
            this_weight[cri] = this_weight[cri]*2.0
            self.weight_criteria(this_name,this_weight)

    def select_criteria(self,cri_list):
        for cri in cri_list:
            assert cri in self.criteria(), "No such criterion: {}".format(cri)
        new_mcdm = Mcdm(self.options)
        for cri in cri_list:
            for opt in self.options:
                new_mcdm.set_score(opt,cri,self.get_score(opt,cri))
        return(new_mcdm)

    def plot(self):
        width=0.1
        colors=['c','m','y','k','b','r','g']
        fig,ax = plt.subplots()
        for (ii,cri) in enumerate(self.criteria()):
            cri_ind = [jj+ii*width for jj in range(len(self.options))]
            cri_score = [self.get_score(opt,cri) for opt in self.options]
            ax.bar(cri_ind,cri_score,width,color=colors[ii],label=str(cri))
        ax.set_xticks([jj+0.5*ii*width for jj in range(len(self.options))])
        ax.set_xticklabels(self.options)
        ax.legend()
        plt.show()

    def __repr__(self):
        opt_fmt='{:8}'
        cri_name_fmt='{:>8.8}'
        cri_val_fmt='{:8.3f}'
        sep = ' : '
        header = opt_fmt.format('Option') + sep + sep.join([cri_name_fmt.format(cri) for cri in self.criteria()]) + '\n'
        rows = '\n'.join([opt_fmt.format(opt) + sep + sep.join([cri_val_fmt.format(self.get_score(opt,cri)) for cri in self.criteria()]) for opt in self.options]) + '\n'
        row_sep = '='*8 + sep + sep.join(['='*8 for cri in self.criteria()]) + '\n'
        return(header+row_sep+rows+row_sep)

def travel_example():
    travel = Mcdm(('Car','Bus','Train'))
    travel.set_score('Car','Fuel',-1.0)
    travel.set_score('Train','Price',1.0)
    print(travel)
    travel.rescale()
    print(travel)
    travel.weight_criteria('Intuit',{'Fuel': 1.0, 'Price': 0.1})
    print(travel)
    travel.weight_mixture(['Fuel','Price'])
    print(travel)
    print(travel.select_criteria(['Fuel_High','Price_High','Intuit']))
    travel.select_criteria(['Fuel_High','Price_High','Intuit']).plot()
    return(travel)

if __name__=='__main__':
    t=travel_example()
