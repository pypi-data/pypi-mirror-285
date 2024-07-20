def read_file_to_list(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            string_list = file.readlines()
        return string_list
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到。")
        return None
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return None