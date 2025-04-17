import re

def validate_date(date_str):
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    return re.match(pattern, date_str) is not None

def validate_inn(inn):
    if not inn:
        return True
    pattern = r'^\d{11}$'
    return re.match(pattern, inn) is not None

def validate_phone(phone):
    if not phone:
        return True
    pattern = r'^(\+7|8)[\d]{10}$'
    return re.match(pattern, phone) is not None