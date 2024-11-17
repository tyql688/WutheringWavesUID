from ....utils.damage.abstract import WavesCharRegister


def shouanren_buff(attr, chain, resonLevel, isGroup, func_list):
    # 守岸人buff
    char_clz = WavesCharRegister.find_class(1505)
    if char_clz:
        s = char_clz()
        s.do_buff(attr, chain=chain, resonLevel=resonLevel, isGroup=isGroup, func_list=func_list)


def sanhua_buff(attr, chain, resonLevel, isGroup, func_list):
    # 散华buff
    char_clz = WavesCharRegister.find_class(1102)
    if char_clz:
        s = char_clz()
        s.do_buff(attr, chain=chain, resonLevel=resonLevel, isGroup=isGroup, func_list=func_list)
