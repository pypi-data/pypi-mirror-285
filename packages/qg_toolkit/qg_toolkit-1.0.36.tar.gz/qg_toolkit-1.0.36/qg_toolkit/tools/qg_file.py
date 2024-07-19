from urllib.parse import urlparse, parse_qs
import yaml
import csv

from loguru import logger


class QGFile:
    @staticmethod
    def save_to_file(file_path, log):
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f'{log}\n')
            f.close()


    @staticmethod
    def save_to_file_deduplicate(file_path, log):
        """去重插入行"""
        # 打开输入文件并读取所有行
        with open(f'{file_path}', 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        # 确保新行末尾有换行符
        if not log.endswith('\n'):
            log += '\n'
        # 将新行插入到行列表中
        lines.append(log)
        # 去除重复行，并保持原有顺序
        unique_lines = list(dict.fromkeys(lines))
        # 将去重后的行写入输出文件
        with open(f'{file_path}', 'w', encoding='utf-8') as outfile:
            outfile.writelines(unique_lines)
            outfile.close()

    @staticmethod
    def txt_to_array(file_path: object, split: object = '----') -> list:
        lines = open(file_path, 'r', encoding='utf-8').readlines()
        arr = [[z.strip() for z in x.split(split)] for x in lines]
        return arr

    @classmethod
    def get_row_from_file_index(cls, file_path: object, split: object = '----', index: int = 1):
        return cls.txt_to_array(file_path, split)[index - 1]

    @staticmethod
    def array_to_txt(arr, to_file_path) -> list:
        with open(to_file_path, 'a', encoding='utf-8') as f:
            for cols in arr:
                log = "----".join(cols)
                f.write(f'{log}\n')
            f.close()
        lines = open(to_file_path, 'r', encoding='utf-8').readlines()
        arr = [[z.strip() for z in x.split(to_file_path)] for x in lines]
        return arr

    @staticmethod
    def read_yaml(file_path):
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def url_params_to_object(url, key=None):
        # 解析URL
        parsed_url = urlparse(url)
        # 获取查询字符串参数并转换为字典对象
        query_params = parse_qs(parsed_url.query)
        # 处理字典对象，将每个参数的值转换为单个值而不是数组
        for key, value in query_params.items():
            query_params[key] = value[0]
        # 返回转换后的字典对象
        if key:
            return query_params.get(key)
        return query_params

    @staticmethod
    def csv_to_array(file_path, has_header=True, delimiter=','):
        """解汇csv文件，返回数组对象"""
        with open(file_path, 'r') as f:
            reader = csv.reader(f, delimiter=delimiter)
            all_list = list(reader)
            if len(all_list) == 0:
                return []
            if has_header:
                head_list = all_list[0]
                data_list = all_list[1:]
                array_obj = []
                for data in data_list:
                    obj = {}
                    for i, attr in enumerate(head_list, start=0):
                        obj[attr] = data[i]
                    array_obj.append(obj)
                # logger.info(array_obj)
                return array_obj
            else:
                return all_list

    @staticmethod
    def to_yaml(wallet_path, dis_path, tw_path, to_path):
        """往文件修改新增"""
        wallets = QGFile.csv_to_array(wallet_path)
        # wallets = QGUtil.txt_to_array(wallet_path)
        dis_tokens = QGFile.txt_to_array(dis_path)
        tws = QGFile.txt_to_array(tw_path)
        full_data = {
            "accounts": []
        }
        for i, row in enumerate(wallets, start=0):
            addr1 = row.get("addr")
            pk1 = row.get("pk")
            if i <= 21:
                continue

            else:
                obj = {
                }
                full_data['accounts'].append(obj)
        with open(to_path, 'w') as file:
            yaml.dump(full_data, file)
        logger.info("数据已成功修改并写回到YAML文件。")

    @staticmethod
    def save_to_yaml(to_path, full_data):
        with open(to_path, 'w') as file:
            yaml.dump(full_data, file)
        logger.info("数据已成功修改并写回到YAML文件。")

