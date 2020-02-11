#!/bin/bash
import os
import requests
import time
import subprocess
import json
import re
import sys
from moviepy.editor import VideoFileClip
import shutil
from requests import exceptions

main_api = "api.mgghot.com"
path = os.getcwd()


def get_data_file(path_file):
    fo = open(path_file, "r")
    lines = fo.readlines()
    fo.close()
    stt_video = ''

    if len(lines) == 0:
        return ''

    return lines[0]


key = get_data_file("config/key.txt")

key_api = get_data_file("config/key_api.txt")


def get_list_video_by_api(channel_id, data_channel):
    results = []
    max_result = 30
    page_token = ''

    while len(results) < 31:
        url = "https://www.googleapis.com/youtube/v3/search?part=id&key=" \
              + str(key_api) + "&channelId=" + str(channel_id) + "&maxResults=" + str(max_result) \
              + "&order=date&pageToken=" + str(page_token)

        req = requests.get(url)

        list_item = json.loads(req.content)

        items = list_item['items']

        try:
            page_token = list_item['nextPageToken']
        except KeyError:
            page_token = ''

        for item in items:
            try:
                id_video = item['id']['videoId']
            except KeyError:
                id_video = ''

            if id_video != '' and id_video not in data_channel:
                results.append(id_video)

        if page_token == '':
            break

    return results


def get_thumbnail(url, path_thumb):
    print(url)
    try:
        stdout = subprocess.check_output(['youtube-dl', '--list-thumbnails', url])

        arr = str(stdout).split('\\n')
        url = ''

        for i in arr:
            temp = re.findall(r'http(.*?).jpg', str(i))

            if len(temp) > 0:
                url = 'http' + temp[0] + '.jpg'

        if url == '':
            return ''

        r = requests.get(url)

        if r.status_code == 200:
            with open(path_thumb + '/thumbnail.jpg', 'wb') as file:
                for chunk in r.iter_content(1024):
                    file.write(chunk)
    except:
        return ''

    return path_thumb + '/thumbnail.jpg'


def get_number_video(url):
    result = []

    try:
        stdout = subprocess.check_output(['youtube-dl', '-F', url])
        arr = str(stdout).split('\\n')

        audio = ''

        for item in arr:
            if 'm4a' in item:
                audio = item.split(' ')[0]

        for item in arr:
            if '1080' in item and 'mp4' in item:
                result.append(str(item.split(' ')[0]) + '+' + str(audio))

            if '720' in item and 'mp4' in item:
                result.append(str(item.split(' ')[0]) + '+' + str(audio))

        for item in arr:
            if '480' in item and 'mp4' in item:
                result.append(str(item.split(' ')[0]) + '+' + str(audio))

        for item in arr:
            if '360' in item and 'mp4' in item:
                result.append(str(item.split(' ')[0]) + '+' + str(audio))

        for item in arr:
            if '240' in item and 'mp4' in item:
                result.append(str(item.split(' ')[0]) + '+' + str(audio))
    except:
        return False

    return result


def download_video_from_youtube(id_video, path_page):
    numbers = get_number_video("https://www.youtube.com/watch?v=" + str(id_video))

    platform = get_platform()

    if numbers is False:
        return False

    print("Downloading...")
    for number in numbers:
        url = "youtube-dl -f " + str(number) + " -o " + path_page + '/' \
              + "input/input.%\(ext\)s https://www.youtube.com/watch?v=" + str(id_video)

        if platform == 'Windows':
            url = "youtube-dl -f " + str(number) + " -o " + path_page + '/' \
                  + "input/input.%(ext)s https://www.youtube.com/watch?v=" + str(id_video)

        os.system(url)

        check = get_file_upload(path_page)

        if check:
            return True

        empty_folder(path_page + '/input')

    return True


