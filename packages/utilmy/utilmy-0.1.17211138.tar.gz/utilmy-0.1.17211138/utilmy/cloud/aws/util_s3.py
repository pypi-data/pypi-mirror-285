""" Utils for S3

  

##### Install LocalStack:
pip install localstack

Start LocalStack: Use the following command to start LocalStack with S3 service:
localstack start --services=s3
Configure AWS CLI and Boto3: Set up AWS CLI and Boto3 to use the LocalStack endpoint for S3. Typically, LocalStack runs on http://localhost:4566.


aws configure


# Use access key: test, secret key: test, region: us-east-1, output format: json
Python Example: Here’s a Python script using boto3 to interact with S3 on LocalStack:

import boto3

# Configure boto3 to use LocalStack
s3 = boto3.client('s3', endpoint_url='http://localhost:4566', aws_access_key_id='test', aws_secret_access_key='test', region_name='us-east-1')

# Create a bucket
s3.create_bucket(Bucket='my-test-bucket')

# Upload a file
s3.put_object(Bucket='my-test-bucket', Key='testfile.txt', Body=b'Hello LocalStack!')

# Retrieve the file
response = s3.get_object(Bucket='my-test-bucket', Key='testfile.txt')
data = response['Body'].read().decode('utf-8')
print(data)



"""
import boto3, os, sys
import pandas as pd
from io import StringIO
import time
import random
from datetime import datetime
import multiprocessing as mp

from utilmy import log,loge

#########################################################################################################
def test_lock():
    """
         pip install fire utilmy

         ### Concurrent lock simulation
             python util_s3.py  test_lock ;     python util_s3.py  test_lock ;   python util_s3.py  test_lock ; 

    Logs: 

         
    """
    ### python util_s3.py test()
    #s3_csv = S3UpdatecsvwithLock('s3://bucket/csv_file.csv"')
    #s3_csv.update_csv(newrow=['Rohn', 75], retries=5, backoff_in_seconds=1)

    ### Bucket

    cmd = " aws s3 mb s3://bucket "
    os.system( cmd )

    s3lock = S3lock('s3://bucket/mylock/')
    s3lock.lock('s3://bucket/path1/csv_file.csv')

    ### Do Something
    time.sleep(random.random(3))

    s3lock.unlock('s3://bucket/path1/csv_file.csv')


    s3_csv = S3Lock_csv('s3://bucket/csv_file.csv', 's3://bucket')
    s3_csv.update_csv(newrow=['Rohn', 75])






def test2():
  """
     Logs


  """  
  # Usage for S3
  s3lock = cloudLock(dirlock="s3://mybucket/lock_hash")
  s3lock.lock("s3://myotherbucket/myfile.csv")
   # do something
  s3lock.unlock("s3://myotherbucket/myfile.csv")

  # Usage for GCS
  gcslock = cloudLock(dirlock="gs://mybucket/lock_hash")
  gcslock.lock("gs://myotherbucket/myfile.csv")
  # do something
  gcslock.unlock("gs://myotherbucket/myfile.csv")

  # Usage for Local Filesystem
  locallock = cloudLock(dirlock="/local/path/lock_hash")
  locallock.lock("/local/path/myfile.csv")
  # do something
  locallock.unlock("/local/path/myfile.csv")


def test_lock1(x):
  time.sleep(1)
  s3lock = S3lock(dirlock="s3://mybucket/lock_hash")
  s3lock.lock("s3://myotherbucket/myfile.csv")
   # do something
  s3lock.unlock("s3://myotherbucket/myfile.csv")
  return x*2

def test_lock2(x):
  time.sleep(2)
  s3lock = S3lock(dirlock="s3://mybucket/lock_hash")
  s3lock.lock("s3://myotherbucket/myfile.csv")
   # do something
  s3lock.unlock("s3://myotherbucket/myfile.csv")
  return x*3

def test_lock3(x):
  time.sleep(3)
  s3lock = S3lock(dirlock="s3://mybucket/lock_hash")
  s3lock.lock("s3://myotherbucket/myfile.csv")
   # do something
  s3lock.unlock("s3://myotherbucket/myfile.csv")
  return x*4

