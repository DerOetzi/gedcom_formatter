import re as regex
import os

class GedcomElement:
    def __init__(self, id, event_tags):
        self._id = self._parseId(id)
        self._values = {}

        for prefix in event_tags.values():
            self._values['%s_is' % prefix] = False

    def getId(self):
        return self._id

    def _parseId(self, rawId):
        return rawId.replace('@', '').strip()

    def _parseEvent(self, prefix, child):
        self._values['%s_is' % prefix] = True
        date = self.__parseDate(child)
        if date is not None:
            self._values['%s_date' % prefix] = date

        self._values['%s_location' % prefix] = self.__parseLocation(child)
        

    def __parseDate(self, event):
        MONTH_SWITCHER = {
            'JAN': 1, 'FEB': 2, 'MAR': 3,
            'APR': 4, 'MAY': 5, 'JUN': 6,
            'JUL': 7, 'AUG': 8, 'SEP': 9,
            'OCT': 10, 'NOV': 11, 'DEC': 12
        }

        GEDCOM_DATE_REGEX = '^(0?[1-9]|[1-2][0-9]|3[0-1]) ([A-Z]{3}) ([1-9]{1}[0-9]{2,3})$'
        
        date = event.getChildByTag('DATE')
        if date is None:
            return None

        match = regex.match(GEDCOM_DATE_REGEX, date.getValue())

        if match is None:
            return None

        day, month, year = match.groups()

        month_parsed = MONTH_SWITCHER.get(month, 0)

        return (int(year), month_parsed, int(day))


    def __parseLocation(self, event):
        location = []
        place = event.getChildByTag('PLAC')
        if place is not None:
            location.append(place.getValue())

        address = event.getChildByTag('ADDR')
        if address is not None:
            location.append(address.getValue())

        return ', '.join(location)

    def _keyExists(self, key):
        return key in self._values

    def _getValueOrEmptyString(self, key):
        if self._keyExists(key):
            return self._values[key]

        return ''

    def _getDateOrNone(self, prefix):
        if self._isEvent(prefix, True):
            return self._values['%s_date' % prefix]

        return None

    def _getDateFormattedOrEmpty(self, prefix):
        date = self._getDateOrNone(prefix)
        if date is not None:
            return '%02d.%02d.%d' % (date[2], date[1], date[0])

        return ''

    def _getYearOrZero(self, prefix):
        date = self._getDateOrNone(prefix)
        if date is not None:
            return date[0]

        return 0

    def _isEvent(self, prefix, checkDateExists = False):
        if self._values['%s_is' % prefix]:
            return not checkDateExists or self._keyExists('%s_date' % prefix)

        return False

