from parser.parsers import parseId

class RawElement():
    def __init__(self, level, pointer, tag, value):
        self.__children = []
        self.__parent = None

        self.__level = level
        self.__pointer = parseId(pointer)
        self.__tag = tag
        self.__value = value.strip()

    def getLevel(self):
        return self.__level

    def getPointer(self):
        return self.__pointer

    def getTag(self):
        return self.__tag

    def getValue(self):
        return self.__value

    def getChildren(self):
        return self.__children

    def getChildByTag(self, tag):
        for child in self.__children:
            if child.getTag() == tag:
                return child

        return None

    def getParent(self):
        return self.__parent

    def addChild(self, element):
        self.__children.append(element)
        element.setParent(self)

        return element

    def setParent(self, element):
        self.__parent = element