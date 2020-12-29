import requests
import json
from pprint import pprint
import time
from time import strftime

token = ''  # token vk
tokenY = ''  # token Yandex
version = '5.126'  # version vk
user_id = 552934290  # id пользователя vk
photo_count = 5  # нужное количество фотографий


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version, user_id):
        self.token = token
        self.version = version
        self.user_id = user_id
        self.params = {'access_token': self.token, 'v': self.version}

    def get_photos(self, owner_id=None):

        if owner_id is None:
            owner_id = self.user_id
        self.owner_id = user_id

        photos_url = self.url + 'photos.get'
        self.photos_params = {'owner_id': self.owner_id,
                              'extended': 1,
                              'photo_sizes': 1,
                              'album_id': 'profile',
                              'count': photo_count}
        photos = requests.get(photos_url, params={**self.params, **self.photos_params}).json()['response']['items']
        print(f'Получено {photo_count} фотографий с профиля Vk')
        return photos

    def get_url_max_photos(self, photos):
        self.photos = photos

        for photo in photos:
            sizes = photo['sizes']

            def get_largest(size_dict):
                if size_dict['width'] >= size_dict['height']:
                    return size_dict['width']
                else:
                    return size_dict['height']

            max_size = max(sizes, key=get_largest)
            photo['sizes'] = max_size
        print('Отобраны фотографии максимального размера')
        return photos


class YaUploader:

    def __init__(self, tokenY):
        self.token = tokenY

    def put_folder(self, folder_name):
        response = requests.put('https://cloud-api.yandex.net/v1/disk/resources/',
                                headers={'authorization': tokenY},
                                params={'path': folder_name})
        print(f'На ЯндексДиск создана папка {folder_name}')


    def post_url_max_photos(self, photos, folder_name):
        self.photos = photos
        self.folder_name = folder_name
        photos_list = []
        response = requests.put('https://cloud-api.yandex.net/v1/disk/resources/',
                                headers={'authorization': tokenY},
                                params={'path': folder_name})

        for photo in photos:
            response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                     headers={'authorization': tokenY},
                                     params={'path': folder_name
                                                     + '/' + str(photo['likes']['count'])
                                                     + '_' + str(photo['date']), 'url': photo['sizes']['url']})
            photo_dict = {'file_name': str(photo['likes']['count']) + '_' + str(
                time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(int(photo['date'])))) + '.jpg',
                          'size': photo['sizes']['type']}
            photos_list.append(photo_dict)

        with open('photos_info.json', 'w') as file:
            json.dump(photos_list, file, indent=2, ensure_ascii=False)

        response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                 headers={'authorization': tokenY},
                                 params={'path': folder_name + '/' + 'photos_info.json'})
        url = response.json()['href']

        with open('photos_info.json', 'rb') as f:
            response = requests.put(url, data={'photos_info.json': f})

        print(f'На ЯндексДиск в папку {folder_name} сохранено {photo_count} фото, информация о которых передана в файле photos_info.json')

user1 = VkUser(token, version, user_id)

uploader = YaUploader(tokenY)

uploader.post_url_max_photos(user1.get_url_max_photos(user1.get_photos()), strftime("%Y-%m-%d_%H-%M-%S"))
