import requests
import json


def write_file(path_file, data):
    f = open(path_file, "w")
    f.write(data)
    f.close()


def get_data_file(path_file):
    fo = open(path_file, "r")
    lines = fo.readlines()
    fo.close()
    stt_video = ''

    if len(lines) == 0:
        return ''

    return lines[0]


key_apis = get_data_file("config/key_api.txt").split(",")


def get_list_video_by_api(channel_id):
    results = []
    max_result = 30
    page_token = ''
    stt = 0
    key_api = key_apis[0]
    len_key_api = len(key_apis)
    maximum = 500

    while len(results) < maximum:
        url = "https://www.googleapis.com/youtube/v3/search?part=id&key=" \
              + str(key_api) + "&channelId=" + str(channel_id) + "&maxResults=" + str(max_result) \
              + "&order=date&pageToken=" + str(page_token)

        req = requests.get(url)

        list_item = json.loads(req.content)

        if 'items' not in list_item:
            stt = stt + 1

            if stt >= len_key_api:
                return []

            key_api = key_apis[stt]

            print("Try next key api...")
            continue

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

            if id_video != '':
                results.append(id_video)

        if page_token == '':
            break

    return results


if __name__ == '__main__':
    channel_id = str(input("Nhập channel id: "))
    data = get_list_video_by_api(channel_id)
    print("Total: %d" % len(data))
    string_data = '\",\"'.join(data)
    string_data = "\"" + string_data + "\""
    write_file("data-channel.txt", string_data)
