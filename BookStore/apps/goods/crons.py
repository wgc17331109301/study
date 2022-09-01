from goods.models import goods
from django.template import loader


# 页面静态化的视图
def generate_static_index():
    # 查到所有的商品
    goods_list = goods.objects.all()
    context = {'all_goods': goods_list}
    template = loader.get_template('index.html')
    html_text = template.render(context=context)

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(html_text)
