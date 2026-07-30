from datetime import datetime
# Clean dates format
Months = {
    'ene': '01',
    'feb': '02',
    'mar': '03',
    'abr': '04',
    'may': '05',
    'jun': '06',
    'jul': '07',
    'ago': '08',
    'sep': '09',
    'oct': '10',
    'nov': '11',
    'dic': '12'
}

def clean_global_date(date_str):
    # validate if there's a date:
    if not date_str:
        return None
    
    try:
        p = str(date_str).strip().split('-')

        # get the actual year
        current_year = datetime.now().year

        if len(p) == 3: return f"{p[2]}-{Months.get(p[1].lower(),'00')}-{p[0]}"
        if len(p) == 2: return f"{current_year}-{Months.get(p[1].lower(),'00')}-{p[0]}"

        return None
    
    except Exception as e:
        print(f"Error with date: '{date_str}': {e}")

        return None