### Installation
```bash
$ pip install django-urls-templateview
```

#### `settings.py`
```python
INSTALLED_APPS+=['django_urls_templateview']
```

#### `migrate`
```bash
$ python manage.py migrate
```

### Features
+   `urls.py` TemplateView `urlpatterns`
+   admin

### Models
model|table|columns/fields
-|-|-
`Map`|`django_urls_templateview`|`id`,`url`,`template_name`

### Examples
`urls.py`
```python
from django.db import connection
from django.views.generic.base import TemplateView

urlpatterns = []

cursor = connection.cursor()
cursor.execute("SELECT url,template_name FROM public.django_urls_templateview")
for url,template_name in cursor.fetchall():
    urlpatterns.insert(0,path(url, TemplateView.as_view(template_name=template_name)))
```