def get_tags(id_video):
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails&key=" + key_api + "&id=" + str(id_video)

    req = requests.get(url)
    items = json.loads(req.content)
    tags = ''
    title = ''
    result = []

    try:
        title = items['items'][0]['snippet']['title']
    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))

    try:
        tags = items['items'][0]['snippet']['tags']
    except KeyError as e:
        print('I got a KeyError - reason "%s"' % str(e))

    list_tag = ','.join(tags)
    result.append(title)
    result.append(list_tag)

    return result


def get_file_upload(path_page):
    filelist = os.listdir(path_page + '/input')

    for fichier in filelist:
        if "input.mp4" in fichier:
            return fichier

    return False


def getLength():
    filename = "input/input.mp4"
    clip = VideoFileClip(filename)

    return clip.duration


def get_ffmpeg(file_video, file_ffmpeg):
    path_file = 'ffmpeg-files/' + file_ffmpeg
    fo = open(path_file, "r")
    lines = fo.readlines()

    if len(lines) > 0:
        string_process = lines[0]
        string_process = string_process.replace("input.mp4", 'input/input.ts')
        string_process = string_process.replace("output.mp4", "output/" + str(file_video))

        return string_process

    return False


def process_video(file_name, length_cut):
    total_lentgh = getLength()

    string1 = "ffmpeg -ss " + str(length_cut) + " -i input/input.mp4 -t " \
              + str(total_lentgh) + " -c copy output/output.mp4"
    os.system(string1)

    # string = "ffmpeg -i /input/temp_input.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts /input/input.ts"
    # os.system(string)

    # string_ffmpeg = get_ffmpeg(file_name, 'text.txt')
    # os.system(string_ffmpeg)

    return 'output/output.mp4'


def uploadVideoToFacebook(file_name, access_token, cookie, title, des, thumb):
    file_size = os.path.getsize(file_name)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'referer': 'https://www.facebook.com/'
    }

    try:
        url1 = "https://graph-video.facebook.com/v2.3/me/videos?"
        data1 = {
            'access_token': access_token,
            'upload_phase': "start",
            "file_size": file_size
        }

        req1 = requests.post(url1, data=data1, headers=headers, cookies=cookie)

        content1 = json.loads(req1.content)

        upload_session_id = content1['upload_session_id']

        data2 = {
            'access_token': access_token,
            'upload_phase': 'transfer',
            'start_offset': 0,
            'upload_session_id': upload_session_id
        }

        up = {'video_file_chunk': (file_name, open(file_name, 'rb'), "multipart/form-data")}
        req2 = requests.post(url1, files=up, data=data2, headers=headers, cookies=cookie)

        data3 = {
            'access_token': access_token,
            'upload_phase': 'finish',
            'upload_session_id': upload_session_id,
            'title': title,
            'description': des
        }

        thumb = {'thumb': (thumb, open(thumb, 'rb'), "multipart/form-data")}

        req3 = requests.post(url1, files=thumb, data=data3, headers=headers, cookies=cookie)

        print(req3.content)
        result = json.loads(req3.content)['success'] is True
    except KeyError as e:
        print(e)
        return False

    return result


