vstestlocation = ""
if vstestlocation.endswith('"'):
    vstestlocation = vstestlocation[:-1]
if not vstestlocation.endswith("\\"):
    if vstestlocation != "":
        vstestlocation = vstestlocation + "\\"
vstestlocation = '"' + vstestlocation + 'vstest.console"'
if vstestlocation == '"vstest.console"':
    vstestlocation = "vstest.console"
print(vstestlocation)