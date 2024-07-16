
""" Docs for database
Docs::


    Sqlite:
       To make a consistent backup of an SQLite database file, you can use the VACUUM INTO command. 
       It creates a new database file that is a compacted copy of the original database. Here's how to do it:
       VACUUM main INTO 'backup.db';

       Sqlite command line to manage DB

      .open "//e"    python prepro.py diskcache_config 
      https://sqlite.org/wal.html
      
      PRAGMA journal_mode = DELETE;   (You can switch it back afterwards.)
      PRAGMA wal_checkpoint(TRUNCATE);
      PRAGMA journal_mode = WAL;     
      PRAGMA wal_checkpoint(FULL);
      
      cache   = diskcache_load( db_path, size_limit=100000000000, verbose=1 )
      v = diskcache_getkeys(cache) ; log(len(v) )
      cache.close() ; cache = None
      ss      = ""
      if task == 'commit':
        # ss =  PRAGMA journal_mode = DELETE;  
        ss =  PRAGMA wal_checkpoint(TRUNCATE); 
      
      elif task == 'fast':
        ss =  PRAGMA journal_mode = WAL;

      elif task == 'copy':
        ss =  PRAGMA wal_checkpoint(TRUNCATE);  
      
      with open( 'ztmp_sqlite.sql', mode='w') as fp :
          fp.write(ss)
      log(ss)            
      os.system( f'sqlite3  {db_path}/cache.db  ".read ztmp_sqlite.sql"    ')    




"""
