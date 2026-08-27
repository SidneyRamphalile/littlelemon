from django.test import TestCase
from rest_framework.test import APIClient
from restaurant.models import Menu
from restaurant.serializers import MenuSerializer


class MenuViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        Menu.objects.create(title="Greek Salad", price=12.50, inventory=25)
        Menu.objects.create(title="Bruschetta", price=8.00, inventory=40)
        Menu.objects.create(title="Lemon Dessert", price=6.75, inventory=30)

    def test_getall(self):
        response = self.client.get('/restaurant/menu/')
        items = Menu.objects.all()
        serializer = MenuSerializer(items, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)
