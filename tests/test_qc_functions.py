from __future__ import annotations

import pytest

from cdm_reader_mapper import read_tables
from cdm_reader_mapper.common.getting_files import load_file

from glamod_marine_processing.qc_suite.modules.next_level_qc import is_buoy, is_ship, is_deck_780, do_position_check, do_date_check, do_time_check, do_blacklist, do_day_check, humidity_blacklist, mat_blacklist, wind_blacklist, do_base_mat_qc, do_base_dpt_qc, do_base_sst_qc, do_base_wind_qc, do_kate_mat_qc

import _load_data
from _settings import get_settings

def test_is_buoy():
    result = is_buoy(inputs)
    assert result == expected_value
    
def test_is_ship():
    result = is_ship(inputs)
    assert result == expected_value
    
def test_is_deck_780():
    result = is_deck_780(inputs)
    assert result == expected_value
    
def test_do_position_check():
    result = do_position_check(inputs)
    assert result == expected_value
    
def test_do_date_check():
    result = do_date_check(inputs)
    assert result == expected_value
    
def test_do_time_check():
    result = do_time_check(inputs)
    assert result == expected_value
    
def test_do_blacklist():
    result = do_blacklist(inputs)
    assert result == expected_value
    
def test_do_day_check():
    result = do_day_check(inputs)
    assert result == expected_value
    
def test_humidity_blacklist():
    result = humidity_blacklist(inputs)
    assert result == expected_value
    
def test_mat_blacklist():
    result = mat_blacklist(inputs)
    assert result == expected_value
    
def test_wind_blacklist():
    result = wind_blacklist(inputs)
    assert result == expected_value
    
def test_do_base_mat_qc():
    result = do_base_mat_qc(inputs)
    assert result == expected_value       
    
def test_do_base_dpt_qc():
    result = do_base_dpt_qc(inputs)
    assert result == expected_value

def test_do_base_sst_qc():
    result = do_base_sst_qc(inputs)
    assert result == expected_value
    
def test_do_base_wind_qc():
    result = do_base_mat_qc(inputs)
    assert result == expected_value
    
def test_do_kate_mat_qc():
    result = do_base_mat_qc(inputs)
    assert result == expected_value                                    