import subprocess
#old test input you gave me. 
#  from is implied to the expression and so we assume it's always sales. it should be removed
#  where is supposed to be combined over every such that clause because it's implicit to every grouping attribute
#  each of the fields are in a very annoying form. I did a minor rewrite of them because it will be easier to translate in the parser than to decode here.
#input = {
#   'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'], 
#   'from': ['sales'], 
#   'where': ["year = 2023 and region = 'east'"],
#   'n': '3', 'groupingAttribute': ['cust', 'prod'], 
#   'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'], 
#   'suchThat': ["1.state='CT'", "2.state='NY'", "3.state='NJ'"], 
#   'having': ['2_sum_quant > 100 or 1_avg_price < 50 and 3_min_quant >= 5']}
"""
the most important change is that what you set suchThat and having to is correct injectable code. 
    no matter what, add the "row[blah]" stuff to every feature for suchThat
      and
    value._ to every f_vect in having

"""
#ideal input below
#input = {
#    'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'],  
#    'n': '3', 
#   'groupingAttribute': ['cust', 'prod'], 
#  'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'], 
# 'suchThat': ["row['year'] == 2023 and row['region'] == 'east' and row['state'] == 'CT'",
#            "row['year'] == 2023 and row['region'] == 'east' and row['state'] == 'NY'",
#           "row['year'] == 2023 and row['region'] == 'east' and row['state'] == 'NJ'"], 
#    'having': 'value._2_sum_quant > 100 or value._1_avg_price < 50 and value._3_min_quant >= 5'}
#note that this will not run because the where clause is incompatible with the sales schema, this is just example

#actual working function that demonstrates how it should look
input = {
    'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'],  
    'n': '3', 
    'groupingAttribute': ['cust', 'prod'], 
    'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'], 
    'suchThat': ["row['day'] > 1 and row['month'] == 1 and row['state'] == 'CT'",
                "row['day'] > 1 and row['month'] == 1 and row['state'] == 'NY'",
                "row['day'] > 1 and row['month'] == 1 and row['state'] == 'NJ'"], 
    'having': 'value._2_sum_quant > 100 or value._1_avg_price < 50 and value._3_min_quant >= 5'}

#new test input to compare to previously calculated aggregates
input = {
    'select': ['cust', 'prod', '1_avg_price', '2_sum_quant', '3_min_quant'],
    'n': '3',
    'groupingAttribute': ['cust', 'prod'],
    'f_vect': ['1_avg_price', '2_sum_quant', '3_min_quant'],
    'suchThat': [
        "row['state'] == 'CT'",
        "row['quant'] > value._1_avg_price",
        "row['state'] == 'NJ'"
    ],
    'having': 'value._2_sum_quant > 0'
}

def generate(aggType, iVal, vectVal):
    output = f"""
            
    for key, value in mfTable.items():
        value.sum = 0
        value.count = 0
        value.min = float('inf')
        value.max = float('-inf')
    """
    match aggType:
        case "avg":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #avg
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.sum += row["quant"]
                    value.count += 1
                    value._{vectVal} = value.sum / value.count
                    #return
            """
        case "sum":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #sum
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.sum += row["quant"]
                    value._{vectVal} = value.sum
                    #return
            """
        case "count":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #count
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.count ++
                    value._{vectVal} = value.count
                    #return
            """

        case "max":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #max
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal][2:]}:
                    value.max = max(value.max, row["quant"])
                    value._{vectVal} = value.max
                    #return
            """
        
        case "min":
            conds = " and ".join(
                f"key.{attr} == row['{attr}']"
                for attr in input["groupingAttribute"]
            )
            output += f"""
    #min
    for row in rows:
        for key, value in mfTable.items():
            if {conds}:
                if {input["suchThat"][iVal]}:
                    value.min = min(value.min, row["quant"])
                    value._{vectVal} = value.min
                    #return
            """

    return output

    


