from .KeyboardData import KeyboardObject
from .Types import KeyboardKey, SupportDirection

# keyboardObjecttype
# 0 = normal switch
# 1 = stabalizer foot


def updateLayoutData(keyboardObject: KeyboardObject):
    keys = 0
    for row in keyboardObject.layoutData:
        key: KeyboardKey
        for key in row:
            keys += 1
            if keyboardObject.doubleSwitchForSpace and key.width >= 4:
                key.isMultiSwitch = True
                key.switches.clear()
                key.switches.append((key.x - (key.width / 4), key.y))
                key.switches.append((key.x + (key.width / 4), key.y))
                keys += 1
            elif key.height >= keyboardObject.supportKeySize:
                key.support = SupportDirection.VERTICAL
                key.supports.clear()
                key.supports.append((key.x, key.y - keyboardObject.supportSizes[key.height]))
                key.supports.append((key.x, key.y + keyboardObject.supportSizes[key.height]))
            elif key.width >= keyboardObject.supportKeySize:
                key.support = SupportDirection.HORIZONTAL
                key.supports.clear()
                key.supports.append((key.x - keyboardObject.supportSizes[key.width], key.y))
                key.supports.append((key.x + keyboardObject.supportSizes[key.width], key.y))
            else:
                key.isMultiSwitch = False
                key.support = SupportDirection.NONE
                None
