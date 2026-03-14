import pytest # Pythonda kulalnılan bir test fonks.
from examples.sample import factorial #sample.pyden factorial fonskiyonunu çekelim
import math

#Bu normal durumlar için
def test_normal_case_fact(): #pytest bunun test fonk. oldugun anlaması için test_ ile başlamalı.
    assert factorial(3) == 6
    assert factorial(4) == 24
    assert factorial(5) == 120
    assert factorial(6) == 720

#Bu sınır durumlar için 0,1
def test_edge_case_fact():
    assert factorial(0) == 1
    assert factorial(1) == 1

#Negatif sayıları kabul etmeme durumu var
def test_negative_fact():
    with pytest.raises(ValueError):
        factorial(-1)
    with pytest.raises(ValueError):
        factorial(-2)
    with pytest.raises(ValueError):
        factorial(-5)
    with pytest.raises(ValueError):
        factorial(-10)

#Sayı çok büyük olabilir. Bu yüzden büyük sayı yazmak yerine fonksiyondan yazdırabilriim.
def test_large_fact():
    assert factorial(10) == math.factorial(10)
    assert factorial(20) == math.factorial(20)

#Tip uyuşmazlıgı olabilir
def test_typing_fact():
    with pytest.raises(TypeError):
        factorial("5") #string
    with pytest.raises(TypeError):
        factorial(None) #none
    with pytest.raises(ValueError): #Burada 3.5 yazınca ValueError'a atıyor ama aynı zamanda TypeError ?
        factorial(3.5) #float
    with pytest.raises(TypeError):
        factorial([5]) #liste       