def getLengthVideo(input_video):
    platform = get_platform()

    if platform == 'Windows':
        string = 'ffprobe -i ' + input_video + ' -show_entries format=duration -v quiet -of csv="p=0"'
        result = subprocess.Popen(string, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = result.communicate()[0].strip()

        index = str(output).find('.')
        output = output[:index - 2]

        return int(output)

    string = 'ffprobe -i ' + input_video + ' -show_entries format=duration -v quiet -of csv="p=0"'

    result = subprocess.getoutput(string)
    output = result.split()[0].strip()
    output = float(output)
    output = int(output)
    # index = str(output).find('.')
    # output = output[:index - 2]

    return int(output)


def hanlde(access_token, cookie, name_title, description, genres, thumbnail, path_page, path_thumb):
    check = False
    file = get_file_upload(path_page)

    if file is False:
        empty_folder(path_page + "/input")

        return False

    file_name = path_thumb + '/input/' + file

    title = name_title
    des = description
    id_page = "me"
    link_video = file_name
    length_video = getLengthVideo(file_name)
    print(length_video)
    print("Uploading...")

    if length_video < 1200:
        check = uploadVideoToFacebook(link_video, access_token, cookie, title, des, thumbnail)
    else:
        if length_video > 3000:
            pass
        else:
            print("Upload by nodejs")

            if get_platform() == 'Windows':
                string_upload = "node upload-video-to-facebook/main.js --id=\"" + id_page + "\" --token=\"" + access_token \
                            + "\" --title=\"" + title + "\" --des=\"" \
                            + des + " \" --video=\"" + link_video + "\" --tags=\"" + genres + "\" --thumb=\"" + thumbnail + "\""
            else:
                string_upload = "sudo node upload-video-to-facebook/main.js --id=\"" + id_page + "\" --token=\"" + access_token \
                                + "\" --title=\"" + title + "\" --des=\"" \
                                + des + " \" --video=\"" + link_video + "\" --tags=\"" + genres + "\" --thumb=\"" + thumbnail + "\""

            os.system(string_upload)
        check = True

    empty_folder(path_page + "/input")

    if thumbnail != '':
        os.remove(path_page + '/thumbnail.jpg')

    return check


def get_list_video(info_api, path_page, path_thumb, account_id):
    print("Get list video..")
    source = info_api['source']
    data_channel = info_api['data_channel']

    channel_id = info_api['channel_id']
    access_token = info_api['access_token']
    cookie = info_api['cookie']

    items = get_list_video_by_api(source, data_channel)

    for id_video in items:
        info = get_tags(id_video)

        title = info[0]
        tags = info[1]

        description = title

        check = False

        thumbnail = get_thumbnail("https://www.youtube.com/watch?v=" + str(id_video), path_thumb)

        has_video = download_video_from_youtube(id_video, path_page)

        if has_video:
            check = hanlde(access_token, cookie, title, description, tags, thumbnail, path_page, path_thumb)
        else:
            save_data_by_api(channel_id, id_video)

        if check:
            save_data_by_api(channel_id, id_video)

            print("Done")
            print("Channel id:" + str(channel_id))
            # time.sleep(7200)
        else:
            # update_check_point(account_id)
            pass
        break


def save_data_by_api(channel_id, video_id):
    url = "http://" + main_api + "/data/set.php"

    data = {
        'video_id': video_id,
        'channel_id': channel_id,
        'key': key
    }

    req = requests.post(url, data=data)

    if req.status_code != 200:
        return False

    return True


def get_info_by_api(page_number, account_id):
    url = "http://" + main_api + "/accesstoken/get.php"

    results = {
        'status_code': 200,
        'data': []
    }
    data = {
        'page_number': page_number,
        'account_id': account_id,
        'key': key
    }

    req = requests.get(url, params=data)

    results['status_code'] = req.status_code

    if req.status_code != 200:
        return results

    datas = req.json()

    if int(datas['status']) != 0:
        access_token = datas['accesstoken']
        cookie = generate_cookie(datas['cookie'])
        channel_id = datas['channel_id']

        source = get_source(channel_id)
        data_channel = get_data_channel(channel_id)

        result = {
            'access_token': access_token,
            'cookie': cookie,
            'channel_id': channel_id,
            'source': source,
            'data_channel': data_channel
        }

        results['data'] = result

    return results


def get_source(channel_id):
    url = "http://" + main_api + "/channel/get.php"

    data = {
        'channel_id': channel_id,
        'key': key
    }

    req = requests.get(url, params=data)

    if req.status_code != 200:
        return False
    data = req.json()

    return data['records'][0]['source']


def get_data_channel(channel_id):
    url = "http://" + main_api + "/data/get.php"

    data = {
        'channel_id': channel_id,
        'key': key
    }

    req = requests.get(url, params=data)

    if req.status_code != 200:
        return False

    data = req.json()

    return data['records']


def check_and_create_dir(account_id, page_number):
    path_account = path + '/' + account_id
    path_page = path + '/' + account_id + '/' + page_number

    if os.path.isdir(account_id) is False:
        os.mkdir(path_account)

    if os.path.isdir(path_page) is False:
        os.mkdir(path_page)

    if os.path.isdir(path_page + "/input") is False:
        os.mkdir(path_page + "/input")

    if os.path.isdir(path_page + "/output") is False:
        os.mkdir(path_page + "/output")


def empty_folder(path_folder):
    shutil.rmtree(path_folder)
    os.makedirs(path_folder)


def update_data():
    channel_id = str(input("Channel id: "))
    list_id = str(input("List id: "))

    url = "http://" + main_api + "/data/update_data.php"

    data = {
        'channel_id': channel_id,
        'list_id': list_id
    }

    req = requests.post(url, data=data)
    print(req.status_code)


def setupDataToServer(account_id, page_number):
    source = str(input("Source: "))
    access_token = str(input("Access token: "))

    url = "http://" + main_api + "/accesstoken/set.php"

    data = {
        'account_id': account_id,
        'page_number': page_number,
        'source': source,
        'accesstoken': access_token,
        'key': key
    }

    req = requests.post(url, data=data)

    if req.status_code == 200:
        return True

    return False


def auto(arr):
    count_reset = 0
    stt = 0

    while True:
        try:
            for i in range(len(arr)):
                account_id = str(i + 1)

                if stt > len(arr[i]) - 1:
                    count_reset = count_reset + 1
                    continue

                try:
                    page_number = str(arr[i][stt])
                except IndexError:
                    count_reset = count_reset + 1
                    continue

                path_page = path + '/' + account_id + '/' + page_number
                path_thumb = account_id + '/' + page_number
                check_and_create_dir(account_id, page_number)

                result = get_info_by_api(page_number, account_id)

                if result['status_code'] != 200:
                    print("Setup new data!")
                    setupDataToServer(account_id, page_number)
                    result = get_info_by_api(page_number, account_id)

                info = result['data']

                if len(info) == 0:
                    count_reset = count_reset + 1
                    continue

                get_list_video(info, path_page, path_thumb, account_id)

            stt = stt + 1

            if count_reset >= len(arr):
                count_reset = 0
                stt = 0

            time.sleep(600)
        except exceptions.ConnectionError:
            print("Error Connect!")
            time.sleep(300)


def default():
    account_id = str(input("Account id: "))
    page_number = str(input("Page number: "))

    path_page = path + '/' + account_id + '/' + page_number
    path_thumb = account_id + '/' + page_number
    check_and_create_dir(account_id, page_number)

    while True:
        try:
            result = get_info_by_api(page_number, account_id)

            if result['status_code'] != 200:
                print("Setup new data!")
                setupDataToServer(account_id, page_number)
                result = get_info_by_api(page_number, account_id)

            info = result['data']

            if len(info) == 0:
                print("Account have been checkpoint!")
                continue

            get_list_video(info, path_page, path_thumb, account_id)

            time.sleep(600)
        except exceptions.ConnectionError:
            print("Error connect!")
            time.sleep(100)


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


def update_check_point(account_id):
    print("Update Check point! Account id: " + str(account_id))
    url = "http://" + main_api + "/account/updateCheckpoint.php"

    data = {
        'account_id': account_id,
        'key': key
    }

    req = requests.post(url, data=data)

    if req.status_code != 200:
        return False

    return True


def generate_cookie(string_cookie):
    if string_cookie == '':
        return {}

    string_cookie = string_cookie.replace(" ", "")
    arr = string_cookie.split(";")
    result = {}

    for i in range(len(arr)):
        key, value = arr[i].split("=")

        result[key] = value

    return result


if __name__ == '__main__':
    arr_page = [[1, 2, 3], [1, 2, 3], [1, 2, 4], [1, 2, 3]]

    option = str(input("One page (0) OR All page (1) ? "))

    if option == "0":
        default()
    else:
        auto(arr_page)
