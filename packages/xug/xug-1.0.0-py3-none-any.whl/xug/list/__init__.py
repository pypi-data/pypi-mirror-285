
def split_list(input_list, segment_length):
    '''
    将列表分割为多个长度相同的列表
    :param input_list: 待分割的列表
    :param segment_length: 分割长度
    :return: 分割后的列表'''

    segment_length=int(segment_length)
    if segment_length <= 0:
        raise ValueError("分段长度必须为正整数")
    return [input_list[i:i + segment_length] for i in range(0, len(input_list), segment_length)]

# 获取指定列
def get_column(matrix, column_index):
    '''
    获取指定列
    :param matrix: 二维列表
    :param column_index: 列序号
    :return: 列数据列表'''
    if column_index <= 0 or column_index > len(matrix[0]):
        raise ValueError("无效的列序号")
    return [row[column_index-1] for row in matrix]