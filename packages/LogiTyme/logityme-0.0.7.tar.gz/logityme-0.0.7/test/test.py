from terminaltables import AsciiTable
def test_terminaltables():
    inbuilt_data = [["Function Name", "Time Consumed"], ["example", "3 sec"]]
    inbuilt_table = AsciiTable(inbuilt_data)
    assert inbuilt_table