def test_lock_multiprocess():
    pool = mp.Pool(processes = 3)
    results = []
    results.append(pool.apply_async(test_lock1, (10,)))
    results.append(pool.apply_async(test_lock2, (20,)))
    results.append(pool.apply_async(test_lock3, (30,)))
    
    for r in results:
        print(r.get())

class cloudLock:
    def __init__(self, dirlock="s3://bucket", ntry_max=20, ntry_sleep=5):
        import fsspec, os
        self.dirlock      = dirlock if dirlock[-1] != "/" else dirlock[:-1]

        storage_type= "local"
        if "s3://" in dirlock:  storage_type= "s3"
        elif "gs://" in dirlock:  storage_type= "gcs"

        self.storage_type = storage_type
        if storage_type == 'local':
            self.fs = fsspec.filesystem('file')
        else:
            self.fs = fsspec.filesystem(storage_type, anon=False)

        self.ntry_max   = ntry_max   
        self.ntry_sleep = ntry_sleep  

    def lock(self, file_path:str):
        lock_path = self._get_lock_path(file_path)
                
        ntry = 0
        while ntry < self.ntry_max:
            try:
               time0 = str(time.time_ns()) 
               with self.fs.open(lock_path, 'wb') as lock_file:
                   lock_file.write(time0)

                   val = self.read_file(lock_path) ### check if writing is correct
                   if str(val) == str(time0) : 
                      break 

            except Exception as e :       
               print(lock_path, "blocked")


            ntry+=1
            self.sleep(self, ntry)

        if  ntry >= self.ntry_max:
            print("Maximum retries reached. The File is blocked")
            return False

        return True
    

    def unlock(self, file_path:str):
        lock_path   = self._get_lock_path(file_path)
                
        ntry = 0
        while ntry < self.ntry_max:
            try:
                val = self.read_file(lock_path) ### check if writing is correct
                if val is None or len(val)== "":
                   self.delete_file(lock_path)
                   return True

            except Exception as e :       
               print(lock_path, "blocked")

            ntry+=1
            self.sleep(self, ntry)

        if  ntry >= self.ntry_max:
            print("Maximum retries reached. The File is blocked")
            return False

        return True

    def read_file(self, file_path):
        lock_path = self._get_lock_path(file_path)
        ntry= 0
        while ntry < self.ntry_max:
          try :  
               with self.fs.open(lock_path, 'rb') as lock_file:
                   val = lock_file.read()
                   return val

          except Exception as e :
            pass

          ntry +=1
          self.sleep(ntry)


    def delete_file(self, file_path):
        lock_path = self._get_lock_path(file_path)
        ntry= 0
        while ntry < self.ntry_max:
          try :  
             if self.fs.exists(lock_path):
                  self.fs.rm(lock_path)
          except Exception as e :
             ntry +=1
             self.sleep(ntry)


    def _get_lock_path(self, file_path):
        return self.dirlock + "/" + str(self.hashx(file_path))

    def hashx(self, xstr:str, seed=123)->int:
        """ Computes xxhash value """
        import xxhash
        return xxhash.xxh64_intdigest(str(xstr), seed=seed)

    def sleep(self, ntry):
        dtsleep = 2.0 + self.ntry_sleep * ntry + random.uniform(0, 1)
        print(f"Retry - {ntry}, retry in {dtsleep}")      
        time.sleep( dtsleep )              

            




