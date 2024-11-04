import sys
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# update.json 文件，保存番剧更新信息，为数组
update_json_file = '/www/wwwroot/pan.sakiko.top/home/data/update.json'
# update_json_file = './test/update.json'

# config.json 文件，bangumi-list-vue3 番剧小窝的 config 文件，将在其中bgmLastUpdate字段保存当前时间
config_json_file = '/www/wwwroot/pan.sakiko.top/home/data/config.json'
# config_json_file = './test/config.json'

# update_json数组长度限制
update_limit_length = 50


def get_input_data():
    """
    获取传入的数据
    从参数获取数据，返回一个字典
    """
    torrent_name = sys.argv[1]
    content_dir = sys.argv[2]
    root_dir = sys.argv[3]
    save_dir = sys.argv[4]
    files_num = sys.argv[5]
    torrent_size = sys.argv[6]
    file_hash = sys.argv[7]
    file_date = datetime.now().isoformat()
    
    return {
        "fileName": torrent_name,
        "filePath": save_dir,
        "fileSize": int(torrent_size),
        "fileHash": file_hash,
        "fileDate": file_date
    }

def read_update_json():
    """
    从update_json_file中读取数据
    返回数据
    """
    try:
        with open(update_json_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return []

def process_data(update_data, new_data):
    """
    处理数据
    在update_json中删除和当前filePath一样的
    将当前数据插入数组首部
    将长度限制update_limit_length（删除尾部）
    返回处理后的数据
    """
    update_data = [item for item in update_data if item['filePath'] != new_data['filePath']]
    update_data.insert(0, new_data)
    return update_data[:update_limit_length]

def save_update_json(data):
    """
    保存数据
    将数据保存回update_json_file
    """
    with open(update_json_file, 'w', encoding='utf-8') as file:
        # 使用 separators 参数生成紧凑的 JSON 文件
        json.dump(data, file, ensure_ascii=False, separators=(',', ':'))

def update_config_json():
    """
    修改config_json_file
    将bgmLastUpdate字段保存当前时间
    """
    try:
        with open(config_json_file, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
    except:
        config_data = {}

    config_data['bgmLastUpdate'] = datetime.now().isoformat()

    with open(config_json_file, 'w', encoding='utf-8') as file:
        # 保存为便于查看的格式 indent=4 指定每一级缩进使用4个空格
        json.dump(config_data, file, ensure_ascii=False, indent=4)

def main():
    # 获取传入的数据
    new_data = get_input_data()
    # 从update_json_file中读取数据
    update_data = read_update_json()
    # 处理数据
    processed_data = process_data(update_data, new_data)
    # 保存数据
    save_update_json(processed_data)
    # 修改config_json_file
    update_config_json()

if __name__ == "__main__":
    main()
