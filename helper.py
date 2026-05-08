import re
from dataclasses import dataclass
VALID_AGG = {"sum", "avg", "count", "min", "max"}
ALIAS = {1:"x",2:"y",3:"z",4:"a",5:"b"}

@dataclass
class AggregateToken:
    gv: int
    func: str
    attr: str
    sqlVer: str
    
def positiveIntCheck(value, field_name):
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"{field_name} must be an integer")

    if number <= 0:
        raise ValueError(f"{field_name} must be greater than 0")

    return number


def parseAggregate(item):
    parts = item.split("_")
    
    if len(parts) != 3 or not parts[0].isdigit():
        return None
    
    gv = int(parts[0])
    func = parts[1]
    attr = "_".join(parts[2:])
    
    if func not in VALID_AGG:
        raise ValueError(f"Invalid aggregate function: {func}")
    
    if gv not in ALIAS:
        raise ValueError(f"No defined letter for gv: {gv}")
    
    sqlVer = f"{func}({ALIAS[gv]}.{attr})" 
    
    return AggregateToken(gv, func, attr,sqlVer)

def normalizeItems(item):
    token = parseAggregate(item)
    return token.sqlVer if token else item

def suchthatStruct(item):
    return re.sub(r"^(\d+)\.([a-zA-Z_]\w*)",r'row["\2"]',item)
    
def havingStruct(item):
    return re.sub(r"^\d+_[a-zA-Z_]\w*",r'value._\1*$',item)