class Family():
    TAG = 'FAM'

    def __init__(self, raw, individuals):
        self.__id = raw.getPointer()

        self.__couple = []

        

    def getId(self):
        return self.__id

    def __str__(self):
        return '%s: %s' % (self.__id, self.__couple)
        