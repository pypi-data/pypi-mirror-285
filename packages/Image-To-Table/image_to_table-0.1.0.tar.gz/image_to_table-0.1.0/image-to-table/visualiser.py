import json
from tabulate import tabulate

def json_to_table(file_path: str, number_char_cell: int = 18) -> None:
    
    output = []
    
    try:
        with open(file_path, "r") as file:
            json_data = file.read()
    except Exception as e:
        print(f"Error saving the content as json: {e}")
        return
        
    json_str = json.loads(json_data)
    
    first_row = ["hours"]
    first_row.extend(list(json_str.keys()))
    
    first_col = [[key] for key in json_str[first_row[1]]]
    
    output.append(first_row)
    output.extend(first_col)
    
    for i in range(1,len(output)):
        row = output[i]
        time = row[0]
        
        for key in json_str.keys():
            appoint = json_str[key][time]
            value = list(appoint.values())
            if value != []:
                row.append(value[0]['course'][:number_char_cell])
            else:
                row.append("-X-")
                
    print(tabulate(output,headers="firstrow",tablefmt="grid"))
    