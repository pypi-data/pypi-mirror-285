from enum import Enum as _Enum
from .iunit import IUnit as _IUnit
from decimal import Decimal


class ByteEnum(_Enum):
    '''relative to bytes'''
    Bit = 0.125 # 1/8 of a byte
    Byte = 1
    KiloByte = 1000
    MegaByte = KiloByte * 1000
    GigaByte = MegaByte * 1000
    TeraByte = GigaByte * 1000
    PetaByte = TeraByte * 1000
    ExaByte  = PetaByte * 1000


class ByteUnit(_IUnit[ByteEnum, 'ByteUnit']):
    _TypeEnum = ByteEnum
    def Partition(self, minUnit:ByteEnum=None, maxUnit:ByteEnum=None) -> dict[ByteEnum, float]:
        """Splits the current amount of relative bytes to individual parts

        :param minUnit: The smallest part that should be included in the resulting dict. \
            if there are smaller parts available than minUnit, they will be added as decimals to minUnit 
        :param maxUnit:  The highest part that should be included in the resulting dict. \
            If there are bigger parts available than maxUnit, they will be added as the maxUnit unit instead.
            This implies that when maxUnit is specified to say MegaByte, in the case \
            that there is 1 complete GigaByte, it will instead be added to MegaBytes as 1000
        :return: dictionary of all used enums as keys, and their corresponding amount as values

        Example Usage:

        >>> ByteUnit(1.5, ByteEnum.MegaByte).Partition()
        {
            ByteEnum.Bit: 0.0,
            ByteEnum.Byte: 0.0,
            ByteEnum.KiloByte: 500.0,
            ByteEnum.MegaByte: 1.0,
            ByteEnum.GigaByte: 0.0,
            ByteEnum.TeraByte: 0.0,
            ByteEnum.PetaByte: 0.0,
            ByteEnum.ExaByte: 0.0,
        }
        >>> ByteUnit(1.5, ByteEnum.MegaByte).Partition(maxUnit=ByteEnum.KiloByte)
        {
            ByteEnum.Bit: 0.0,
            ByteEnum.Byte: 0.0,
            ByteEnum.KiloByte: 1500.0,
        }

        >>> ByteUnit(1002.1, ByteEnum.MegaByte).Partition(minUnit=ByteEnum.MegaByte, maxUnit=ByteEnum.GigaByte)
        {
            ByteEnum.MegaByte: 2.1,
            ByteEnum.GigaByte: 1.0,
        }

        """

        #we will use decimals to mitigate floating imperfections when using modulo/division operations
        #this is because small float imperfections can get amplified when dividing/modulo multiple times and
        #can therefore produce incorrect partition results affecting smaller units

        parts = {}
        remaining = Decimal(str(self.amount)) * Decimal(str(self.unit.value))

        # sort by size and reverse it to get biggest parts to smallest
        reversed_enum = sorted(ByteEnum, key=lambda x: x.value, reverse=True)
        for enumUnit in reversed_enum:
            if maxUnit and (enumUnit.value > maxUnit.value):
                continue

            preciseEnumUnitValue = Decimal(str(enumUnit.value))
            if enumUnit.value <= remaining:
                part = remaining // preciseEnumUnitValue
                parts[enumUnit] = float(part)
                remaining %= preciseEnumUnitValue
            else:
                parts[enumUnit] = 0.0
            
            if minUnit and (minUnit == enumUnit):
                break
        
        #gather the leftovers to the smallest part if any
        if(remaining > 0):
            #use last ByteUnit in loop since that will be the smallest part
            parts[enumUnit] = parts[enumUnit] + float(remaining / enumUnit.value)
        return parts
    
