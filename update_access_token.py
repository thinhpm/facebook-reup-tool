import connect_db


def update_access_token(data):
    connect_db.update_token_access_token(data)

    return connect_db.update_status_access_token({'status': 1, 'page_number': data['page_number']})


def get_name_page(page_number):
    data = connect_db.get_data_page(page_number)

    return data['name']


if __name__ == '__main__':
    print("====== Change access token! ==============")
    page_number = str(input("Page number: "))
    print("Change access token for page: " + get_name_page(page_number))
    access_token = str(input("Access token: "))

    update_access_token({'page_number': page_number, 'access_token': access_token})
    print("Done!")
