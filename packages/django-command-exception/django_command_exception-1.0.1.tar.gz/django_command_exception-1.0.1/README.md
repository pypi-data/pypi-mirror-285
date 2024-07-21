### Installation
```bash
$ pip install django-command-exception
```

#### `settings.py`
```python
INSTALLED_APPS+=['django_command_exception']
```

#### `migrate`
```bash
$ python manage.py migrate
```

### Models
model|table|columns/fields
-|-|-
`CommandException`|`django_command_exception`|id,command,exc_class,exc_message,exc_traceback,created_at

### Examples
`call_command`
```python
from django_command_exception.models import CommandException

try:
    call_command(name)
except Exception as e:
    CommandException(command=name).save()
```

`BaseCommand`
```python
from django_command_exception.models import CommandException

class BaseCommand(BaseCommand):
    def execute(self, *args, **options):
        try:
            return super().execute(*args, **options)
        except Exception as e:
            CommandException(command=type(self).__module__.split('.')[-1]).save()
```