def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """
    mfValue = "[";
    for i in range (int(input["n"])):
        mfValue += "0, "
    mfValue = mfValue[:-2] + "]";

    keyDef = f"""
    class Key:
        def __init__(self, """
    params = ", ".join(input["groupingAttribute"])
    keyDef += params + "):\n"
    for attr in input["groupingAttribute"]:
        keyDef += f"            self.{attr} = {attr}\n"
    
    keyDef += """
        def __repr__(self):
            attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
            return f"Key({attrs})"

        def __eq__(self, other):
            return isinstance(other, Key) and self.__dict__ == other.__dict__

        def __hash__(self):
            return hash(tuple(self.__dict__.values()))
    """

    rowDef = f"""
    class Row:
        def __init__(self,"""
    for agg in input["f_vect"]:
        aggType = agg.split("_", 1)[1].split("_")[0]
        match aggType:
            case "avg":
                me = "0"
            case "sum":
                me = "0"
            case "count":
                me = "0"
            case "min":
                me = "float('inf')"
            case "max":
                me = "float('-inf')"
        safe_name = "_" + agg   # prefix with underscore so it's a valid Python identifier
        rowDef += f"{safe_name}={me},"
    rowDef = rowDef[:-1] + "):\n"

    for agg in input["f_vect"]:
        safe_name = "_" + agg
        rowDef += f"            self.{safe_name} = {safe_name}\n"

    rowDef += "\n            self.sum = 0\n"
    rowDef += "            self.count = 0\n"
    rowDef += "            self.min = float('inf')\n"
    rowDef += "            self.max = float('-inf')\n"

    rowDef += """
        def __repr__(self):
            attrs = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
            return f"Row({attrs})"
"""


    body = f"""
    
    mfTable = {{}}
    groupingAttributes = {input["groupingAttribute"]}

    {keyDef}

    {rowDef}

    mfValue = {mfValue}
    #int n = {input["n"]}

    for row in rows:
        #key = tuple(generateKey(groupingAttributes, row))
        key = Key(*[row[attr] for attr in {input["groupingAttribute"]}])
        if key not in mfTable:
            mfTable[key] = Row()
            #print(key)
    #print(mfTable)


    """
    parsed = []
    for vect in input["f_vect"]:
        parts = vect.split("_", 1)   # ["1", "avg_price"]
        iVal = int(parts[0]) - 1    # grouping variable index (0-based)
        aggType = parts[1].split("_")[0]   # "avg", "sum", "min"
        #parsed.append((aggType, gv, vectVal))
        body += generate(aggType, iVal, vect)


    
    #body += generate("max", 0, "1_avg_price")
    
    #body += generate("min", 1, "2_sum_quant")

    
    body += f"""
    #having
    theOutput = []
    for key, value in mfTable.items():
        if {input["having"]}:
            theOutput.append((key, value))

    outputFR = []
    for key, value in theOutput:
        theRow = []
        for attr in {input["select"]}:
            if attr in {input["groupingAttribute"]}:
                theRow.append(getattr(key, attr))
            else:
                the = "_" + attr
                theRow.append(getattr(value, the))
        outputFR.append(theRow);
    """

    

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
#test test hello
{input["select"]}
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def generateKey(groupingAttributes, row):
    output = []
    for thing in groupingAttributes:
        output.append(row[thing])
    return output

def query():
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    rows = cur.fetchall()
    
    _global = []
    {body}
    
    return tabulate.tabulate(outputFR,
                        headers={input["select"]}, tablefmt="psql")


def main():
    print(query())
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code
    #subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()

"""
    def howIdDoIt():
    select 
        from
        where
        groupy by x, y  :  x.a, y.b
        having          


    mfTable = {}

    int numGroupByVars
    list groupByVars = ...
    
    generate groupyby table:
        for each row in realTable:
            if row not in mfTable:
                add to mfTable

    tableScannin:
        for each groupingVariable in groupByVars:
            for each row in table:
                if row satisfies WHERE clause:
                    if row satisfies SUCH THAT clause:
                        key = ...
                        if key in mfTable:
                            update mfTable
        
    output = []
    HAVING:
        for each in mfTable:
            if HAVING is satisfied:
                result.append whatever I need

    
"""
