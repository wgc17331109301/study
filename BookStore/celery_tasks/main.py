import os
from celery import Celery

# 为celery使用django配置文件进行设置
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'BookStore.settings'

# 创建celery应用
celery_app = Celery('bookstore')

# 导入celery配置信息
celery_app.config_from_object('celery_tasks.config')

# 导入任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])

