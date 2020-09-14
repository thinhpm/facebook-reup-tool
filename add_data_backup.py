import connect_db


def add_data_backup(page_number, list_data_add):
    data = connect_db.get_data_page(page_number)
    print(data)
    channel_id = data['channel_id']

    for item in list_data_add:
        item_data = {
            'channel_id': channel_id,
            'video_id': item
        }

        connect_db.create_new_data(item_data)


if __name__ == '__main__':
    list_data_add = ["123", '456']

    print("====== Change access token! ==============")
    page_number = str(input("Page number: "))
    add_data_backup(page_number, list_data_add)
    print("Done!")