class GedcomIndividual(GedcomElement):
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
        'BURI': 'burial',
        'CONF': 'confirmation'
    }

    SKIP_TAGS = ['_UID', 'FAMC', 'CHAN']

    def __init__(self, raw):
        GedcomElement.__init__(self, raw.getPointer(), GedcomIndividual.EVENT_TAGS)

        self.__families = []

        for child in raw.getChildren():
            tag = child.getTag()
            if tag == 'NAME':
                for namepart in child.getChildren():
                    nametag = namepart.getTag()
                    if nametag in GedcomIndividual.VALUE_TAGS:
                        self._values[GedcomIndividual.VALUE_TAGS[nametag]] = namepart.getValue()
                    else:
                        raise(Exception("Unknown tag: %s %s" % (nametag, namepart.getValue())))
                        
            elif tag in GedcomIndividual.VALUE_TAGS:
                self._values[GedcomIndividual.VALUE_TAGS[tag]] = child.getValue()
            elif tag in GedcomIndividual.EVENT_TAGS:
                self._parseEvent(GedcomIndividual.EVENT_TAGS[tag], child)
            elif tag == 'FAMS':
                self.__families.append(self._parseId(child.getValue()))
            elif tag == 'OBJE':
                if 'file' in self._values:
                    continue

                file = child.getChildByTag('FILE')
                filename = file.getValue().replace('C:\\', '').replace('\\', '/')
                self._values['file'] = os.path.basename(filename)
            elif tag in GedcomIndividual.SKIP_TAGS:
                continue
            else:
                raise(Exception("Unknown tag: %s %s" % (tag, child.getValue())))

    def getFamilies(self):
        return self.__families

    def isMale(self):
        return self._getValueOrEmptyString('gender') == 'M'   

    def isFemale(self):
        return self._getValueOrEmptyString('gender') == 'F'

    def getTitle(self):
        return self._getValueOrEmptyString('nameprefix')

    def getGivenname(self):
        return self._getValueOrEmptyString('givenname')

    def getGivennames(self):
        return self._getValueOrEmptyString('givenname').split(' ')

    def getCallname(self, withTitle = False):
        callname = ''
        if self._keyExists('callname'):
            callname = self._getValueOrEmptyString('callname')
        elif self._keyExists('givenname'):
            callname = self.getGivennames()[0] 

        if withTitle and self._keyExists('nameprefix'):
            callname = self.getTitle() + ' ' + callname

        return callname
        
    def getSurname(self):
        if self._keyExists('marriagename'):
            return self._getValueOrEmptyString('marriagename')
        
        return self.getBirthname()

    def getBirthname(self):
        birthname = self._getValueOrEmptyString('birthname')
        
        if self._keyExists('beforebirthname'):
            birthname = self._getValueOrEmptyString('beforebirthname') + ' ' + birthname

        return birthname.strip()

    def isBirthdate(self):
        return self._isEvent('birth', True)

    def getBirthyear(self):
        return self._getYearOrZero('birth')

    def getBirthdate(self):
        return self._getDateOrNone('birth')

    def getBirthdateFormatted(self):
        return self._getDateFormattedOrEmpty('birth')

    def isDeathdate(self):
        return self._isEvent('death', True)

    def isDead(self):
        return self._isEvent('death')

    def getDeathyear(self):
        return self._getYearOrZero('death')

    def getDeathdate(self):
        return self._getDateOrNone('death')

    def getDeathdateFormatted(self):
        return self._getDateFormattedOrEmpty('death')

    def isFile(self):
        return self._keyExists('file')

    def getFile(self):
        return self._getValueOrEmptyString('file')

    def __str__(self):
        return '%s: %s' % (self._id, self._values)

class GedcomFamily(GedcomElement):
    TAG = 'FAM'

    EVENT_TAGS = {
        'MARR': 'marriage',
        'DIV': 'divorce'
    }

    SKIP_TAGS = {'_MARR'}

    def __init__(self, raw):
        GedcomElement.__init__(self, raw.getPointer(), GedcomFamily.EVENT_TAGS)

        self.__couple = []

        self.__children = []

        for child in raw.getChildren():
            tag = child.getTag()
            value = self._parseId(child.getValue())
            if tag == 'WIFE':
                self.__couple.append(value)
            elif tag == 'HUSB':
                self.__couple.insert(0, value)
            elif tag == 'CHIL':
                self.__children.append(value)
            elif tag in GedcomFamily.EVENT_TAGS:
                self._parseEvent(GedcomFamily.EVENT_TAGS[tag], child)
            elif tag == '_STAT' and value == 'NOT MARRIED':
                self._values['marriage_is'] = False
            elif tag in GedcomFamily.SKIP_TAGS:
                continue
            else:
                raise(Exception("Unknown tag: %s %s" % (tag, child.getValue())))

    def getCouple(self):
        return self.__couple

    def isCouple(self, individual):
        return individual in self.__couple

    def getChildren(self):       
        return self.__children

    def isMarriagedate(self):
        return self._isEvent('marriage', True)

    def isMarried(self):
        return self._isEvent('marriage')

    def getMarriageyear(self):
        return self._getYearOrZero('marriage')
    
    def getMarriagedate(self):
        return self._getDateOrNone('marriage')

    def getMarriagedateFormatted(self):
        return self._getDateFormattedOrEmpty('marriage')

    def isDivorcedate(self):
        return self._isEvent('divorce', True)

    def isDivorced(self):
        return self._isEvent('divorce')

    def getDivorceyear(self):
        return self._getYearOrZero('divorce')

    def getDivorcedate(self):
        return self._getDateOrNone('divorce')

    def getDivorcedateFormatted(self):
        return self._getDateFormattedOrEmpty('divorce')

    def __str__(self):
        return '%s: %s %s %s' % (self._id, self.__couple, self.__children, self._values)

class GedcomLine():
    LINE_REGEX = '^(0|[1-9]+[0-9]*) (@[A-Z0-9]+@ |)([A-Za-z0-9_]+)(.*|)$' 

    def __init__(self, level, pointer, tag, value):
        self.__children = []
        self.__parent = None

        self.__level = level
        self.__pointer = pointer
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
        matches = regex.match(GedcomLine.LINE_REGEX, line)
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
