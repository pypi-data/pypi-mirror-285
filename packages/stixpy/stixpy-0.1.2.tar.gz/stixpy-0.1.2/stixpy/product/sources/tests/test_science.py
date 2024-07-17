import numpy as np
import pytest

from stixpy.product import Product


# @pytest.mark.parametrize('item', [0, (0,0), (0,0), ([0]*3), ([0]*4)])
def test_sciencedata_getitem():
    l1 = Product(
        "https://pub099.cs.technik.fhnw.ch/fits/L1/2020/05/05/SCI/solo_L1_stix-sci-xray-cpd_20200505T235959-20200506T000019_V02_0087031809-50883.fits"
    )
    a = l1[0]
    b = l1[0, 0]
    c = l1[0, 0, 0]
    d = l1[1:3, 0, 0, 0]
    e = l1[1:3, 0, 0, [1, 2, 3]]
    assert True


def test_sciencedata_props():
    l1 = Product(
        "https://pub099.cs.technik.fhnw.ch/fits/L1/2020/05/05/SCI/solo_L1_stix-sci-xray-cpd_20200505T235959-20200506T000019_V02_0087031809-50883.fits"
    )
    lt = l1.livetime
    area = l1.area
    assert True
