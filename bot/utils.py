from datetime import date
from prettytable import PrettyTable


def to_db_date(text_date:str) -> str:
    """
    convert date from dd.mm.yyyy into string that compatible with date format yyyy-mm-dd
    """
    date_str=text_date.split(".")
    return str(date(
        year=int(date_str[-1]),
        month=int(date_str[1]),
        day=int(date_str[0]),
    ))
    

def to_normal_date(db_date:date) -> str:
    """
    convert date from yyyy-mm-dd into dd.mm.yyyy format
    """
    text = db_date.split('-')
    return f"{text[-1]}.{text[1]}.{text[0]}"


def make_table(info: list) -> PrettyTable:
    uah_sum = 0
    usd_sum = 0
    
    table = PrettyTable()
    table.field_names = ["Дата","Ід", "Назва","Сума грн","Сума дол"]

    for item in info:
        uah_sum += item["uah_amount"]
        usd_sum += item["usd_amount"]
        
        item["date"] = to_normal_date(item["date"])
        table.add_row([item["date"], item["id"], item["description"], item["uah_amount"], item["usd_amount"]])
        
    table.add_divider()
    table.add_row(["","","", round(uah_sum,2), usd_sum])
    
    return table