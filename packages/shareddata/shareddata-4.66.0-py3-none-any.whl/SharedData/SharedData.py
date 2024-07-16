import os
import psutil
import pandas as pd
import numpy as np
import json
import warnings
import time
import shutil
from datetime import datetime, timezone

from multiprocessing import shared_memory
from pathlib import Path
from importlib.metadata import version

# Ignore the "invalid value encountered in cast" warning
warnings.filterwarnings("ignore", category=RuntimeWarning)

import SharedData.Defaults as Defaults
from SharedData.Logger import Logger
from SharedData.TableMemory import TableMemory
from SharedData.TableDisk import TableDisk
from SharedData.TimeseriesContainer import TimeseriesContainer
from SharedData.TimeSeriesMemory import TimeSeriesMemory
from SharedData.TimeSeriesDisk import TimeSeriesDisk
from SharedData.DataFrame import SharedDataFrame
from SharedData.Utils import datetype
from SharedData.IO.AWSS3 import S3ListFolder, S3DeleteFolder, S3GetSession
from SharedData.Utils import remove_shm_from_resource_tracker, cpp
from SharedData.MultiProc import io_bound_unordered

class SharedData:
    
    databases = {        
        'MarketData':    ['date', 'symbol'],        
        'Relationships': ['date', 'symbol', 'symbol1'],
        'Tags':          ['date', 'tag', 'symbol'],
        'Portfolios':    ['date', 'portfolio'],        
        'Signals':       ['date', 'portfolio', 'symbol'],
        'Risk':          ['date', 'portfolio', 'symbol'],
        'Positions':     ['date', 'portfolio', 'symbol'],
        'Orders':        ['date', 'portfolio', 'symbol', 'clordid'],
        'Trades':        ['date', 'portfolio', 'symbol', 'tradeid']
    }

    def __init__(self, source, user='guest'):
        self.source = source
        self.user = user

        # DATA DICTIONARY
        self.data = {}

        # MEMORY MANAGEMENT
        self.memmaps = []

        # LOGIN VARIABLES
        self.islogged = False
        self.source = source
        self.user = user
        self.mode = 'rw'

        # S3 VARIABLES
        self.s3read = True
        self.s3write = True

        # save files locally
        self.save_local = (os.environ['SAVE_LOCAL'] == 'True')
        
        # Ie. {"MarketData/RT":"/nvme2/db","Trades/RT":"/nvme2/db"}
        self.dbfolderdict = None
        if 'DATABASE_FOLDER_DICT' in os.environ.keys():
            self.dbfolderdict = json.loads(os.environ['DATABASE_FOLDER_DICT'])

        Logger.connect(self.source, self.user)

        if (os.name == 'posix'):
            remove_shm_from_resource_tracker()

        if not self.islogged:
            self.islogged = True
            try:
                Logger.log.debug('User:%s,SharedData:%s CONNECTED!' %
                                 (self.user, version('SharedData')))
            except:
                Logger.log.debug('User:%s CONNECTED!' % (self.user))

        # [self.shm_mutex, self.globalmutex, self.ismalloc] = \
        #     self.mutex('SharedData', os.getpid())
        
    ###############################################
    ############# DATA CONTAINERS #################
    ###############################################
    
    ############# TABLE #################
    def table(self, database, period, source, tablename,
            names=None, formats=None, size=None, hasindex=True,\
            value=None, user='master', overwrite=False,\
            type='DISK', partitioning=None):

        path = f'{user}/{database}/{period}/{source}/table/{tablename}'
        if not path in self.data.keys():
            if type == 'MEMORY':
                self.data[path] = TableMemory(self, database, period, source,
                                        tablename, records=value, names=names, formats=formats, size=size, hasindex=hasindex,
                                        user=user, overwrite=overwrite)
            elif type == 'DISK':
                self.data[path] = TableDisk(self, database, period, source,
                                        tablename, records=value, names=names, formats=formats, size=size, hasindex=hasindex,
                                        user=user, overwrite=overwrite, partitioning=partitioning)
        return self.data[path].records

    ############# TIMESERIES #################
    def timeseries(self, database, period, source, tag=None, user='master',
                   startDate=None,type='DISK',
                   columns=None, value=None, overwrite=False): # tags params

        path = f'{user}/{database}/{period}/{source}/timeseries'
        if not path in self.data.keys():
            self.data[path] = TimeseriesContainer(self, database, period, source, 
                user=user, type=type, startDate=startDate)
            
        if not startDate is None:
            if self.data[path].startDate != startDate:
                raise Exception('Timeseries startDate is already set to %s' %
                                self.data[path].startDate)
            
        if tag is None:
            return self.data[path]
                    
        if (overwrite) | (not tag in self.data[path].tags.keys()):
            if (columns is None) & (value is None):
                self.data[path].load()
                if not tag in self.data[path].tags.keys():
                    errmsg = 'Tag %s/%s doesnt exist' % (path, tag)
                    Logger.log.error(errmsg)                    
                    raise Exception(errmsg)
            else:
                if self.data[path].type == 'DISK':
                    self.data[path].tags[tag] = TimeSeriesDisk(
                        self, self.data[path],database, period, source, tag,
                        value=value, columns=columns, user=user,
                        overwrite=overwrite)                    
                elif self.data[path].type == 'MEMORY':
                    if overwrite == True:
                        raise Exception('Overwrite is not supported for MEMORY type')                    
                    self.data[path].tags[tag] = TimeSeriesMemory(
                        self, self.data[path],database, period, source, tag,
                        value=value, columns=columns, user=user)
                

        return self.data[path].tags[tag].data

    ############# DATAFRAME #################
    def dataframe(self, database, period, source,
                  date=None, value=None, user='master'):
        pass

    ###############################################
    ######### SHARED MEMORY MANAGEMENT ############
    ###############################################    

    @staticmethod
    def mutex(shm_name, pid):        
        dtype_mutex = np.dtype({'names': ['pid', 'type', 'isloaded'],\
                                'formats': ['<i8', '<i8', '<i8']})
        try:
            shm_mutex = shared_memory.SharedMemory(
                name=shm_name + '#mutex', create=True, size=dtype_mutex.itemsize)
            ismalloc = False
        except:                                            
            shm_mutex = shared_memory.SharedMemory(
                name=shm_name + '#mutex', create=False)
            ismalloc = True        
        mutex = np.ndarray((1,), dtype=dtype_mutex,buffer=shm_mutex.buf)[0]        
        SharedData.acquire(mutex, pid, shm_name)        
        # register process id access to memory
        fpath = Path(os.environ['DATABASE_FOLDER'])
        fpath = fpath/('shm/'+shm_name.replace('\\', '/')+'#mutex.csv')
        os.makedirs(fpath.parent, exist_ok=True)
        with open(fpath, "a+") as f:
            f.write(str(pid)+',')
        return [shm_mutex, mutex, ismalloc]
    
    @staticmethod
    def acquire(mutex, pid, relpath):
        tini = time.time()
        # semaphore is process safe
        telapsed = 0
        hdrptr = mutex.__array_interface__['data'][0]
        semseek = 0
        firstcheck = True
        while cpp.long_compare_and_swap(hdrptr, semseek, 0, pid) == 0:
            # check if process that locked the mutex is still running
            telapsed = time.time() - tini
            if (telapsed > 15) | ((firstcheck) & (telapsed > 1)):
                lockingpid = mutex['pid']
                if not psutil.pid_exists(lockingpid):
                    if cpp.long_compare_and_swap(hdrptr, semseek, lockingpid, pid) != 0:
                        break
                if not firstcheck:
                    Logger.log.warning('%s waiting for semaphore...' % (relpath))
                tini = time.time()
                firstcheck = False
            time.sleep(0.000001)

    @staticmethod
    def release(mutex, pid, relpath):
        hdrptr = mutex.__array_interface__['data'][0]
        semseek = 0
        if cpp.long_compare_and_swap(hdrptr, semseek, pid, 0) != 1:
            Logger.log.error(
                '%s Tried to release semaphore without acquire!' % (relpath))
            raise Exception('Tried to release semaphore without acquire!')

    # TODO: check free memory before allocate    
    @staticmethod
    def malloc(shm_name, create=False, size=None):
        ismalloc = False
        shm = None
        if not create:
            try:
                shm = shared_memory.SharedMemory(
                    name=shm_name, create=False)
                ismalloc = True
            except:
                pass            
        elif (create) & (not size is None):
            try:
                shm = shared_memory.SharedMemory(
                    name=shm_name, create=True, size=size)                
                ismalloc = False
            except:                                            
                shm = shared_memory.SharedMemory(
                    name=shm_name, create=False)
                ismalloc = True
                
        elif (create) & (size is None):
            raise Exception(
                'SharedData malloc must have a size when create=True')
        
        # register process id access to memory
        fpath = Path(os.environ['DATABASE_FOLDER'])
        fpath = fpath/('shm/'+shm_name.replace('\\', '/')+'.csv')
        os.makedirs(fpath.parent, exist_ok=True)
        pid = os.getpid()
        with open(fpath, "a+") as f:
            f.write(str(pid)+',')

        return [shm, ismalloc]

    @staticmethod
    def free(shm_name):
        if os.name == 'posix':
            try:
                shm = shared_memory.SharedMemory(
                    name=shm_name, create=False)
                shm.close()
                shm.unlink()
                fpath = Path(os.environ['DATABASE_FOLDER'])
                fpath = fpath/('shm/'+shm_name.replace('\\', '/')+'.csv')
                if fpath.is_file():
                    os.remove(fpath)
            except:
                pass

    @staticmethod
    def freeall():
        shm_names = SharedData.list_memory()
        for shm_name in shm_names.index:
            SharedData.free(shm_name)

    ######### LIST ############    
    def listall(self, keyword='', user='master'):
        tables = pd.DataFrame()

        mdprefix = user+'/'+keyword

        s3, bucket = S3GetSession()
        arrobj = np.array([[obj.key , obj.last_modified, obj.size]
                    for obj in bucket.objects.filter(Prefix=mdprefix)])
        dfremote = pd.DataFrame()
        dfremote_metadata = pd.DataFrame()
        if arrobj.size>0:
            dfremote = pd.DataFrame(arrobj, columns=['key','last_modified','size'])
            dfremote['last_modified'] = pd.to_datetime(dfremote['last_modified']).dt.tz_localize(None)
            dfremote['size'] = dfremote['size'].astype(int)
            dfremote['user'] = dfremote['key'].apply(lambda x: x.split('/')[0])
            dfremote['database'] = dfremote['key'].apply(lambda x: x.split('/')[1])
            dfremote_metadata = dfremote[dfremote['database']=='Metadata'].copy()
            dfremote_metadata.rename(columns={'key':'path',
                                            'last_modified':'last_modified_remote',
                                            'size':'size_remote'},inplace=True)
            dfremote_metadata['path'] = dfremote_metadata['path'].apply(lambda x: x.replace('.bin.gzip',''))
            dfremote_metadata.set_index('path',inplace=True)

            dfremote = dfremote[dfremote['database']!='Metadata'].copy()
            dfremote['period'] = dfremote['key'].apply(lambda x: x.split('/')[2])
            dfremote['source'] = dfremote['key'].apply(lambda x: x.split('/')[3])
            timeseriesidx = np.array(['timeseries_' in s for s in dfremote['key']])
            dfremote.loc[timeseriesidx,'container'] = 'timeseries'
            dfremote.loc[~timeseriesidx,'container'] = 'table'
            dfremote['tablename'] = ''
            dfremote.loc[~timeseriesidx,'tablename'] = \
                dfremote[~timeseriesidx]['key'].apply(
                    lambda x: '/'.join(x.split('/')[5:]).
                    replace('head.bin.gzip','').replace('tail.bin.gzip','').rstrip('/')
                    )
            dfremote['partition'] = dfremote['tablename'].apply(lambda x: '/'.join(x.split('/')[1:]) if '/' in x else '')
            dfremote['tablename'] = dfremote['tablename'].apply(lambda x: x.split('/')[0])
            dfremote['path'] = dfremote['user']+'/'+dfremote['database']+'/'+dfremote['period']+'/' \
                +dfremote['source']+'/'+dfremote['container']+'/'+dfremote['tablename']+'/'+dfremote['partition']
            dfremote['path'] = dfremote['path'].apply(lambda x: x.rstrip('/').rstrip('/'))
            dfremote['files'] = 1

            dfremote = dfremote.groupby('path').agg(
                    {               
                        'last_modified':'max','size':'sum','files':'sum',
                        'user':'first','database':'first','period':'first',
                        'source':'first','container':'first','tablename':'first',
                        'partition':'first'
                    }
                )
            dfremote.rename(columns={
                'last_modified':'last_modified_remote','size':'size_remote','files':'files_remote'    
                },inplace=True)

        # get a list of local files
        dflocal = pd.DataFrame()
        dflocal_metadata = pd.DataFrame()
        dbfolder = os.environ['DATABASE_FOLDER']
        localpath = Path(dbfolder) / Path(mdprefix)
        records = []
        for root, dirs, files in os.walk(localpath):
            for name in files:
                full_path = os.path.join(root, name)
                modified_time_local = os.path.getmtime(full_path)
                # Convert the local modified time to a datetime object
                dt_local = datetime.fromtimestamp(modified_time_local)
                # Convert the local datetime object to UTC
                dt_utc = dt_local.astimezone(timezone.utc)      
                size = os.path.getsize(full_path)
                records.append({
                    'key': full_path.replace(dbfolder,'')[1:].replace('\\','/'),
                    'last_modified': dt_local,
                    'size': size
                })

        if len(records)>0:
            dflocal = pd.DataFrame(records)
            dflocal['last_modified'] = pd.to_datetime(dflocal['last_modified'])
            dflocal['size'] = dflocal['size'].astype(int)
            dflocal['user'] = dflocal['key'].apply(lambda x: x.split('/')[0])
            dflocal['database'] = dflocal['key'].apply(lambda x: x.split('/')[1])
            dflocal_metadata = dflocal[dflocal['database']=='Metadata'].copy()
            dflocal_metadata.rename(columns={'key':'path',
                                            'last_modified':'last_modified_local',
                                            'size':'size_local'},inplace=True)
            dflocal_metadata['path'] = dflocal_metadata['path'].apply(lambda x: x.replace('.bin',''))
            dflocal_metadata = dflocal_metadata[['.xlsx' not in s for s in dflocal_metadata['path']]]
            dflocal_metadata.set_index('path',inplace=True)
            dflocal = dflocal[dflocal['database']!='Metadata'].copy()
            dflocal['period'] = dflocal['key'].apply(lambda x: x.split('/')[2])
            dflocal['source'] = dflocal['key'].apply(lambda x: x.split('/')[3])
            timeseriesidx = np.array(['timeseries' in s for s in dflocal['key']])
            dflocal.loc[timeseriesidx,'container'] = 'timeseries'
            dflocal.loc[~timeseriesidx,'container'] = 'table'
            dflocal['tablename'] = ''
            dflocal.loc[~timeseriesidx,'tablename'] = \
                dflocal[~timeseriesidx]['key'].apply(
                    lambda x: '/'.join(x.split('/')[5:]).
                    replace('data.bin','').replace('dateidx.bin','').replace('symbolidx.bin','').
                    replace('portidx.bin','').replace('pkey.bin','').replace('.bin','').rstrip('/')
                    )
            dflocal['partition'] = dflocal['tablename'].apply(lambda x: '/'.join(x.split('/')[1:]) if '/' in x else '')
            dflocal['tablename'] = dflocal['tablename'].apply(lambda x: x.split('/')[0])
            dflocal['path'] = dflocal['user']+'/'+dflocal['database']+'/'+dflocal['period']+'/' \
                +dflocal['source']+'/'+dflocal['container']+'/'+dflocal['tablename']+'/'+dflocal['partition']
            dflocal['path'] = dflocal['path'].apply(lambda x: x.rstrip('/').rstrip('/'))
            dflocal['files'] = 1
            dflocal = dflocal.groupby('path').agg(
                    {               
                        'last_modified':'max','size':'sum','files':'sum',
                        'user':'first','database':'first','period':'first',
                        'source':'first','container':'first','tablename':'first',
                        'partition':'first'
                    }
                )
            dflocal.rename(columns={
                'last_modified':'last_modified_local','size':'size_local','files':'files_local'
                },inplace=True)

        ls = dfremote.copy()
        ls = ls.reindex(index=ls.index.union(dflocal.index),
                        columns=ls.columns.union(dflocal.columns))
        ls.loc[dflocal.index,dflocal.columns] = dflocal.values

        ls_metadata = dfremote_metadata.copy()
        ls_metadata = ls_metadata.reindex(index=ls_metadata.index.union(dflocal_metadata.index),
                        columns=ls_metadata.columns.union(dflocal_metadata.columns))
        ls_metadata.loc[dflocal_metadata.index,dflocal_metadata.columns] = dflocal_metadata.values


        if len(ls)>0:
            ls = ls[['last_modified_local','size_local','files_local',
                    'last_modified_remote', 'size_remote', 'files_remote',
                    'user','database','period','source','container', 'tablename','partition']].copy()
            ls['partitioning_period'] = ls['partition'].apply(lambda x: datetype(x))

            ls_metadata = ls_metadata[['last_modified_local','size_local',
                    'last_modified_remote', 'size_remote',
                    'user','database']].copy()

            tables = ls.copy()
            timeseries = tables[tables['container']=='timeseries'].copy()
            tables = tables[tables['container']!='timeseries'].copy()
            ts = list(timeseries.itertuples())[0]
            for ts in timeseries.itertuples():
                try:              
                    tbl = self.timeseries(ts.database,ts.period,ts.source)
                    tbl.load()
                    tag = list(tbl.tags)[0]
                    for tag in tbl.tags:
                        path = ts.Index + '/' + tag                
                        tables.loc[path,timeseries.columns] = timeseries.loc[ts.Index].values
                        tables.loc[path,['user','database','period','source','container','tablename']] = \
                            [user,ts.database,ts.period,ts.source,'timeseries',tag]
                        tables.loc[path,'size_local'] = 0
                        tables.loc[path,'last_modified_local'] = pd.NaT    
                        filepath,shmname = tbl.tags[tag].get_path()
                        if filepath.is_file():  
                            tables.loc[path,'size_local'] = filepath.stat().st_size
                            tables.loc[path,'last_modified_local'] = pd.to_datetime(filepath.stat().st_mtime,unit='s')
                            tables.loc[path,'files_local'] = 1
                except Exception as e:
                    Logger.log.error(f'Loading {ts.Index} Error: {e}')
            
            tables = pd.concat([tables,ls_metadata])

            tables['last_modified_local'] = pd.to_datetime(tables['last_modified_local'])
            tables['last_modified_remote'] = pd.to_datetime(tables['last_modified_remote'])
            tables.sort_index(inplace=True)

        return tables

    @staticmethod
    def list(keyword='', user='master'):
        mdprefix = user+'/'
        keys = S3ListFolder(mdprefix+keyword)
        keys = keys[['.bin' in k for k in keys]]
        keys = [k.replace(mdprefix, '').split('.')[0]
                .replace('/head', '').replace('/tail', '')\
                .replace('_head', '').replace('_tail', '')
                for k in keys]
        keys = np.unique(keys).tolist()
        return keys
    
    @staticmethod
    def list_remote(keyword='', user='master'):
        mdprefix = user+'/'+keyword
        keys = S3ListFolder(mdprefix)
        keys = keys[['.bin' in k for k in keys]]
        keys = [k.replace(mdprefix, '').split('.')[0]
                .replace('/head', '').replace('/tail', '')\
                .replace('_head', '').replace('_tail', '')
                for k in keys]
        keys = np.unique(keys)
        return keys
    
    @staticmethod
    def list_local(keyword='', user='master'):
        mdprefix = user+'/'+keyword
        mdprefix = Path(os.environ['DATABASE_FOLDER']) / Path(mdprefix)
        keys = list(mdprefix.rglob('*data.bin'))
        keys = [str(k).replace(str(mdprefix)+'/', '').replace('/data.bin','') 
                for k in keys]
        keys = np.unique(keys)
        return keys

    @staticmethod
    def list_memory():
        folder = Path(os.environ['DATABASE_FOLDER'])/'shm'
        shm_names = pd.DataFrame()
        for root, _, filepaths in os.walk(folder):
            for filepath in filepaths:
                if filepath.endswith('.csv'):
                    fpath = os.path.join(root, filepath)
                    shm_name = fpath.removeprefix(str(folder))[1:]
                    shm_name = shm_name.removesuffix('.csv')
                    if os.name == 'posix':
                        shm_name = shm_name.replace('/', '\\')
                    elif os.name == 'nt':
                        shm_name = shm_name.replace('\\', '/')
                    try:
                        shm = shared_memory.SharedMemory(
                            name=shm_name, create=False)
                        shm_names.loc[shm_name, 'size'] = shm.size
                        shm.close()
                    except:
                        try:
                            if fpath.is_file():
                                os.remove(fpath)
                        except:
                            pass
        shm_names = shm_names.sort_index()
        return shm_names
    
    def listdb(self, database, user='master'):
        tables = pd.DataFrame()
        schemas = pd.DataFrame()        
        try:
            ls = SharedData.list(database,user)
            if len(ls)>0:
                ls = pd.DataFrame(ls,columns=['path'])
                ls['user'] = user
                ls['database'] = ls['path'].apply(lambda x: x.split('/')[0])
                ls['period'] = ls['path'].apply(lambda x: x.split('/')[1])
                ls['source'] = ls['path'].apply(lambda x: x.split('/')[2])
                ls['container'] = ls['path'].apply(lambda x: x.split('/')[3])
                ls['tablename'] = ls['path'].apply(lambda x: '/'.join(x.split('/')[4:]))
                ls['partition'] = ls['tablename'].apply(lambda x: '/'.join(x.split('/')[1:]) if '/' in x else '')
                ls['tablename'] = ls['tablename'].apply(lambda x: x.split('/')[0])
                
                # date partitioning
                ls['partitioning'] = ls['partition'].apply(lambda x: datetype(x))        
                ls['ispartitiondate'] = (ls['partitioning']=='day') | (ls['partitioning']=='month') | (ls['partitioning']=='year')
                ls_part = ls[ls['ispartitiondate']].groupby(['user','database','period','source','container','tablename','partitioning']).last()
                ls_part = ls_part.reset_index().set_index(['user','database','period','source','container','tablename'])

                # name partitioning
                idx = ~ls['ispartitiondate']
                ls.loc[idx,'partitioning'] = ls['tablename'].apply(lambda x: datetype(x))
                idx = (idx) & ((ls['partitioning'] == 'day') | (ls['partitioning'] == 'month') | (ls['partitioning'] == 'year'))
                ls['ispartitionname'] = False
                ls.loc[idx,'ispartitionname'] = True        
                ls_name = ls[ls['ispartitionname']].groupby(['user','database','period','source','container','partitioning']).last()                                
                ls_name = ls_name.reset_index().set_index(['user','database','period','source','container','tablename'])

                tables = pd.concat([tables,ls])

                ls['ispartitioned'] = (ls['ispartitiondate']) | (ls['ispartitionname'])
                ls = ls[~ls['ispartitioned']].set_index(['user','database','period','source','container','tablename']).sort_index()
                ls = pd.concat([ls,ls_part,ls_name]).sort_index()
                schemas = pd.concat([schemas,ls])
        except Exception as e:
            print(e)

        if len(tables) == 0:
            tables = pd.DataFrame(columns=['path'])
        else:
            tables = tables.reset_index(drop=True).set_index('path')
            timeseries = tables[tables['container']=='timeseries']
            tables = tables[tables['container']!='timeseries'].copy()
            for ts in timeseries.itertuples():  
                try:      
                    tbl = self.timeseries(ts.database,ts.period,ts.source)
                    tbl.load()
                    tags = list(tbl.tags.keys())
                    for tag in tags:            
                        path = ts.Index + '/' + tag
                        tables.loc[path,['user','database','period','source','container','tablename']] = \
                            [user,ts.database,ts.period,ts.source,'timeseries',tag]   
                except Exception as e:
                    Logger.log.error(f'Loading {ts.Index} Error: {e}')
        
        if len(schemas) == 0:
            schemas = pd.DataFrame(columns=['path'])
        else:
            schemas = schemas.reset_index().set_index('path')

             
        return tables, schemas        
    
    def load_table(self,table,args, user='master'):    
        result = {}
        result['path'] = table.name
        try:
            if table['partition']!= '':
                tablename = table['tablename'] + '/' + table['partition']
            else:
                tablename = table['tablename']
                    
            tbl = self.table(table['database'],table['period'],table['source'],tablename, user=user)
            result['hasindex'] = tbl.table.hdr['hasindex']
            result['mtime'] = pd.Timestamp.fromtimestamp(tbl.mtime)
            result['size'] = tbl.recordssize*tbl.dtype.itemsize
            result['count'] = tbl.count
            result['recordssize'] = tbl.recordssize
            result['itemsize'] = tbl.dtype.itemsize
            result['names'] = ','.join([s[0] for s in tbl.dtype.descr])
            result['formats'] = ','.join([s[1] for s in tbl.dtype.descr])
            
        except Exception as e:
            Logger.log.error(f'Loading {table.name} Error: {e}')
        finally:
            tbl.free()
        
        return result
    
    def load_tables(self, tables):
        try:
            tables = tables[tables['container']=='table']
            Logger.log.info('Loading tables...')
            results = io_bound_unordered(self.load_table,tables,[],maxproc=8)
            Logger.log.info('Tables loaded!')  
            for r in results:
                if r==-1:
                    Logger.log.warning('removing',r)
                    results.remove(r)
            df = pd.DataFrame(results).set_index('path')
            tables.loc[df.index,df.columns] = df.values
            return True
        except Exception as e:
            Logger.log.error(f'load_tables error {e}')
        return False

    def loaddb(self, database, user='master',maxproc=8):
        try:
            tables, schemas = self.listdb(database, user)
            tables = tables[tables['container']=='table']
            Logger.log.info('Loading tables...')
            results = io_bound_unordered(self.load_table,tables,[],maxproc=maxproc)
            Logger.log.info('Tables loaded!')  
            for r in results:
                if r==-1:
                    Logger.log.warning('removing',r)
                    results.remove(r)
            df = pd.DataFrame(results).set_index('path')
            tables.loc[df.index,df.columns] = df.values
            return True
        except Exception as e:
            Logger.log.error(f'load_db error {e}')        
        return False

    ######### DELETE ############
    
    def delete_table(self, database, period, source, tablename, user='master'):
        try:
            path = f'{user}/{database}/{period}/{source}/table/{tablename}'
            if path in self.data.keys():
                self.data[path].free()
                del self.data[path]
            localpath = Path(os.environ['DATABASE_FOLDER'])/Path(path)
            if localpath.exists():
                shutil.rmtree(localpath)
            S3DeleteFolder(path)
            return True
        except Exception as e:
            Logger.log.error(f'Delete {path} Error: {e}')
            return False
        
    def delete_timeseries(self, database, period, source, 
                          tag=None, user='master'):
        try:
            path = f'{user}/{database}/{period}/{source}/timeseries'
            if tag is None:                
                # delete timeseries container                
                if path in self.data.keys():
                    del self.data[path]
                localpath = Path(os.environ['DATABASE_FOLDER'])/Path(path)
                if localpath.exists():
                    shutil.rmtree(localpath)
                S3DeleteFolder(path)                                
                return True
            else:
                # delete timeseries tag
                ts = self.timeseries(database,period,source,tag,user=user)                
                tstag = self.data[path].tags[tag]
                fpath, shm_name = tstag.get_path()
                del self.data[path].tags[tag]
                del ts
                os.remove(fpath)
                return True
            
        except Exception as e:
            Logger.log.error(f'Delete {path}/{tag} Error: {e}')
            return False        