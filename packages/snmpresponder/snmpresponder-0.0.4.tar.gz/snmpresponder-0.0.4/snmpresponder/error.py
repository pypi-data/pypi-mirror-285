#
# This file is part of snmpresponder software.
#
# Copyright (c) 2019, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/snmpresponder/license.html
#

class SnmpResponderError(Exception):
    pass


class EofError(SnmpResponderError):
    pass
