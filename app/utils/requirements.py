import json, os


def init():
    if not os.path.exists('data'):
        os.mkdir('data')
    if not os.path.exists('data/accounts'):
        os.mkdir('data/accounts')
    if not os.path.exists('data/accounts/raw'):
        os.mkdir('data/accounts/raw')
    if not os.path.exists('data/accounts/good'):
        os.mkdir('data/accounts/good')
    # if not os.path.exists('data/config.json'):
    #     with open(f'data/config.json', 'w', encoding='utf-8') as file:
    #         json.dump({'inventories': [['304930', '2']]}, file, indent=4, ensure_ascii=False)





    pass