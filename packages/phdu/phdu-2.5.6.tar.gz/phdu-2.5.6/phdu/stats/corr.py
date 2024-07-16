"""
Correlation metrics
"""
import pandas as pd
import numpy as np
try:
    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell': # script being run in Jupyter notebook
        from tqdm.notebook import tqdm
    elif shell == 'TerminalInteractiveShell': #script being run in iPython terminal
        from tqdm import tqdm
except NameError:
    from tqdm import tqdm # Probably runing on standard python terminal. If does not work => should be replaced by tqdm(x) = identity(x)

def corr_pruned(df, method='spearman', alpha=0.05, ns_to_nan=True):
    """
    Returns correlation between DataFrame features with pvalue < alpha.
    """
    import scipy.stats as ss
    corr_func = getattr(ss, f"{method}r")
    c = {}
    p = {}
    for col1 in tqdm(df.columns):
        for col2 in df.columns:
            if (col1, col2) in c or (col2, col1) in c:
                continue
            elif col1 == col2:
                c[(col1, col2)] = 1.0
                p[(col1, col2)] = 0
            else:
                corr, pval = corr_func(*(df[[col1, col2]].dropna().values.T))
                c[(col1, col2)] = corr
                c[(col2, col1)] = corr
                p[(col1, col2)] = pval
                p[(col2, col1)] = pval
    c = pd.Series(c).unstack()
    p = pd.Series(p).unstack()
    if ns_to_nan:
        c[p > alpha] = np.NaN
    return c, p
