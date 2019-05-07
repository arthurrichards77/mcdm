import matplotlib.pyplot as plt
from IPython.display import HTML

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
        self._criteria = []
    
    def copy(self,reset_scores=False):
        new_mcdm = Mcdm(self.options)
        for (opt,cri) in self.scores.keys():
            new_val = 0.0
            if not reset_scores:
                new_val = self.get_score(opt,cri)
            new_mcdm.set_score(opt,cri,new_val)
        return(new_mcdm)
    
    def __add__(self,other):
        new_mcdm = self.copy()
        for (opt,cri) in other.scores.keys():
            assert (opt in self.options), "No such option: {}".format(opt)
            self_val = self.get_score(opt,cri)
            add_val = other.get_score(opt,cri)
            new_mcdm.set_score(opt,cri,self_val+add_val)
        return(new_mcdm)        
    
    def set_score(self,opt,cri,val):
        """m.set_score(opt,cri,val)

        Set score for option against criterion.
        Will introduce new criterion if not scored
        before, but will fail if option was not
        included at initialization."""
        assert (opt in self.options), "No such option: {}".format(opt)
        self.scores[(opt,cri)]=val
        # and add to critria list
        if not cri in self._criteria:
            self._criteria.append(cri)
            
    def set_scores_dict(self,score_dict):
        """m.set_scores_dict(self,score_dict)
        
        Set multiple scores at once via dictionary.
        Each key should be (opt,cri) and each value
        should be a score.
        Example:
        
        m.set_scores_dict({('Car','Speed'):1,('Car','Comfort'):-1})"""
        for (opt,cri) in score_dict.keys():
            assert (opt in self.options), "No such option: {}".format(opt)
            self.set_score(opt,cri,score_dict[(opt,cri)])
            
    def criteria(self):
        #return(set([cri for (opt,cri) in self.scores]))
        return self._criteria

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

    def _rescale_all(self):
        """Rescale all scores linearly to range [0,1]"""
        new_mcdm = self.copy()
        mn = self.min_score()
        rg = self.max_score() - mn
        for opt in self.options:
            for cri in self.criteria():
                new_val = (self.get_score(opt,cri) - mn)/rg
                new_mcdm.set_score(opt,cri,new_val)
        return(new_mcdm)

    def _rescale_each_col(self):
        """Rescale each column's scores linearly
        such that each column fills range [0,1]"""
        new_mcdm = self.copy()
        for cri in self.criteria():
            mn = self.select_criteria([cri]).min_score()
            rg = self.select_criteria([cri]).max_score() - mn
            for opt in self.options:
                new_val = (self.get_score(opt,cri) - mn)/rg
                new_mcdm.set_score(opt,cri,new_val)
        return(new_mcdm)

    def rescale(self,by_columns=False):
        """Rescale all scores linearly to range [0,1]"""
        if by_columns:
            return(self._rescale_each_col())
        else:
            return(self._rescale_all())

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
    
    def select_options(self,opt_list):
        for opt in opt_list:
            assert opt in self.options, "No such criterion: {}".format(opt)
        new_mcdm = Mcdm(opt_list)
        for cri in self.criteria():
            for opt in opt_list:
                new_mcdm.set_score(opt,cri,self.get_score(opt,cri))
        return(new_mcdm)

    def plot(self,show=True):
        width=0.1
        colors=['c','m','y','k','b','r','g']
        fig,ax = plt.subplots()
        for (ii,cri) in enumerate(self.criteria()):
            cri_ind = [jj+ii*width for jj in range(len(self.options))]
            cri_score = [self.get_score(opt,cri) for opt in self.options]
            ax.bar(cri_ind,cri_score,width,color=colors[ii%len(colors)],label=str(cri))
        ax.set_xticks([jj+0.5*ii*width for jj in range(len(self.options))])
        ax.set_xticklabels(self.options)
        ax.legend()
        if show:
            plt.show()
        return(ax)

    def __repr__(self):
        opt_fmt='{:8}'
        cri_name_fmt='{:>8.8}'
        cri_val_fmt='{:8.3f}'
        sep = ' : '
        header = opt_fmt.format('Option') + sep + sep.join([cri_name_fmt.format(cri) for cri in self.criteria()]) + '\n'
        rows = '\n'.join([opt_fmt.format(opt) + sep + sep.join([cri_val_fmt.format(self.get_score(opt,cri)) for cri in self.criteria()]) for opt in self.options]) + '\n'
        row_sep = '='*8 + sep + sep.join(['='*8 for cri in self.criteria()]) + '\n'
        return(header+row_sep+rows+row_sep)

    def _raw_html(self):
        table_start = '<table>\n'
        header = '<tr><th>{}</th>'.format('Option') + ' '.join(['<th>{}</th>'.format(cri) for cri in self.criteria()]) + '</tr>\n'
        rows = '\n'.join(['<tr><th>{}</th>'.format(opt) + ' '.join(['<td>{:8.3f}</td>'.format(self.get_score(opt,cri)) for cri in self.criteria()]) + '</tr>' for opt in self.options])
        table_stop = '\n</table>\n'
        return(table_start+header+rows+table_stop)

    def to_html(self):
        return(HTML(self._raw_html()))
    
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
