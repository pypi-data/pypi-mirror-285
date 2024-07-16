import xarray as xr
import colorama as ca

def p_header(text):
    print(ca.Fore.CYAN + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_hint(text):
    print(ca.Fore.LIGHTBLACK_EX + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_success(text):
    print(ca.Fore.GREEN + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_fail(text):
    print(ca.Fore.RED + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def p_warning(text):
    print(ca.Fore.YELLOW + ca.Style.BRIGHT + text + ca.Style.RESET_ALL)

def preprocess_coords(ds):
    #rename for consistency
    if 'i' in ds:
        ds=ds.rename({'i':'x', 'j':'y'})
        
    if 'd2' in ds.dims:
        ds = ds.rename_dims({'d2':'bnds'})
            
    if 'axis_nbounds' in ds.dims:
        ds = ds.rename_dims({'axis_nbounds':'bnds'})
    
    if 'lat' in ds.dims:
        ds = ds.rename_dims({'lon':'x', 'lat':'y'})
        
    if ('nlat' in ds.dims):
        ds = ds.rename_dims({'nlon':'x', 'nlat':'y'})
        
    if 'olevel' in ds:
        ds = ds.rename({'olevel':'lev', 'olevel_bounds':'lev_bnds'})
        
    if ('latitude' in ds.coords):
        if ('umo' in ds.variables) or ('uo' in ds.variables):
            ds = ds.rename({'latitude':'ulat', 'longitude':'ulon'})
        elif ('vmo' in ds.variables) or ('vo' in ds.variables):
            ds = ds.rename({'latitude':'vlat', 'longitude':'vlon'})
        elif ('thetao' in ds.variables) or ('so' in ds.variables):
            ds = ds.rename({'latitude':'tlat', 'longitude':'tlon'})    
        
    if ('lat' in ds.coords):
        if ('umo' in ds.variables) or ('uo' in ds.variables):
            ds = ds.rename({'lat':'ulat', 'lon':'ulon'})
        elif ('vmo' in ds.variables) or ('vo' in ds.variables):
            ds = ds.rename({'lat':'vlat', 'lon':'vlon'})
        elif ('thetao' in ds.variables) or ('so' in ds.variables):
            ds = ds.rename({'lat':'tlat', 'lon':'tlon'})
    
    if ('nav_lat' in ds.coords):
        if ('umo' in ds.variables) or ('uo' in ds.variables):
            ds = ds.rename({'nav_lat':'ulat', 'nav_lon':'ulon', 'bounds_nav_lon':'ulon_bnds', 'bounds_nav_lat':'ulat_bnds'})
        elif ('vmo' in ds.variables) or ('vo' in ds.variables):
            ds = ds.rename({'nav_lat':'vlat', 'nav_lon':'vlon', 'bounds_nav_lon':'vlon_bnds', 'bounds_nav_lat':'vlat_bnds'})
        elif ('thetao' in ds.variables) or ('so' in ds.variables):
            ds = ds.rename({'nav_lat':'tlat', 'nav_lon':'tlon', 'bounds_nav_lon':'tlon_bnds', 'bounds_nav_lat':'tlat_bnds'})
            
    if 'time_bounds' in ds:
        ds = ds.rename({'time_bounds':'time_bnds'})
        
    if 'lev_bounds' in ds:
        ds = ds.rename({'lev_bounds':'lev_bnds'})
        
    if 'bounds_lon' in ds:
        if ('umo' in ds) or ('uo' in ds.variables):
            ds = ds.rename({'bounds_lon':'ulon_bnds', 'bounds_lat':'ulat_bnds'})
        elif ('vmo' in ds) or ('vo' in ds.variables):
            ds = ds.rename({'bounds_lon':'vlon_bnds', 'bounds_lat':'vlat_bnds'})
        elif ('thetao' in ds) or ('so' in ds.variables):
            ds = ds.rename({'bounds_lon':'tlon_bnds', 'bounds_lat':'tlat_bnds'})
            
    if 'longitude_bnds' in ds:
        if ('umo' in ds) or ('uo' in ds.variables):
            ds = ds.rename({'longitude_bnds':'ulon_bnds', 'latitude_bnds':'ulat_bnds'})
        elif ('vmo' in ds) or ('vo' in ds.variables):
            ds = ds.rename({'longitude_bnds':'vlon_bnds', 'latitude_bnds':'vlat_bnds'})
        elif ('thetao' in ds) or ('so' in ds.variables):
            ds = ds.rename({'longitude_bnds':'tlon_bnds', 'latitude_bnds':'tlat_bnds'})
                    
    #assign coords for x and y indices across all datasets
    xindex = range(len(ds.x))
    xindex = xr.DataArray(range(len(ds.x)),name='x', dims=['x'], coords = {'x':xindex})
    
    yindex = range(len(ds.y))
    yindex = xr.DataArray(range(len(ds.y)),name='y', dims=['y'], coords = {'y':yindex})
   
    ds['x_orig'] = ds['x'].copy()
    ds['y_orig'] = ds['y'].copy()
    
    ds = ds.assign_coords({'x':xindex, 'y':yindex})
     
    return ds

def preprocess_cmcc_esm2(ds):
    ds = ds.rename({'i':'y'})
    ds = ds.rename({'j':'x'})
    ds=preprocess_coords(ds)
    return ds

def preprocess_cas(ds):
    ds = ds.isel(j=slice(None, None, -1))
    ds = ds.assign_coords({'j':np.arange(len(ds.j)-1, -1, -1, dtype='int')})
    ds=preprocess_coords(ds)  
    return ds

def preprocess_cesm(ds):
    
    ds = preprocess_coords(ds)
    
    #convert lev to m from cm
    ds['lev'] = ds['lev']/100
    #lev bnds were already converted
    
    return ds