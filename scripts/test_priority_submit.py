import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from django.test import Client

c = Client()
resp = c.post('/api/complaints/create/', {
    'title':'Fan broken in room 202',
    'description':'The fan is broken and needs urgent repair in class 202.',
    'anonymous':'true',
    'priority':'Medium',
    'department':'Mechanical Engineering',
})
print('status:', resp.status_code)
try:
    print('json:', resp.json())
except Exception:
    print('text:', resp.content.decode('utf-8', errors='ignore'))
