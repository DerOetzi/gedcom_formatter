from parser.parsers import parseDate, parseLocation

class Individual():
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

    SKIP_TAGS = ['_UID', 'FAMS', 'FAMC', 'CHAN', 'OBJE']

    def __init__(self, raw):
        self.__id = raw.getPointer()

        self.__render = False
        self.__child = False

        self.__values = {}

        for child in raw.getChildren():
            tag = child.getTag()
            if tag == 'NAME':
                for namepart in child.getChildren():
                    nametag = namepart.getTag()
                    if nametag in Individual.VALUE_TAGS:
                        self.__values[Individual.VALUE_TAGS[nametag]] = namepart.getValue()
                    else:
                        raise(Exception("Unknown tag: %s %s" % (nametag, namepart.getValue())))
                        
            elif tag in Individual.VALUE_TAGS:
                self.__values[Individual.VALUE_TAGS[tag]] = child.getValue()
            elif tag in Individual.EVENT_TAGS:
                prefix = Individual.EVENT_TAGS[tag] + '_'
                self.__values[prefix + 'date'] = parseDate(child)
                self.__values[prefix + 'location'] = parseLocation(child)
            elif tag in Individual.SKIP_TAGS:
                continue
            else:
                raise(Exception("Unknown tag: %s %s" % (tag, child.getValue())))

    def getId(self):
        return self.__id

    def setRender(self, render = True):
        self.__render = render

    def setChild(self):
        self.setRender()
        self.__child = True

    def render(self):
        if self.__render:
            label = '{}\\n{}\\n{}'.format(self.getCallname(), self.getBirthname(), self.getBirthdate())
            print('    {} [shape = doubleoctagon label="{}"];'.format(self.__id, label))

            if self.__child:
                print('    {}Child [shape = circle, label="", height = 0.01, width = 0.0];'.format(self.__id))
                print('    {}Child -> {};'.format(self.__id, self.__id))

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

    def getBirthdate(self):
        if 'birth_date' in self.__values and self.__values['birth_date'] is not None:
            date = self.__values['birth_date']
            return '{:02d}.{:02d}.{}'.format(date[2], date[1], date[0])

        return ''

    def __str__(self):
        return '%s: %s' % (self.__id, self.__values)