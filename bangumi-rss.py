import sys
import json
from datetime import datetime, timezone, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom

# rss.xml RSS文件的保存位置
rss_xml_file = '/www/wwwroot/pan.sakiko.top/home/data/rss.xml'
# rss_xml_file = './test/rss.xml'

# update.json 文件，保存番剧更新信息，为数组
update_json_file = '/www/wwwroot/pan.sakiko.top/home/data/update.json'
# update_json_file = './test/update.json'

# follow 认证
# 不同域名5个订阅源
"""
https://bangumi.sakiko.top/home/data/rss.xml
https://sakiko.top/home/data/rss.xml
https://uika.top/home/data/rss.xml
https://bangumi.soyo.mom/home/data/rss.xml
https://bangumi.uika.uk/home/data/rss.xml

feedId:75862759381069824+userId:62789766742730752 bangumi.sakiko.top
feedId:75869532418666496+userId:62789766742730752 sakiko.top
feedId:75876404122691584+userId:62789766742730752 uika.top
feedId:76095364160960512+userId:62789766742730752 bangumi.soyo.mom
feedId:76153581122960384+userId:62789766742730752 bangumi.uika.uk
"""
follow_claim_description = '''
This message is used to verify that this feed belongs to me.
Join me in enjoying the next generation information browser https://follow.is.
feedId:75862759381069824+userId:62789766742730752
feedId:75869532418666496+userId:62789766742730752
feedId:75876404122691584+userId:62789766742730752
feedId:76095364160960512+userId:62789766742730752
feedId:76153581122960384+userId:62789766742730752
'''


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

def beijing_to_utc(beijing_time_str):
    """
    将北京时间字符串转换为UTC时间字符串
    :param beijing_time_str: 北京时间字符串，格式为 "%Y-%m-%dT%H:%M:%S.%f"
    :return: UTC时间字符串，格式为 "%Y-%m-%dT%H:%M:%S.%fZ"
    """
    # 将字符串转换为 datetime 对象
    beijing_time = datetime.strptime(beijing_time_str, "%Y-%m-%dT%H:%M:%S.%f")

    # 北京时间是 UTC+8
    beijing_tz = timezone(timedelta(hours=8))

    # 将时间本地化为北京时区
    beijing_time = beijing_time.replace(tzinfo=beijing_tz)

    # 转换为 UTC 时间
    utc_time = beijing_time.astimezone(timezone.utc)

    # 返回 UTC 时间字符串
    return utc_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

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


def generate_rss(anime_updates):
    # 创建根节点
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    # 添加频道信息
    ET.SubElement(channel, "title").text = "番剧小窝 | 更新记录"
    ET.SubElement(channel, "link").text = "/"
    ET.SubElement(channel, "description").text = "" + follow_claim_description
    ET.SubElement(channel, "language").text = "zh-cn"
    # ET.SubElement(channel, "lastBuildDate").text = beijing_to_utc(datetime.now().isoformat())

    # 添加每个番剧更新项
    for update in anime_updates:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = update["fileName"]
        ET.SubElement(item, "link").text = update_info_to_bgm_info_link(update)
        ET.SubElement(item, "pubDate").text = beijing_to_utc(update["fileDate"])
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
        date_time_str = datetime.strptime(update['fileDate'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%Y-%m-%d %H:%M:%S")
        
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
    # 从update_json_file中读取数据
    update_data = read_update_json()

    # 生成RSS
    generate_rss(update_data)

if __name__ == "__main__":
    main()
