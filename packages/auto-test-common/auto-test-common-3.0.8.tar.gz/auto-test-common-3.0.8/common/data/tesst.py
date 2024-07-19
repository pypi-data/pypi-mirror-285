import pyexcel
from ext_list import ExtList
from common.data.data_process import DataProcess
# book = pyexcel.get_book(file_name="data.xls")
# print(book['Sheet1'])
_list = ExtList([{'name': 'Alice1;Alice2', 'age': '25'},{'name': 'Alice2', 'age': '26;34'}, {'name': 'Bob', 'age': '30'},{'name': 'Alice3', 'age': 27}])
_list2 = ExtList([{'name': 'Alice', 'age': 25},{'name': 'Alice2', 'age': 25}])
_list3 = ExtList(filter(lambda x:(str(x['name']).find(';')>=0 or str(x['age']).find(';')>=0) , _list))

_count1 = _list.in_('name',['Bob'])
# _count1 = _list.in_('name',['Alice1','Bob1'])
_count2 = _list.in_('age',[273,253])
_count1.extend(_count2)
_count1.extend(_list3)
_test = _count1
_test = DataProcess.list_dict_duplicate_removal_byKey(_test, 'name22')
_test = DataProcess.list_dict_duplicate_removal_byKey(_test, 'age')
print(_test)

_str="33"
_str.find(';')