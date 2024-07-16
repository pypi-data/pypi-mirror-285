import utilmy

# CPU: I got this Error ---> AttributeError: module 'utilmy' has no attribute 'os_cpu'. Did you mean: 'os_copy'?
utilmy.os_cpu()

# Work with directories
utilmy.os_makedirs('test')
utilmy.os_removedirs('test')