import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *




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