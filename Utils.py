from .KeyboardData import KeyboardObject, KeyboardKey

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
                key.switches.append((key.x - (key.width / 4), key.y))
                key.switches.append((key.x + (key.width / 4), key.y))
                keys += 1
            elif key.width >= keyboardObject.supportKeySize:
                key.isSupported = True
                # TODO add supports here
                # key.supports.append()
            else:
                None
