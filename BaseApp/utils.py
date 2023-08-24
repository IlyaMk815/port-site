from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count
from django.core.cache import cache

from .models import *


# class TestUserMixin(UserPassesTestMixin):
#
#     def test_func(self):
#         object = self.get_object()
#         if self.request.user == object.user:
#             return True
#         return False
