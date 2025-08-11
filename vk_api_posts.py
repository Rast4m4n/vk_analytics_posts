import csv
import vk_api
from datetime import datetime

ACCESS_TOKEN = ''
"""Токен доступа к общей информации страницы пользователя
    Получить токен можно в https://vkhost.github.io/ -> Vk.com -> скопировать access_token до &expires_in=
"""

# https://m.vk.com/1universe_1
USER_ID = '1universe_1'  
"""Никнейм/ID страницы пользователя"""

def create_vk_api_session(access_token: str):
    """ Создаем и вовзаращем апи VK.COM"""
    session = vk_api.VkApi(token=access_token)
    return session.get_api()

def fetch_wall_posts(vk_api_user, screen_name: str, count: int = 100):
    """Получаем посты со стены пользователя """
    owner_id = vk_api_user.utils.resolveScreenName(screen_name=screen_name)['object_id']
    response = vk_api_user.wall.get(owner_id=owner_id, count=count)
    
    posts = []
    for item in response.get('items', []):
        post_date = datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d %H:%M:%S')
        likes_count = item.get('likes', {}).get('count', 0)
        posts.append((post_date, likes_count))
    return posts


def save_posts_to_csv(posts, filename='vk_posts.csv'):
    """Сохраняет список постов в CSV файл"""
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['DateTime', 'Likes'])
        writer.writerows(posts)
    print(f"Данные успешно сохранены в файл '{filename}'")


def main():
    vk_api_user = create_vk_api_session(ACCESS_TOKEN)
    posts = fetch_wall_posts(vk_api_user, USER_ID, count=100)
    save_posts_to_csv(posts)

if __name__ == "__main__":
    main()