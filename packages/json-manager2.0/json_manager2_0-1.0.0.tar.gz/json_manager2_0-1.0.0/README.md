# JsonManager
 Json Manager for load, write and modify your json data


__Made by BOXER__


```python
#import module
from json_manager import setup

#setup your files
data = setup({'file_1': {'directory/myfile_1.json'},
              'file_2': 'directory/sub_directory/myfile_2.json'})

#print data files
print(data.file_1)
#output : {...}

print(data.file_2)
#output : {...}

#You can access sub_dictionary to
print(data.file_1.my_data)
#output : the value from the key "my_data"


'''Write all files to save data'''
data.write()
#This will rewrite all the files with their new data located in "data".
```
