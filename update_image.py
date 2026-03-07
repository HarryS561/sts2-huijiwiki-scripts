from utils import *

base_path = 'C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/export/slay-the-spire-2'

exist = {image.name for image in site.allimages()}
# 之后官方改卡图的话就得重新传一遍，不能有旧图就不传了

card_images = os.path.join(base_path, 'card-images')
for filename in os.listdir(card_images):
    if filename.endswith('.png'):
        new_name = filename.lower().replace('plus1', '_upgrade')
        if not ("文件:" + new_name.capitalize().replace('_', ' ')) in exist:
            site.upload(os.path.join(card_images, filename), new_name, '[[分类:卡牌图像]]', True)

for en, cn in [('relics', '遗物'), ('potions', '药水'), ('enchantments', '附魔'), ('afflictions', '苦痛')]:
    images = os.path.join(base_path, en)
    for filename in tqdm(os.listdir(images)):
        if filename.endswith('.png'):
            new_name = filename.lower()
            if not ("文件:" + new_name.capitalize().replace('_', ' ')) in exist:
                site.upload(os.path.join(images, filename), new_name, f'[[分类:{cn}图像]]', True)
