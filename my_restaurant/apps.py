from django.apps import AppConfig


class MyRestaurantConfig(AppConfig):
    name = 'my_restaurant'
    def ready(self):
        import my_restaurant.signals