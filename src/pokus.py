import os


print()
if os.path.exists('data.cvs'):
    os.remove('data.cvs')
    print('Hotovo')
else:
    print("Nemám co mazat")