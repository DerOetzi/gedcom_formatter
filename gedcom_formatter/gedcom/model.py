import re as regex
from math import ceil
from .parsers import parseId, parseDate, parseLocation

class GedcomIndividual():
    TAG = 'INDI'

    VALUE_TAGS = {
        'SURN': 'birthname',
        'GIVN': 'givenname',
        '_MARNM': 'marriagename',
        '_RUFNAME': 'callname',
        'NPFX': 'nameprefix',
        'SPFX': 'beforebirthname',
        'SEX': 'gender',
        'OCCU': 'occupation',
        'RELI': 'religion',
        'NOTE': 'note'
    }

    EVENT_TAGS = {
        'BIRT': 'birth',
        'CHR': 'baptism',
        'DEAT': 'death',
        'BURI': 'burial'
    }

    SKIP_TAGS = ['_UID', 'FAMC', 'CHAN', 'OBJE']

    def __init__(self, raw):
        self.__id = raw.getPointer()

        self.__values = {}

        self.__families = []

        for child in raw.getChildren():
            tag = child.getTag()
            if tag == 'NAME':
                for namepart in child.getChildren():
                    nametag = namepart.getTag()
                    if nametag in GedcomIndividual.VALUE_TAGS:
                        self.__values[GedcomIndividual.VALUE_TAGS[nametag]] = namepart.getValue()
                    else:
                        raise(Exception("Unknown tag: %s %s" % (nametag, namepart.getValue())))
                        
            elif tag in GedcomIndividual.VALUE_TAGS:
                self.__values[GedcomIndividual.VALUE_TAGS[tag]] = child.getValue()
            elif tag in GedcomIndividual.EVENT_TAGS:
                prefix = GedcomIndividual.EVENT_TAGS[tag] + '_'
                self.__values[prefix + 'date'] = parseDate(child)
                self.__values[prefix + 'location'] = parseLocation(child)
            elif tag == 'FAMS':
                self.__families.append(parseId(child.getValue()))
            elif tag in GedcomIndividual.SKIP_TAGS:
                continue
            else:
                raise(Exception("Unknown tag: %s %s" % (tag, child.getValue())))

    def getId(self):
        return self.__id

    def getFamilies(self):
        return self.__families

    def isMale(self):
        return 'gender' in self.__values and self.__values['gender'] == 'M'   

    def getCallname(self):
        if 'callname' in self.__values:
            callname = self.__values['callname']
        else:
            callname = self.__values['givenname'].split(' ')[0]

        if 'nameprefix' in self.__values:
            callname = self.__values['nameprefix'] + ' ' + callname

        return callname
        
    def getBirthname(self):
        birthname = ''
        
        if 'birthname' in self.__values:
            birthname = self.__values['birthname']

        if 'beforebirthname' in self.__values:
            birthname = self.__values['beforebirthname'] + ' ' + birthname

        return birthname.strip()

    def getBirthYear(self):
        if 'birth_date' in self.__values and self.__values['birth_date'] is not None:
            return self.__values['birth_date'][0]
        
        return 0

    def getBirthdate(self):
        if 'birth_date' in self.__values and self.__values['birth_date'] is not None:
            date = self.__values['birth_date']
            return '{:02d}.{:02d}.{}'.format(date[2], date[1], date[0])

        return ' '

    def __str__(self):
        return '%s: %s' % (self.__id, self.__values)

LINE_REGEX = '^(0|[1-9]+[0-9]*) (@[A-Z0-9]+@ |)([A-Za-z0-9_]+)(.*|)$' 

class GedcomFamily():
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
            elif tag in GedcomFamily.EVENT_TAGS:
                prefix = GedcomFamily.EVENT_TAGS[tag] + '_'
                self.__values[prefix + 'date'] = parseDate(child)
                self.__values[prefix + 'location'] = parseLocation(child)
            elif tag == '_STAT' and value == 'NOT MARRIED':
                self.__values['married'] = False
            elif tag in GedcomFamily.SKIP_TAGS:
                continue
            else:
                raise(Exception("Unknown tag: %s %s" % (tag, child.getValue())))

    def getId(self):
        return self.__id 

    def getCouple(self):
        return self.__couple

    def isCouple(self, individual):
        return individual in self.__couple

    def getChildren(self):       
        return self.__children

    def __str__(self):
        return '%s: %s %s %s' % (self.__id, self.__couple, self.__children, self.__values)

class GedcomLine():
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

class Gedcom():
    def __init__(self):
        self.__individuals = {}
        self.__families = {}

    def parseFile(self, filename):
        with open(filename, 'rb') as fp:
            lineNumber = 1
            rootElement = GedcomLine(-1, '', 'ROOT', '')
            lastElement = rootElement
            for line in fp:
                lastElement = self.__parseLine(lineNumber, line.decode('utf-8-sig'), lastElement)
                lineNumber += 1

        for element in rootElement.getChildren():
            if element.getTag() == GedcomIndividual.TAG:
                individual = GedcomIndividual(element)
                self.__individuals[individual.getId()] = individual
            
        for element in rootElement.getChildren():
            if element.getTag() == GedcomFamily.TAG:
                family = GedcomFamily(element)
                self.__families[family.getId()] = family
            
    def __parseLine(self, lineNumber, line, lastElement):
        matches = regex.match(LINE_REGEX, line)
        if matches is None:
            errorMessage = "Line %d: %s parse error" % (lineNumber, line)
            raise Exception(errorMessage)

        else:
            level, pointer, tag, value = matches.groups()
            level = int(level)

            if level > lastElement.getLevel() + 1:
                errorMessage = "Line %d: %d level violation" % (lineNumber, level)
                raise Exception(errorMessage)

            element = GedcomLine(level, pointer, tag, value)

            parent = lastElement

            while parent.getLevel() > level - 1:
                parent = parent.getParent()

            parent.addChild(element)

            return element

    def getIndividuals(self):
        return self.__individuals

    def getIndividual(self, id):
        return self.__individuals[id]

    def getFamilies(self):
        return self.__families.values()

    def getFamily(self, id):
        return self.__families[id]

    def __str__(self):
        return 'Individuals: %d, Families: %d' % (len(self.__individuals), len(self.__families))
