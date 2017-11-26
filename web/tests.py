from django.test import TestCase
from web.models import *

obj = News.objects.all().values_list("ctime")
print(obj)