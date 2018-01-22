
def utilities(internet, TV, electricity, phone, water, trash, heat, parking):
    pass

def living_expenses(salary, percent=0.35, monthly_salary=0, debt=0, utilities=0):
    if monthly_salary!=0:
        rent = percent*(monthly_salary - debt - utilities)
    else:
        rent = percent*(salary/12 - debt - utilities)
    return rent

if __name__ == '__main__':
    utilities = utilities()
    print(living_expenses(60000))
