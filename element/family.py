from math import ceil
from parser.parsers import parseId, parseDate, parseLocation

class Family():
    TAG = 'FAM'

    EVENT_TAGS = {
        'MARR': 'marriage',
        'DIV': 'divorce'
    }

    SKIP_TAGS = {'_MARR'}

    def __init__(self, raw):
        self.__id = raw.getPointer()

        self.__couple = []

        self.__children = []

        self.__values = {'married': True}

        for child in raw.getChildren():
            tag = child.getTag()
            value = parseId(child.getValue())
            if tag == 'WIFE':
                self.__couple.append(value)
            elif tag == 'HUSB':
                self.__couple.insert(0, value)
            elif tag == 'CHIL':
                self.__children.append(value)
            elif tag in Family.EVENT_TAGS:
                prefix = Family.EVENT_TAGS[tag] + '_'
                self.__values[prefix + 'date'] = parseDate(child)
                self.__values[prefix + 'location'] = parseLocation(child)
            elif tag == '_STAT' and value == 'NOT MARRIED':
                self.__values['married'] = False
            elif tag in Family.SKIP_TAGS:
                continue
            else:
                raise(Exception("Unknown tag: %s %s" % (tag, child.getValue())))

    def getId(self):
        return self.__id

    def getCouple(self):
        return self.__couple

    def getChildren(self):       
        return self.__children

    def render(self, families, individuals):
        print('    {} [shape = circle, label = "", height = 0.01, width = 0.0];'.format(self.__id))
        print('    {rank = same; %s -> %s -> %s;};' % (self.__couple[0], self.__id, self.__couple[1]))
        individuals[self.__couple[0]].setRender()
        individuals[self.__couple[1]].setRender()

        childCount = len(self.__children)

        if childCount > 0:
            for individual in [individuals[i] for i in self.__children if i in individuals]:
                individual.setChild()

            childNodes = list(map(lambda x: x + 'Child', self.__children))
            if childCount % 2 == 0:
                childNode = '{}Childs'.format(self.__id)
                childNodes.insert((childCount / 2), childNode)
            else:
                childNode = childNodes[ceil(childCount / 2) - 1]

            print('    {rank = same; %s;};' % (' -> '.join(childNodes)))
            print('    {rank = same; %s;};' % ('; '.join(self.__children)))
            print('    {} -> {}'.format(self.__id, childNode))


    def __str__(self):
        return '%s: %s %s %s' % (self.__id, self.__couple, self.__children, self.__values)
        