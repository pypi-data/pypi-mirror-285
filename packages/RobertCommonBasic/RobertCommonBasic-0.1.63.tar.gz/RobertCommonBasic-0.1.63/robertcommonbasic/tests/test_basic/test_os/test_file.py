from robertcommonbasic.basic.os.file import scan_files, del_file, del_folder, get_file_folder, get_file_name


def test_scan_files():
    files = scan_files(f"E:/Beop/Code/Git/datapushserver/file/real/*/20220323/**", False)
    print(files)


def test_scan_folder():
    files = scan_files(f"E:/file/**", False)
    print(files)


print(len(get_file_folder(r'aa.csv')))
print(get_file_folder(r'E:/aa.csv'))
del_folder(r'C:\DTU\point')
print()