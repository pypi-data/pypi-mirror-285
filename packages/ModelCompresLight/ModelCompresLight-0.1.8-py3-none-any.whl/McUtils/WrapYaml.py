import yaml

def asyn_yaml_config(connect_config:str,recommend_config:str,rank:int=0):
    """
    write recommend_config ----->connect_config to compression

    :param connect_config:
    :param recommend_config:
    :param rank:
    :return:
    """
    connected=yaml.load(open(connect_config))
    recommend=yaml.load(open(recommend_config))

    mask_layers = connected['mask_layers']
    for key, info in mask_layers.items():
        layer_name = key
        if layer_name in recommend.keys():
            lens = len(recommend[layer_name]['index_list'])
            if rank<=lens-1:
                info['recommend_len'] = recommend[layer_name]['index_list'][rank]

            else:

                info['recommend_len'] = recommend[layer_name]['index_list'][lens-1]


    with open(connect_config, "w") as f:
        yaml.safe_dump(connected, f, encoding='utf-8', allow_unicode=True)

def CleanRecommend(connect_config):
    connected = yaml.load(open(connect_config))
    mask_layers = connected['mask_layers']

    for key, info in mask_layers.items():

        info['recommend_len'] = None

    with open(connect_config, "w") as f:
        yaml.safe_dump(connected, f, encoding='utf-8', allow_unicode=True)

def asyn_net_pth(orinet,pth:str):
    """
    original net loads pth file.

    :return:
    """

