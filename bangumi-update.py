import sys
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# rss.xml RSS文件的保存位置，空字符串即为禁用
# rss_xml_file = '/www/wwwroot/pan.sakiko.top/home/data/rss.xml'
rss_xml_file = './test/rss.xml'

# update.json 文件，保存番剧更新信息，为数组
# update_json_file = '/www/wwwroot/pan.sakiko.top/home/data/update.json'
update_json_file = './test/update.json'

# config.json 文件，bangumi-list-vue3 番剧小窝的 config 文件，将在其中bgmLastUpdate字段保存当前时间
# config_json_file = '/www/wwwroot/pan.sakiko.top/home/data/config.json'
config_json_file = './test/config.json'

# update_json数组长度限制
update_limit_length = 20

# RSS中要用到的链接处理逻辑
def update_info_to_bgm_watch_link(update_info):
    """
    用 BgmUpdateInfo 拼接观看链接
    filePath: "/root/Downloads/Sakiko/Bangumi/魔法光源股份有限公司/Season 1"
    fileName: "[LoliHouse] Kabushikigaisha Magi-Lumière - 04 [WebRip 1080p HEVC-10bit AAC SRTx2].mkv"
    watchlink: "/Bangumi/魔法光源股份有限公司/Season 1/[LoliHouse] Kabushikigaisha Magi-Lumière - 04 [WebRip 1080p HEVC-10bit AAC SRTx2].mkv"
    """
    dir_path = update_info['filePath'][len('/root/Downloads/Sakiko'):]
    return dir_path + '/' + update_info['fileName']

def update_info_to_bgm_download_link(update_info):
    """
    用 BgmUpdateInfo 拼接下载链接
    downloadlink: "/d/onedrive/Sakiko/Bangumi/魔法光源股份有限公司/Season 1/[LoliHouse] Kabushikigaisha Magi-Lumière - 04 [WebRip 1080p HEVC-10bit AAC SRTx2].mkv"
    """
    return '/d/onedrive/Sakiko' + update_info_to_bgm_watch_link(update_info)

def update_info_to_bgm_info_link(update_info):
    """
    用 BgmUpdateInfo 拼接详情链接
    infoLink: "/Bangumi/魔法光源股份有限公司"
    """
    watchlink = update_info_to_bgm_watch_link(update_info)
    # 获取前三个路径部分 ['', 'Bangumi', '魔法光源股份有限公司'] ，然后拼接
    return '/'.join(watchlink.split('/')[:3])

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

def generate_rss(anime_updates):
    # 创建根节点
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    # 添加频道信息
    ET.SubElement(channel, "title").text = "番剧小窝 | 番剧更新"
    ET.SubElement(channel, "link").text = "/"
    ET.SubElement(channel, "description").text = "番剧小窝更新记录"
    ET.SubElement(channel, "language").text = "zh-cn"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().isoformat()

    # 添加每个番剧更新项
    for update in anime_updates:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = update["fileName"]
        ET.SubElement(item, "link").text = update_info_to_bgm_info_link(update)
        ET.SubElement(item, "pubDate").text = update["fileDate"]
        ET.SubElement(item, "guid").text = update["fileHash"]
        # 观看链接
        watch_link = ET.SubElement(item, "watchLink")
        watch_link.text = update_info_to_bgm_watch_link(update)
        # 下载链接
        download_link = ET.SubElement(item, "downloadLink")
        download_link.text = update_info_to_bgm_download_link(update)

        # 将文件大小从字节数转换为MB
        file_size_mb = update['fileSize'] / (1024 * 1024)
        # 日期格式化
        date_time_str = datetime.fromisoformat(update['fileDate']).strftime("%Y-%m-%d %H:%M:%S")
        
        description = ET.SubElement(item, "description")
        description.text = f"""
          <p>文件大小: {file_size_mb:.1f} MB</p>
          <p>更新时间: {date_time_str}</p>
          <p><a href="{update_info_to_bgm_watch_link(update)}">观看</a></p>
          <p><a href="{update_info_to_bgm_download_link(update)}">下载</a></p>
        """

    # 将XML格式化为字符串
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="   ")

    # 保存到文件
    with open(rss_xml_file, "w", encoding="utf-8") as f:
        f.write(xml_str)


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
