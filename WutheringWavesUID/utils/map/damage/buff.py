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


def motefei_buff(attr, chain, resonLevel, isGroup, func_list):
    # 莫特斐buff
    char_clz = WavesCharRegister.find_class(1204)
    if char_clz:
        s = char_clz()
        s.do_buff(attr, chain=chain, resonLevel=resonLevel, isGroup=isGroup, func_list=func_list)


def weilinai_buff(attr, chain, resonLevel, isGroup, func_list):
    # 维里奈buff
    char_clz = WavesCharRegister.find_class(1503)
    if char_clz:
        s = char_clz()
        s.do_buff(attr, chain=chain, resonLevel=resonLevel, isGroup=isGroup, func_list=func_list)


def zhezhi_buff(attr, chain, resonLevel, isGroup, func_list):
    # 折枝buff
    char_clz = WavesCharRegister.find_class(1105)
    if char_clz:
        s = char_clz()
        s.do_buff(attr, chain=chain, resonLevel=resonLevel, isGroup=isGroup, func_list=func_list)
