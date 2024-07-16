import ast
import glob
import os
import shutil
import subprocess
import sys

from tqdm import tqdm

# from IPython.nbformat import current as nbformat
# from IPython.nbconvert import PythonExporter
import nbformat
from nbconvert import PythonExporter


def scan(data_file):
    """function scan.
    Doc::
            
            Args:
                data_file:   
            Returns:
                
    """
    # note: I have checked os_file_listall, I think the following will be better
    files = glob.glob(data_file + "/**/*.ipynb", recursive=True)
    # remove .ipynb_checkpoints
    files = [s for s in files if ".ipynb_checkpoints" not in s]

    print("scan files done ... ")
    return files


def convert_topython(source_files, data_file, dirout):
    """function convert_topython.
    Doc::
            
            Args:
                source_files:   
                data_file:   
                dirout:   
            Returns:
                
    """

    dst_files = []

    for filepath in tqdm(source_files):
        # export_path = '%s/%s.py'%(dirout, os.path.basename(filepath[:-6]))
        export_path = filepath.replace(data_file, dirout)
        export_path = export_path[:-6] + ".py"
        # print(export_path)

        with open(filepath) as fh:
            nb = nbformat.reads(fh.read(), nbformat.NO_CONVERT)

        exporter = PythonExporter()
        source, meta = exporter.from_notebook_node(nb)

        with open(export_path, "w+") as fh:
            fh.writelines(source)
            # fh.writelines(source.encode('utf-8'))

        dst_files.append(export_path)

    print("convert to python file done ...")
    return dst_files


def check(file_list, dump=False):
    """function check.
    Doc::
            
            Args:
                file_list:   
                dump:   
            Returns:
                
    """

    error_list = []
    error_msgs = []
    for f in file_list:
        with open(f, "r") as f1:
            codesource = f1.read()
        try:
            p = ast.parse(codesource)
        except Exception as e:
            # print('-'*30)
            # print(f, str(e))
            # print('-'*30)

            # error_list.append(f)
            error_list.append(os.path.abspath(f))
            error_msgs.append(str(e))

    if dump:
        with open("./issue_files.csv", "w") as fp:
            fp.write("file,error_info\n")
            for file, error in zip(error_list, error_msgs):
                fp.write("%s,%s\n" % (file, error))

    print("check done ... ")
    return error_list


def Run():
    """function Run.
    Doc::
            
            Args:
            Returns:
                
    """
    if len(sys.argv) != 3:
        print("Syntax: %s src_ipny_fold dst_py_fold" % sys.argv[0])
        sys.exit(0)
    (data_file, dirout) = sys.argv[1:]

    # scan file recursively
    source_files = scan(data_file)
    # print(source_files)

    # make some dirs in dst fold
    if os.path.exists(dirout):
        inp = input("output dir exists, re-generate? (y/n): ")
        if inp == "y":
            shutil.rmtree(dirout)
        else:
            sys.exit(0)

    shutil.copytree(data_file, dirout)
    dst_files_to_delete = scan(dirout)
    for s in dst_files_to_delete:
        os.remove(s)

    # convert all files
    dst_files = convert_topython(source_files, data_file, dirout)

    # check converted script file are runnable
    # dump log file, default to the current fold
    error_list = check(dst_files, dump=True)

    # clean error file
    for s in error_list:
        os.remove(s)
    print(
        "%d were converted successfully, %d cause error"
        % (len(dst_files) - len(error_list), len(error_list))
    )


if __name__ == "__main__":
    Run()
