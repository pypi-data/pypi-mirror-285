from robertcommonbasic.basic.os.path import get_spilt_text

name = b'GuangZhou_Westin_Hotel_Energy_Fun_Report4.4.xlsx'
if not isinstance(name, bytes):
    name = name.decode()
print(get_spilt_text(name))
