from project import stock_movement
from project import whatScanned
import pytest


def test_stock_movement():
    #stock_movement(item, process, place, amount):
    assert stock_movement("jonas","in","P1",1) == "success"
    with pytest.raises(ValueError):
        stock_movement("jonas","in","P1",-1)


def test_what():
    #whatScanned(barcode)
    # Returns True if it was a barcode, not aplace or a process
    assert whatScanned("jonas") == True
    assert whatScanned("P1") == False
    assert whatScanned("in") == False
    assert whatScanned("out") == False
    assert whatScanned("55") == False #is number of amount
    assert whatScanned("5555") == True


def test_table_create():
    #table_create(table, columns):
    # Creates table in sqlite if it not exists

    ...

if __name__ == "__main__":
    main()