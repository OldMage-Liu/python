from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2
import os
import re
def list_files_in_directory(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".mp3"):  # 确保只返回 MP3 文件
                files_list.append(os.path.join(root, file_name))
    return files_list
directory_path = r"C:\Users\ASUS\PycharmProjects\pythonProject\车载音乐"
files = list_files_in_directory(directory_path)
for mp3_file_path in files:
    audio = MP3(mp3_file_path, ID3=ID3)
    title = re.findall('- (.*?) .mp3', os.path.basename(mp3_file_path))
    print(mp3_file_path)
    title = title[0]  # 取出列表中的第一个元素
    print(title)
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio.save()