class S3lock:
    def __init__(self, dirlock:str, ntry_max=10, ntry_sleep=1):
        """
           Atomic Read, Atomic write on S3 text file.
           Many readers, many writers ---> All atomic.

        """
        self.s3      = boto3.client('s3')
        self.dirlock = dirlock  #### where all the lock are stored.
        #self.bucket, self.lock_key = dirlock.replace("s3://", "").split('/', 1)
        self.ntry_max   = ntry_max
        self.ntry_sleep = ntry_sleep

    def to_int(self, x):
        try:
            return int(x)
        except:  
            return -1

    def hashx(self, xstr:str, seed=123)->int:
        """ Computes xxhash value """
        import xxhash
        return xxhash.xxh64_intdigest(str(xstr), seed=seed)

    def sleep(self, ntry):

        tsleep = self.ntry_sleep * 2**ntry + random.uniform(0, 1)
        print(f"Retry - {ntry}")      
        print(f"Retrying in {tsleep}" )
        time.sleep( tsleep )              


    def lock(self, dirfile:str):
        """  Wait until we can lock the file.
             path1/path2/path2/dirlock/

        """
        dirfile2 = self.dirlock + "/" + str(self.hashx(dirfile))
        dirfile2 = dirfile2.replace("s3://", "").replace('//', "/").split('/')
        bucket, lock_key = dirfile2[0],  "/".join(dirfile2[1:] )
      
        try:
            self.s3.head_object(Bucket= bucket, Key= lock_key)
        except Exception as e:
            self.s3.put_object(Bucket=bucket, Key=lock_key, Body='0')
          
        ##### Wait until the file is Un-locked --> ntry_max
        ntry = 0
        while ntry < self.ntry_max:
            lock_code = self.s3.get_object(Bucket= bucket, Key= lock_key)["Body"].read().decode()

            #### File has zero value: Not locked --> we can lock it
            if self.to_int(lock_code) == 0:
                break

            ntry+=1
            self.sleep(self, ntry) ### wait a bit untl the file is unlocked
            log( f"waiting to unlock: {dirfile}")

        if  ntry >= self.ntry_max:
            print("Maximum retries reached. File has been locked by someone else.")
            return False


        ##### Insert Lock into the file with timestamp ############################
        ntry = 0
        while ntry < self.ntry_max:
            try:
                lock_code1 = str(time.time_ns())
                self.s3.put_object(Bucket= bucket, Key= lock_key, Body=lock_code1)

                ### Check if the write was done properly
                lock_code2 = self.s3.get_object(Bucket= bucket, Key= lock_key)["Body"].read().decode()
                if lock_code2 == lock_code1:
                    print("File Locked")
                    return True

                ntry+=1
                self.sleep(self, ntry)
            except Exception as e:
                log(e)
                time.sleep(1)

        if  ntry >= self.ntry_max:
            print("Maximum retries reached. The File is in use.")
            return False

        return False
    

    def unlock(self, dirfile:str):
        dirfile2 = self.dirlock + "/" + str(self.hashx(dirfile))
        dirfile2 = dirfile2.replace("s3://", "").replace('//', "/").split('/')
        bucket, lock_key = dirfile2[0],  "/".join(dirfile2[1:] )

        ntry = 0
        while ntry < self.ntry_max:
            try:
                self.s3.put_object(Bucket= bucket, Key= lock_key, Body='0')
                lock_code = self.s3.get_object(Bucket= bucket, Key= lock_key)["Body"].read().decode()
                if self.to_int(lock_code) == 0:
                    print("File Unlocked")
                    return True

                ntry+=1
                self.sleep(self, ntry)

            except Exception as e:
                log(e)

        if  ntry >= self.ntry_max:
            print("Maximum retries reached. Unable to unlock file after update.")
            return False
        
        return False













class S3Lock_csv:
    def __init__(self, dircsv:str, dirlock:str):
        self.s3 = boto3.client('s3', endpoint_url='http://localhost:4566')
        self.dircsv = dircsv
        self.s3lock = S3lock(dirlock)


    def read_atomic(self, ntry_max):
        islock = self.s3lock.lock(self.dircsv)
        """
             https://aws-sdk-pandas.readthedocs.io/en/stable/ 

        """
        import awswrangler 
        islock = self.s3lock.lock(self.dircsv)
        while islock and ntry < ntry_max : 
            time.sleep(5*ntry)
            ntry += 1

        self.s3lock.lock(self.dircsv) 
        bucket, dircsv1 = self.s3_split(self.dircsv)
        df =  self.s3.get_object(Bucket= bucket, Key= self.dircsv)["Body"].read().decode()
        self.s3lock.unlock(self.dircsv) 

        return df    


    def update(self, ntry_max, newrow:list):
        islock = self.s3lock.lock(self.dircsv, ntry_max=10)
        while islock and ntry < ntry_max : 
            time.sleep(5*ntry)
            ntry += 1

        if ntry == ntry_max :
             return False    

        self.s3lock.lock(self.dircsv) 
        bucket, dircsv1 = self.s3_split(self.dircsv)
        df =  self.s3.get_object(Bucket= bucket, Key= self.dircsv)["Body"].read().decode()

        newrows = pd.DataFrame(newrows)
        df = pd.concat((df, newrows))

        self.s3.get_object(Bucket= bucket, Key= self.dircsv)["Body"].put(df)
        self.s3lock.unlock(self.dircsv) 
        return True








