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


def generate_rss(anime_updates):
    # 创建根节点
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    # 添加频道信息
    ET.SubElement(channel, "title").text = "番剧小窝 | 番剧更新"
    ET.SubElement(channel, "link").text = "/"
    ET.SubElement(channel, "description").text = "番剧小窝更新记录"
    ET.SubElement(channel, "language").text = "zh-cn"
    ET.SubElement(channel, "lastBuildDate").text = anime_updates[0]["fileDate"]

    # 添加每个番剧更新项
    for update in anime_updates:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = update["fileName"]
        ET.SubElement(item, "link").text = update_info_to_bgm_info_link(update)

        # 将文件大小从字节数转换为MB
        file_size_mb = update['fileSize'] / (1024 * 1024)
        
        description = ET.SubElement(item, "description")
        description.text = (
            f"文件大小: {file_size_mb:.1f} MB\n"
            f"更新时间: {update['fileDate']}\n"
        )
        
        ET.SubElement(item, "pubDate").text = update["fileDate"]
        ET.SubElement(item, "guid").text = update["fileHash"]

        # 确定文件的 MIME 类型
        file_extension = update["fileName"].split('.')[-1].lower()
        if file_extension == 'mp4':
            mime_type = 'video/mp4'
        elif file_extension == 'mkv':
            mime_type = 'video/x-matroska'
        else:
            mime_type = 'application/octet-stream'
        
        # 添加下载链接
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", update_info_to_bgm_download_link(update))
        enclosure.set("length", str(update["fileSize"]))
        enclosure.set("type", mime_type)

        # 添加观看链接
        watch_link = ET.SubElement(item, "watchLink")
        watch_link.text = update_info_to_bgm_watch_link(update)

    # 将XML格式化为字符串
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="   ")

    # 保存到文件
    with open(rss_xml_file, "w", encoding="utf-8") as f:
        f.write(xml_str)

# 示例番剧更新数组
anime_updates_example = [
    {
        "fileName": "[ANi] BLEACH 死神 千年血戰篇-相剋譚- - 31 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4",
        "filePath": "/root/Downloads/Sakiko/Bangumi/死神 千年血战篇/Season 1",
        "fileSize": 564933851,
        "fileHash": "d4db5e25ef494015264cb7c738c1c9510fd0f5a2",
        "fileDate": "2024-11-02T23:44:20.560360"
    },
    {
        "fileName": "[Nekomoe kissaten][Ao no Hako][06][1080p][JPSC].mp4",
        "filePath": "/root/Downloads/Sakiko/Bangumi/青之箱/Season 1",
        "fileSize": 490813890,
        "fileHash": "73ef5421c42f70bb519c35de08641bc4cb1f4bef",
        "fileDate": "2024-11-02T17:12:19.054477"
    },
    {
        "fileName": "[ANi] 蜻蛉高球 - 18 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4",
        "filePath": "/root/Downloads/Sakiko/Bangumi/喂！蜻蜓/Season 1",
        "fileSize": 302695972,
        "fileHash": "b256eeab78955be10695ebd11d5119fb72b2060d",
        "fileDate": "2024-11-02T09:39:46.145724"
    },
]

# 调用函数生成RSS文件
generate_rss(anime_updates_example)