import helper
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

def parse_input(input):
    queryLine = {}
    lines = [line.strip() for line in input.splitlines() if line.strip()]
    
    i=0
    while i <len(lines):
        line = lines[i]
        if line in ["select","groupingAttribute","f_vect"]:
            key = Keywords[line]
            i+=1
            values = []
            while i < len(lines) and lines[i] not in Keywords:
                values.append(lines[i])
                i+=1
            if key in Keywords:
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
    
    
def syntax_checker(input):
    
    # check if keys are missing
    if "select" not in input:
        raise KeyError("Missing Select Clause")
    
    
    # check if numbers declared does not match up to whats provided
    n = int (input.get("n",0))
    attr = input.get("groupingAttribute","")
    attrList = [a.strip() for a in attr.split(",") if a.strip()]
    

def process_token():
    

def write_output():