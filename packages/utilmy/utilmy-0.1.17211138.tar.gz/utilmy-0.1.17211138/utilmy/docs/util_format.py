""" Tools to format all python code automatically

#### Remove all Docstring, comments:

    python $dirutilmy/docs/util_format.py   remove_docstring  --dirin youpath/**/*.py   --diroot yourpath/   --dirout yourpath2/   --dryrun 1 







"""

import os 
from utilmy import log 


def remove_docstring1(dirin, diroot=None, dirout=None, dryrun=1, tag="", checkcode=1, verbose=0):
    """ 
        python util_format.py remove_docstring --dirin "ztmp/*.py" --diroot "ztmp/"    --dirout ztmp/ztmp2/  --dryrun 0
    
    """
    run_clean_generic(dirin, diroot, dirout, dryrun, tag, checkcode, verbose,
              fun_cleaner= code_clean_dc):



def remove_docstring1(dirin, diroot=None, dirout=None, dryrun=1, tag="", checkcode=1, verbose=0):
    """ 
        python util_format.py  removedocstring2  --dirin "ztmp/*.py" --diroot "ztmp/"    --dirout ztmp/ztmp2/  --dryrun 0
    
    """
    run_clean_generic(dirin, diroot, dirout, dryrun, tag, checkcode, verbose,
              fun_cleaner= code_remove_docstrings):








#############################################################################################################
def run_clean_generic(dirin, diroot=None, dirout=None, dryrun=1, tag="", checkcode=1, verbose=0,
                      fun_cleaner = None

):
    """ 
    
    """
    from utilmy import glob_glob, os_makedirs, log
    import re, ast, traceback
    flist = glob_glob(dirin)
    log('N Files', len(flist))
    for fi in flist:
        if verbose>0: log(fi)
        try :
            with open(fi, 'r') as file1:
                data = file1.read()

            ### Clean the Code
            data = fun_cleaner(data)
            

            if checkcode>0:
                # log('checkcode')
                try:
                    ast.parse(data)
                except Exception as e:
                    log(fi, ":", e)
                    log(e)
                    traceback.print_exc()  # Remove to silence any errros
                    continue
            
            fi2 = fi
            if dirout is not None and str(diroot) in fi:
                fi2 = fi.replace(diroot, dirout)
                
            fi2 = fi2.replace(".py", f"{tag}.py" ) 
                
            os_makedirs(fi2)    
            if dryrun == 0 :        
                with open(fi2, 'w') as file1:
                    file1.write(data)
                    log('done', fi2)       
            else:
                log('dryrun', fi2)       
        except Exception as e :
            log(fi, e)   



def code_clean_dc(code):
    # Define markers for triple double quotes and triple single quotes
    DOC_DQ = '"""'
    DOC_SQ = "''''"
    
    code = code.split("\n")

    codenew = ""
    is_open_doc_string = False
    prev_line =""
    for line in code:
        line2      = line.strip()
        prev_line2 = prev_line.strip()
        if line2.startswith((DOC_DQ, DOC_SQ)) and line2.endswith((DOC_DQ, DOC_SQ)) and len(line2) > 3 :
            is_open_doc_string = False
            # if len(line2)>0 : prev_line = line
            continue
        
        if line.strip().startswith((DOC_DQ, DOC_SQ)) :
            if not prev_line2.endswith("+") and  not prev_line2.endswith(",") and  not prev_line2.endswith("\\")  :            
                is_open_doc_string = not is_open_doc_string
                continue  # Skip 

        if not is_open_doc_string :
            codenew += line + "\n"    
            if len(line2)>0 : prev_line = line

    return codenew[:-1] 




##############################################################################################################
##############################################################################################################
# Function to remove docstrings from the AST
def remove_docstrings_rec(node: ast.AST) -> Union[ast.AST, None]:
    # Check if the node is an expression and its value is a string (docstring)
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
        return None  # Return None to remove the docstring
    for field_name, field_value in ast.iter_fields(node):
        if isinstance(field_value, list):
            # Handle lists of child nodes
            new_values = [remove_docstrings_rec(item) for item in field_value if isinstance(item, ast.AST)]
            setattr(node, field_name, new_values)
        elif isinstance(field_value, ast.AST):
            # Handle individual child nodes
            new_field_value = remove_docstrings_rec(field_value)
            setattr(node, field_name, new_field_value)
    return node


# Function to remove docstrings from the source code
def code_remove_docstrings(source_code: str) -> str:
    tree: ast.AST = ast.parse(source_code)
    tree = remove_docstrings_rec(tree)
    clean_code: str = astor.to_source(tree)

    return clean_code


# Main function to read, process, and write the code
def main():
    with open(SOURCE_FILE, 'r') as file:
        raw_code: str = file.read()

    clean_code: str = code_remove_docstrings(raw_code)

    with open(SOURCE_FILE, 'w') as file:
        file.write(clean_code)



if __name__ == "__main__":
    fire.Fire()


