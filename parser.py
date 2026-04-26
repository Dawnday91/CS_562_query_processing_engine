from helper import parseAggregate, positiveIntCheck, getFuncAgg

'''Format to keep in mind
SELECT ATTRIBUTE(S):
cust, 1_sum_quant, 2_sum_quant, 3_sum_quant
NUMBER OF GROUPING VARIABLES(n):
3
GROUPING ATTRIBUTES(V):
cust
F-VECT([F]):
1_sum_quant, 1_avg_quant, 2_sum_quant, 3_sum_quant, 3_avg_quant
SELECT CONDITION-VECT([σ]):
1.state=’NY’
2.state=’NJ’
3.state=’CT’
HAVING_CONDITION(G):
1_sum_quant > 2 * 2_sum_quant or 1_avg_quant > 3_avg_quant'''

Keywords = {
        "SELECT ATTRIBUTE(S)":"select",
        "NUMBER OF GROUPING VARIABLES(n)":"n",
        "GROUPING ATTRIBUTES(V)":"groupingAttribute",
        "F-VECT([F])":"f_vect",
        "SELECT CONDITION-VECT([σ])":"selectConditions",
        "HAVING_CONDITION(G)":"having",
    }

def parseInput(item):
    queryLine = {}
    lines = [line.strip() for line in item.splitlines() if line.strip()]
    
    i=0
    while i <len(lines):
        line = lines[i]
        if line in Keywords:
            key = Keywords[line]
            i+=1
            values = []
            while i < len(lines) and lines[i] not in Keywords:
                values.append(lines[i])
                i+=1
            if key in ['select','groupingAttribute','f_vect']:
                queryLine[key]= [
                    item.strip() for v in values for item in v.split(",") if item.strip()
                ]
            elif key == "n":
                queryLine[key] = values[0] if values else None
            else: 
                queryLine[key] = values
        else:
            i+=1
    return queryLine
    
    
def syntaxCheckerNorm(item):
    reqBase = {'select'}
    reqGv = {"n", "groupingAttribute", "f_vect", "selectConditions", "having"}
    
    missing = [key for key in reqBase if not item.get(key)]
    if missing:
        raise KeyError(f"Missing required sections(s): {missing}")
    
    gv = bool(item.get("groupingAttribute"))

    if not gv:
        return True

    missingGv = [key for key in reqGv if not item.get(key)]
    if missingGv:
        raise KeyError(f"Missing GV section(s): {missingGv}")
    
    syntaxCheckerGv(item)
    
    return True;

def syntaxCheckerGv(item):
    n = positiveIntCheck(item['n'],'n')
    gv = item['groupingAttribute']
    
    if n != len(gv):
        raise ValueError("number of provided grouping variables does not match upto n")
    
    for value in item['select']:
        if not parseAggregate(value) and value not in gv:
            raise ValueError(f"{value} is in SELECT but not in grouping attribute section")

def write_output(tokenDict):
    output = ""
    syntaxCheckerNorm(tokenDict)
    """with token from parse item and syntax checker being ran handle the token output"""
    
    return output