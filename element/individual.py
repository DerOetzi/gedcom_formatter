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

    def __str__(self):
        return '%s: %s' % (self.__id, self.__values)