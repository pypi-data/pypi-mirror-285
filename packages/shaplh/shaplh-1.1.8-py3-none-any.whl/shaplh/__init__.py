import os
import scipy as sp
from hashlib import sha256
import shutil
import numpy as np
from scipy.sparse import csc_matrix
import pandas as pd
from typing import Any, Dict, List
from .shaplh import *

__doc__ = shaplh.__doc__
if hasattr(shaplh, "__all__"):
    __all__ = shaplh.__all__

def shparse(obj: Any, # dataset
    pthin: str,       # path to data
    opt: str='uset'   # to be used in later builds
) -> List[str]:  
    if isinstance(obj, pd.core.frame.DataFrame):
        csc_m = csc_matrix(obj.to_numpy()) 
    elif isinstance(obj, np.ndarray):
        csc_m = csc_matrix(obj) 
    elif isinstance(obj, sp.sparse.csc.csc_matrix):
        csc_m = obj
    else: 
        return 'invalid parameter'
    if not os.path.exists(pthin+'/.sh'):
        os.makedirs(pthin+'/.sh/')
    df = pd.DataFrame({'row':csc_m.tocoo().col if csc_m.ndim==1 else csc_m.indices, 'col':0 if csc_m.ndim==1 else csc_m.tocoo().col, 'val':csc_m.data})
    df.to_csv(pthin+'/.dat', index=False)
    output = shaplh.libshparse(pthin, opt)
    if os.path.isfile(pthin+'/.dat'):
        os.remove(pthin+'/.dat')
    if output[0]=="i":
        filename = pthin+'/.sh/'+output
        if os.path.isfile(filename):
            df = pd.read_csv(filename)
            df = df.sort_values(by=['id']).reset_index(drop=True)
            return df
        else:
            return "missing results" 
    else:
        return False


def shcluster(sourcevec: str, pthin: str) -> str:
    return shaplh.libshcluster(','.join(sourcevec), pthin)


def shclustert(sourcevec: str, pthin: str) -> str:
    return shaplh.libshclustert(','.join(sourcevec), pthin)


def shstage(df: str, pthin: str) -> str:
    refdata = ','.join([str(val) for val in df.row.values]+[str(val) for val in df.val.values])
    return shaplh.libshstage(refdata, pthin)


def shmerget(referencea: str, referenceavec: str, pthin: str) -> str:
    values = shaplh.libshmerget(referencea, ','.join(referenceavec), pthin)
    return values.split(',')


def shmerge(referencea: str, referenceb: str, pthin: str) -> str:
    return shaplh.libshmerge(referencea, referenceb, pthin)


def shapley(referencea: str, 
    referencebvec: str,      
    pthin: str,              
    ofs: str='none',         
    limit: str='none',      
    size: int=100,           
    force=True,               
    opt='uset',              
    summarize='none'        
) -> List[pd.DataFrame]:
    referencebvecs = [ refb+'|a'+sha256((referencea+'_'+refb).encode('utf-8')).hexdigest()[0:15] for refb in referencebvec]
    subrefbs = referencebvecs if force else [refb for refb in referencebvecs if not os.path.isfile(pthin+'/.sh/'+refb.split('|')[1] )]
    if len(subrefbs) > 0:
        sourcevecs = [ ','.join(list(outsource)) for outsource in np.split(subrefbs, np.arange(size,len(subrefbs),size)) ]
        resultvec =  [ shaplh.libshapley(referencea, sourcevec, pthin, opt, ofs, limit, summarize) for sourcevec in sourcevecs]
    result = {referencea+'|'+b:pd.read_csv(pthin+'/.sh/'+b.split('|')[1]) for b in referencebvecs if os.path.isfile(pthin+'/.sh/'+b.split('|')[1]) }
    return result

