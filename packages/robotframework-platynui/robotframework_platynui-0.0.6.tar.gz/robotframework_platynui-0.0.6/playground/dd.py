from pythonnet import load, get_runtime_info

import clr

#load("netfx")
#load("coreclr")

# #import clr
# from System import Environment
# from System.Runtime.InteropServices import RuntimeInformation

# print(get_runtime_info().kind)
# print(Environment.Version)
# print(RuntimeInformation.ProcessArchitecture)
# print(RuntimeInformation.FrameworkDescription)

print(get_runtime_info())