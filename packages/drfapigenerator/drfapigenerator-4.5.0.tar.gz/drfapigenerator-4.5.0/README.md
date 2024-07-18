
# drfapigenerator

DRF API Generator simplifies API development in Django projects by automating the creation of RESTful APIs using Django Rest Framework (DRF). It generates necessary components such as viewsets, serializers, and routing based on your Django models, allowing developers to quickly expose CRUD (Create, Read, Update, Delete) operations via API endpoints. This tool enhances productivity by reducing manual configuration and boilerplate code, making it easier to build and maintain APIs in Django applications.


## Installation

add drfapigenerator in settings.py installed app.

```bash
INSTALLED_APPS = [
 -------------------
    'drfapigenerator',
 -------------------
]

```
generate automatic api's for your all models of your app.

```bash
python manage.py makeapi --app <your_app_name>
```
## Usage/Examples

To generate APIs for a specific Django app

Run the following management command, replacing <your_app_name> with the name of your Django app:

```python
python manage.py makeapi --app <your_app_name>
```

This command will automatically create necessary viewsets, serializers, and API routing for all models in the specified app.

you can see the generated API endpoints at http://localhost:8000/api/


## Example:

Suppose you have a Django app named myapp with a model MyModel defined as follows:

# myapp/models.py

from django.db import models

```
class MyModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
```

After running:

```
python manage.py makeapi --app myapp
```

You can access the API for MyModel at http://localhost:8000/api/mymodel/.



This structure provides clear instructions on how to install and use DRF API Generator in your Django project, including a practical example for generating APIs.




## Warning: Correcting the URL Configuration

In the current setup, there may be an issue with the registration of the accounts router. Ensure that your `urlpatterns` in your `urls.py` file are correctly configured as follows:

### Incorrect Configuration

The following code may lead to issues:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
   
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#*********This is accounts router registered by autoapi*********
from accounts.routers.routers import router as accounts_router 
urlpatterns.append(path('api/',include(accounts_router.urls)))
```

### Correct Configuration

Replace the above code with the following corrected configuration:

Ensure you import the `accounts_router` correctly:

```python
#*********This is accounts router registered by autoapi*********
from accounts.routers.routers import router as accounts_router
```

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(accounts_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```


## GitHub Repository

The source code for DRF API Generator is available on [GitHub](https://github.com/mddas2/drfapigenerator).

## About the Author

**Manoj Das**  
Senior Python Developer at Vrit Technologies 
5 years of experience

LinkedIn: [Manoj Das](https://www.linkedin.com/in/manoj-das-1a3867231/)


## License

[MIT](https://choosealicense.com/licenses/mit/)


MIT License

Copyright (c) [2024] [Manoj Kumar Das]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.





































