from robertcommonbasic.basic.file.csv import values_to_csv, read_csv, pd, read_csv_rows, csv_to_values

points = [{'point_name': '192_168_1_184_47808_6_2_602_2_1', 'index': 0,
                                                       'point_writable': 'True',
                                                       'point_device_address': '6:20/616/192.168.1.12:47808',
                                                       'point_type': 'analogValue', 'point_property': 'presentValue',
                                                       'point_address': 1, 'description': 'None', 'point_value': '1.0',
                                                       'object_name': 'Random-602-1'},
          {'point_name': '192_168_1_184_47808_6_2_602_2_1', 'index': 0,
           'point_writable': 'True',
           'point_device_address': '6:20/616/192.168.1.12:47808',
           'point_type': 'analogValue', 'point_property': 'presentValue',
           'point_address': 1, 'description': 'None', 'point_value': '1.0',
           'object_name': 'Random-602-1'}
          ]

names = pd.read_csv(r'C:\Users\85101\Downloads\6577faea9b97e0d7b3e2e8f8.csv', low_memory=False, sep=',', keep_default_na=False, nrows=1).columns.tolist()
for time, values in read_csv(r'C:\Users\85101\Downloads\6577faea9b97e0d7b3e2e8f8.csv',).T.to_dict().items():
    print([[time, k, v] for k, v in values.items()])

print(csv_to_values(r'C:\Users\85101\Downloads\6577faea9b97e0d7b3e2e8f8.csv', False, True, index_col=0))
print(csv_to_values(r'C:\Users\85101\Downloads\6577faea9b97e0d7b3e2e8f8.csv', True, True, index_col=0))
#print(read_csv(r'C:\Users\85101\Downloads\6577faea9b97e0d7b3e2e8f8.csv'))
print(read_csv_rows(r'C:\Users\85101\Downloads\6577faea9b97e0d7b3e2e8f8.csv'))


datas = pd.read_csv(r'C:\Users\85101\Downloads\654dd71f8d5bd2bee3614d4a.csv', chunksize=500, low_memory=False,sep=',', keep_default_na=False)
for data in datas:
    for index, row in data.iterrows():
        print(index)
        print(row)


values_to_csv(points, 'E:/aa.csv', index=None)


