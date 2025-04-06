from datetime import date
import xlsxwriter


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


def make_xlsx_file(expenses: list)-> None:
    """
    Make file ./Expenses.xlsx
    
    And fill it info from expenses: list
    """
    workbook = xlsxwriter.Workbook("Expenses.xlsx")
    worksheet= workbook.add_worksheet("Expenses")
    worksheet.write(0,0,"Дата")
    worksheet.write(0,1,"Ід")
    worksheet.write(0,2,"Назва")
    worksheet.write(0,3,"Сума грн")
    worksheet.write(0,4,"Сума дол")

    row = 0

    for index, item in enumerate(expenses):
        row += 1
        worksheet.write(row, 0, item["date"])
        worksheet.write(row, 1, item["id"])
        worksheet.write(row, 2, item["description"])
        worksheet.write(row, 3, item["uah_amount"])
        worksheet.write(row, 4, item["usd_amount"])

    worksheet.write(row+1, 2, "Всього:")
    worksheet.write(row+1, 3, f"=SUM(D2:D{row+1})")
    worksheet.write(row+1, 4, f"=SUM(E2:E{row+1})")
    workbook.close()