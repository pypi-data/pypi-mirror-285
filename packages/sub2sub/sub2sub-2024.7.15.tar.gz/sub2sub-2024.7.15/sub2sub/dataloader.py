import os
import xarray as xr
from . import utils

class DataLoader:
    def __init__(self, omippath='/glade/collections/cmip/CMIP6/OMIP/'):
        self.omippath = omippath
        utils.p_header(f'>>> DataLoader.omippath = {self.omippath}')
        
    def getpaths_byvar(self, var, rpath, omipver, inst, mod, verbose=False, versions=None):
        grids = os.listdir(rpath + var)

        if len(grids)>1:
            if verbose: print("More than 1 Grid type. Exception needed. Currently set to read in gn.", grids)
            if 'gn' in grids:
                for gg in grids:
                    if gg!='gn': grids.remove(gg)

        gridtypepath = rpath +var+'/' + grids[0]

        simvers = os.listdir(gridtypepath)
        if len(simvers)>1:
            if verbose: print('More than one version, need to make exception, choosing latest version (alphabetically)', simvers)

        filepaths = gridtypepath+'/'+simvers[-1]+'/'+var+'/'
        if ('CESM2' in gridtypepath):
            if verbose: print('CESM2 FILE STRUCTURE BREAKS PATTERN')
            filepaths = gridtypepath+'/'+simvers[-1]+'/'
    
        if verbose: print(var, filepaths)
    
        key = 'OMIP.'+inst+'.'+mod+'.'+omipver+'.Omon.'+grids[0]+'.'+var
        return key, filepaths

    def variablesearch(self, omip, varnames, verbose=False, versions=None):
        if verbose: utils.p_header(f'>>> Searching OMIP version: {omip}')
        omippath = self.omippath
        institutions = os.listdir(omippath)
        if verbose:
            print('All institutions:', institutions)
            print()
    
        paths={}
    
        for ii in institutions:
            instpath = omippath+ii
            models = os.listdir(instpath)
            if verbose: print(ii, models)
    
            for mm in models:
                if verbose: print(mm)
                modelpath = instpath+'/'+mm
                omipvers = os.listdir(modelpath)
                if verbose: print('OMIP versions?', omipvers)

                if omip in omipvers:
                    omipverspath = modelpath+'/'+omip
                    member = sorted(os.listdir(omipverspath)) #select only first ensemble member
                    if verbose:
                        print('mems?', member)
                        if len(member)>1: print('more than one member')
                    rr = member[0]

                    rpath = omipverspath+'/'+rr+'/Omon/'
                    variables = os.listdir(rpath)

                    for jj,vv in enumerate(varnames):
                        if vv in variables:
                            key, filepaths = self.getpaths_byvar(vv, rpath, omip, ii, mm, verbose=verbose, versions=versions)
                            paths[key] = filepaths

                    if verbose: print()

                else:
                    continue 

            if verbose: print()
        if verbose: print()
        self.paths = paths
        utils.p_success(f'>>> DataLoader.paths created')