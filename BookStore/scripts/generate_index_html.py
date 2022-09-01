import sys,django,os

sys.path.insert(0, '../')
sys.path.insert(0, '../apps')

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Bookstore.settings'
# 初始化django设置


django.setup()

from goods.crons import generate_static_index

if __name__ == '__main__':
    generate_static_index()
