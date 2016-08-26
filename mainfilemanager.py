import sqlite3
import os
from pathlib import Path


class Files(object):
    
    def __init__(self):
        if not os.path.exists(os.path.join(os.path.expanduser('~'),'.filetransmitserver')):
            os.makedirs(os.path.join(os.path.expanduser('~'),'.filetransmitserver'))
            os.makedirs(os.path.join(os.path.expanduser('~'),'.filetransmitserver','junk'))
        self.db = sqlite3.connect(os.path.join(os.path.expanduser('~'),'.filetransmitserver','filesdata.sqlite3'))
        self.db.execute('create table if not exists files (name text, size text, notes text)')
        self.db.execute('create table if not exists master_folders (name text, path text)')

        self.db.commit()


    def __call__(self,name,size,note=''):
        datac = self.db.execute('select * from files')
        data = datac.fetchall()
        names = []
        sizes = []
        notes = []
        

        for i in data:
            names.append(i[0])
            sizes.append(i[1])
            notes.append(i[2])

        if name in names:
            i = names.index(name)
            self.getdir(name)
            if str(sizes[i]) == str(size):
                return (False,'')
            else:
                return (True,self.getdir(name))
        else:
            self.getdir(name)
            self.db.execute('insert into files values (?,?,?)',(name,str(size),note))
            self.db.commit()
            return (True,self.getdir(name))

    def addMasterDir(self,name,path):
        if os.path.exists(path) == False:
            os.mkdir(path)
        self.db.execute('insert into master_folders values (?,?)',(name,path))
        self.db.commit()

    def getdir(self,name):
        #FileNotFoundError
        datac = self.db.execute('select * from master_folders')
        data = datac.fetchall()
        names = []
        paths = []
        for i in data:
            names.append(i[0])
            paths.append(i[1])

        

        s = name.split(os.path.sep)
        master_name = s[0]
        s.pop(0)
        name = '/'.join(s)

        if master_name in names:
            i = names.index(master_name)
            path = os.path.join(paths[i],name)
            basepath,dummy = os.path.split(path)
            if os.path.exists(basepath) == False:
                os.makedirs(basepath)
            return os.path.join(paths[i],name)
        else:
            raise FileNotFoundError('Cannot find master folder %s in database!' % master_name)

    def getMasterDirs(self):
        datac = self.db.execute('select * from master_folders')
        data = datac.fetchall()
        d = {}
        for i in data:
            d[i[0]] = i[1]

        return d

    
    def getAllFilesFromMasterDir(self,master_dir):
        master_dirs = self.getMasterDirs()
        if master_dir not in list(master_dirs.keys()):
            raise FileNotFoundError('Cannot find master folder %s in database!' % master_dir)

        e = []

        datac = self.db.execute('select * from files')
        data = datac.fetchall()
        names = []
        sizes = []
        notes = []
        

        for i in data:
            names.append(i[0])
            sizes.append(i[1])
            notes.append(i[2])
            if i[0].startswith(master_dir):
                e.append(i[0])
        return e

    def getAllFiles(self):
        d = {}
        for i in self.getMasterDirs():
            d[i] = self.getAllFilesFromMasterDir(i)

        return d

    def removeFile(self,filename):
        '''
removes file from database
'''
        try:
            self.db.execute('delete from files where name=?',(filename,))
            self.db.commit()
            return

        except:
            pass
        raise FileNotFoundError('File %s Not in Database!' % filename)
    
    def deleteFile(self,filename):
        f = self.getdir(filename)
        e = filename.replace('/',':')
        p = Path(f)
        p.rename(os.path.join(os.path.expanduser('~'),'.filetransmitserver','junk',e))
        self.removeFile(filename)
        class imitator:
            pass
        a = imitator()
        a.restore = lambda : self.restore(filename)
        a.delete = lambda : self._delete(filename)
        return a
    

    def restore(self,filename):
        '''
restore file from junk
'''
        e = filename.replace('/',':')
        if not os.path.exists(os.path.join(os.path.expanduser('~'),'.filetransmitserver','junk',e)):
            raise FileNotFoundError('File %s Not in junk folder!' % filename)
        fn = os.path.join(os.path.expanduser('~'),'.filetransmitserver','junk',e)
        p = Path(fn)
        size = p.stat().st_size
        self(filename,size)
        p.rename(self.getdir(filename))

    def _delete(self,filename):
        '''
delete file from junk
'''
        e = filename.replace('/',':')
        if not os.path.exists(os.path.join(os.path.expanduser('~'),'.filetransmitserver','junk',e)):
            raise FileNotFoundError('File %s Not in junk folder!' % filename)

        os.remove(os.path.join(os.path.expanduser('~'),'.filetransmitserver','junk',e))

    def list_junk(self):
        l = os.path.listdir(os.path.join(os.path.expanduser('~'),'.filetransmitserver','junk'))
        nl = []
        for i in l:
            nl.append(i.replace(':','/'))

        return nl

    

        

        

        
        
        
        
                 

    
        
    

     

        
        
        

        
                         
        






        
        
