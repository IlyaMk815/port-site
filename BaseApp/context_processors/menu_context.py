class MenuCreator:
    """
    A class that forms a nested collection to pass to the context
    """

    def __init__(self):
        self.menu = []

    def menu_create(self, **kwargs):
        for part in kwargs:
            self.menu.append({'url_name': part, 'title': kwargs[part]})
        return self.menu


BASE_MENU_CONTEXT = MenuCreator().menu_create(home='Home', about='About', GitHub='GitHub',
                                              contacts='Contacts')
USER_MENU_CONTEXT = MenuCreator().menu_create(profile_redirect='Профиль', add_post='Добавить статью',
                                              user_posts='Созданные статьи', rated_posts='Оценённые статьи')

CONTACT_CONTEXT = [
        {'contact': 'Telegram', 'contact_data': '/'},
        {'contact': '@mail', 'contact_data': 'im.workpost@mail.ru'},
        {'contact': 'Phone', 'contact_data': '/'},
    ]

PROFILE_MENU_CONTEXT = MenuCreator().menu_create(profile_update_form='Редактировать профиль',
                                                 password_change='Сменить пароль')


def base_menu(request):
    return {
        'base_menu': BASE_MENU_CONTEXT
    }


def user_menu(request):
    return {
        'user_menu': USER_MENU_CONTEXT
    }


def my_contacts(request):
    return {
        'my_contacts': CONTACT_CONTEXT
    }


def profile_menu(request):
    return {
        'profile_menu': PROFILE_MENU_CONTEXT
    }