def test10():
  """
  # Provide 10 other usage examples of this class
  #Here are 10 additional usage examples of the S3lock class:

  Locking multiple files sequentially:
  files = ["file1.txt", "file2.txt", "file3.txt"]
  for file in files:
      if lock_manager.lock(file):
          print(f"{file} locked and processed.")
          lock_manager.unlock(file)
      else:
          print(f"Failed to lock {file}.")
  Using the lock in a function:
  def process_file(filename):
      if lock_manager.lock(filename):
          print(f"Processing {filename}")
          # Process logic here
          lock_manager.unlock(filename)
      else:
          print("File is locked by another process.")
  process_file("data.txt")
  Locking with exception handling:
  try:
      if lock_manager.lock("critical_file.txt"):
          raise ValueError("Error processing file")
      else:
          print("File is currently locked.")
  except Exception as e:
      print(f"Exception occurred: {e}")
  finally:
      lock_manager.unlock("critical_file.txt")
  Locking files from a list with error handling:
  for file in ["doc1.txt", "doc2.txt", "doc3.txt"]:
      try:
          if not lock_manager.lock(file):
              print(f"Skipping {file}, it's locked.")
          else:
              # Process the file
              print(f"{file} processed.")
      finally:
          lock_manager.unlock(file)
  Using locks in a multithreaded environment:
  import threading

  def worker(file_name):
      if lock_manager.lock(file_name):
          print(f"{file_name} is being processed by {threading.current_thread().name}")
          lock_manager.unlock(file_name)
      else:
          print(f"{file_name} is locked.")

  threads = [threading.Thread(target=worker, args=(f"file{i}.txt",)) for i in range(5)]
  for thread in threads:
      thread.start()
  for thread in threads:
      thread.join()
  Locking and unlocking in a loop:
  while True:
      if lock_manager.lock("loop_file.txt"):
          print("Locked for processing")
          # Simulate work
          lock_manager.unlock("loop_file.txt")
          break
      else:
          print("Waiting for lock")
  Scheduled file processing with locking:
  import schedule

  def job():
      if lock_manager.lock("scheduled_file.txt"):
          print("File is processed on schedule")
          lock_manager.unlock("scheduled_file.txt")

  schedule.every().day.at("10:30").do(job)
  Conditional processing based on lock status:
  if lock_manager.lock("condition_file.txt"):
      # Perform operations if lock is successful
      print("Lock acquired, processing the file")
      lock_manager.unlock("condition_file.txt")
  else:
      print("Lock not acquired, skipping operations")
  Using lock for critical section in code:
  if lock_manager.lock("critical_section.txt"):
      try:
          # Critical code section
          print("Critical operations are being executed")
      finally:
          lock_manager.unlock("critical_section.txt")
  Lock management in a class method:
  class FileManager:
      def __init__(self, lock_manager, file_name):
          self.lock_manager = lock_manager
          self.file_name = file_name

      def process(self):
          if self.lock_manager.lock(self.file_name):
              print(f"{self.file_name} is being processed")
              self.lock_manager.unlock(self.file_name)
          else:
              print(f"Unable to lock {self.file_name}")

  manager = FileManager(lock_manager, "managed_file.txt")
  manager.process()
  These examples illustrate various scenarios where the S3lock class can be utilized to manage file access in a distributed environment, ensuring that files are not concurrently modified or accessed inappropriately.
  """



if __name__ == "__main__":
    import fire 
    fire.Fire()



