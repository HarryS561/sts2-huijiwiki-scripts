import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

base_path = 'C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/export/slay-the-spire-2'

exist = {image.name for image in site.allimages()}
# 之后官方改卡图的话就得重新传一遍，不能有旧图就不传了

def update_card_images(ids: list[str]):
    ids = [id.upper() for id in ids]
    print(ids)
    card_images = os.path.join(base_path, 'card-images')
    for filename in os.listdir(card_images):
        if filename.endswith('.png') and filename.replace('Plus1', '_UPGRADE').replace('.png', '') in ids:
            new_name = filename.lower().replace('plus1', '_upgrade')
            # if not ("文件:" + new_name.capitalize().replace('_', ' ')) in exist:
            if not False:
                print(f"正在上传 {filename} -> {new_name}")
                for attempt in range(1, 5):
                    try:
                        site.upload(os.path.join(card_images, filename), new_name, '[[分类:卡牌图像]]', True)
                        break
                    except APIError as e:
                        if e.code == "fileexists-no-change":
                            # 远端已经是完全相同的版本，不算真正失败
                            print(f"文件 {filename} 内容没变化，跳过上传")
                            break
                        elif e.code == "empty-file":
                            continue
                        else:
                            raise

# for en, cn in [('relics', '遗物'), ('potions', '药水'), ('enchantments', '附魔'), ('afflictions', '苦痛')]:
#     images = os.path.join(base_path, en)
#     for filename in tqdm(os.listdir(images)):
#         if filename.endswith('.png'):
#             new_name = filename.lower()
#             if not ("文件:" + new_name.capitalize().replace('_', ' ')) in exist:
#                 site.upload(os.path.join(images, filename), new_name, f'[[分类:{cn}图像]]', True)

if __name__ == "__main__":
    images_to_upload = ['BEAT_INTO_SHAPE', 'BEAT_INTO_SHAPE_UPGRADE', 
                        'BLACK_HOLE', 'BLACK_HOLE_UPGRADE', 
                        'BOOST_AWAY', 'BOOST_AWAY_UPGRADE', 
                        'BURST', 'CLEANSE', 'CLEANSE_UPGRADE', 
                        'EIDOLON', 'EIDOLON_UPGRADE', 
                        'END_OF_DAYS', 'END_OF_DAYS_UPGRADE', 
                        'EVIL_EYE', 'EVIL_EYE_UPGRADE', 
                        'EXPERTISE', 'EXPERTISE_UPGRADE', 
                        'FERAL', 'FERAL_UPGRADE', 
                        'GANG_UP', 'GANG_UP_UPGRADE', 
                        'HIGH_FIVE', 'HIGH_FIVE_UPGRADE', 
                        'SCULPTING_STRIKE', 'SCULPTING_STRIKE_UPGRADE', 
                        'SNAP', 'SNAP_UPGRADE', 
                        'TRACKING', 'TRACKING_UPGRADE', 
                        'WHISTLE', 'WHISTLE_UPGRADE', 
                        'WHITE_NOISE', 'WHITE_NOISE_UPGRADE']
    update_card_images(images_to_upload)