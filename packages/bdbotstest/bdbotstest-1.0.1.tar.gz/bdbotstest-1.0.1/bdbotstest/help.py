import os

def getMyDeviceName():
    return os.name

def doCommand(command: str):
    return os.system(command)

def help():
    text = (
        f"Our Team is fully prepared to make Innovative Modules and Works\n\n"
        f"Stay with us 👑"
    )
    return text