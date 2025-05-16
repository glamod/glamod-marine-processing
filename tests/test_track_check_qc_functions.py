from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from glamod_marine_processing.qc_suite.modules.next_level_track_check_qc import (  # backward_discrepancy,; calc_alternate_speeds,; forward_discrepancy,
    calculate_speed_course_distance_time_difference,
    find_multiple_rounded_values,
    find_repeated_values,
    find_saturated_runs,
    iquam_track_check,
    km_to_nm,
    row_difference,
    spike_check,
    track_check,
)


def generic_frame(in_pt):
    pt = [in_pt for _ in range(30)]
    lat = [-5.0 + i * 0.1 for i in range(30)]
    lon = [0 for _ in range(30)]
    sst = [22 for _ in range(30)]
    sst[15] = 33

    vsi = [11.11951 * km_to_nm for _ in range(30)]
    dsi = [0 for _ in range(30)]
    dck = [193 for _ in range(30)]

    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(pt))

    df = pd.DataFrame(
        {
            "sst": sst,
            "date": date,
            "lat": lat,
            "lon": lon,
            "pt": pt,
            "vsi": vsi,
            "dsi": dsi,
            "dck": dck,
        }
    )

    id = ["GOODTHING" for _ in range(30)]

    df["id"] = id

    return df


@pytest.fixture
def ship_frame():
    return generic_frame(1)


@pytest.fixture
def buoy_frame():
    return generic_frame(6)


def test_spike_check(ship_frame, buoy_frame):
    for frame in [ship_frame, buoy_frame]:
        result = spike_check(frame)
        for i in range(30):
            row = result.iloc[i]
            if i == 15:
                assert row.spike == 1
            else:
                assert row.spike == 0


@pytest.mark.parametrize("key", ["sst", "lat", "lon", "pt", "date"])
def test_spike_check_raises(ship_frame, key):
    ship_frame.drop(labels=[key], axis=1, inplace=True)
    with pytest.raises(KeyError):
        spike_check(ship_frame)


def test_row_difference(ship_frame):
    earlier = ship_frame.iloc[0]
    later = ship_frame.iloc[1]

    speed, distance, course, timediff = row_difference(later, earlier)

    assert pytest.approx(speed, 0.00001) == 11.119508064776555
    assert pytest.approx(distance, 0.00001) == 11.119508064776555
    assert course == 0.0
    assert pytest.approx(timediff, 0.0000001) == 1.0


def test_track_check(ship_frame):
    result = track_check(ship_frame)
    for i in range(len(result)):
        assert result.iloc[i].trk == 0

    lon = ship_frame.lon.array
    lon[15] = 30.0
    ship_frame["lon"] = lon
    result = track_check(ship_frame)
    for i in range(len(result)):
        if i == 15:
            assert result.iloc[i].trk == 1
        else:
            assert result.iloc[i].trk == 0


@pytest.mark.parametrize("key", ["lat", "lon", "pt", "date"])
def test_track_check_raises(ship_frame, key):
    ship_frame.drop(labels=[key], axis=1, inplace=True)
    with pytest.raises(KeyError):
        _ = track_check(ship_frame)


def test_calculate_speed_course_distance_time_difference(ship_frame):
    result = calculate_speed_course_distance_time_difference(ship_frame)
    numobs = len(result)
    for i in range(numobs):
        row = result.iloc[i]
        if i > 0:
            assert pytest.approx(row.speed, 0.00001) == 11.119508064776555
            assert pytest.approx(row.distance, 0.00001) == 11.119508064776555
            assert (
                pytest.approx(row.course, 0.00001) == 0
                or pytest.approx(row.course, 0.00001) == 360.0
            )
            assert pytest.approx(row.time_diff, 0.0000001) == 1.0
        else:
            assert np.isnan(row.speed)


@pytest.fixture
def long_frame():
    lat = [-5.0 + i * 0.1 for i in range(30)]
    lon = [0 for _ in range(30)]
    at = [15.0 for i in range(30)]
    dpt = [15.0 for i in range(30)]
    id = ["GOODTHING" for _ in range(30)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame(
        {"date": date, "lat": lat, "lon": lon, "at": at, "dpt": dpt, "id": id}
    )
    return df


@pytest.fixture
def longer_frame():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [15.0 for i in range(50)]
    dpt = [15.0 for i in range(50)]
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame(
        {"date": date, "lat": lat, "lon": lon, "at": at, "dpt": dpt, "id": id}
    )
    return df


@pytest.fixture
def longer_frame_last_passes():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [15.0 for i in range(50)]
    dpt = [15.0 for i in range(50)]
    dpt[49] = 10.0
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame(
        {"date": date, "lat": lat, "lon": lon, "at": at, "dpt": dpt, "id": id}
    )
    return df


@pytest.fixture
def longer_frame_broken_run():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [15.0 for i in range(50)]
    dpt = [15.0 for i in range(50)]
    dpt[25] = 10.0
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame(
        {"date": date, "lat": lat, "lon": lon, "at": at, "dpt": dpt, "id": id}
    )
    return df


@pytest.fixture
def longer_frame_early_broken_run():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [15.0 for i in range(50)]
    dpt = [15.0 for i in range(50)]
    dpt[3] = 10.0
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame(
        {"date": date, "lat": lat, "lon": lon, "at": at, "dpt": dpt, "id": id}
    )
    return df


def test_find_saturated_runs(
    long_frame,
    longer_frame,
    longer_frame_last_passes,
    longer_frame_broken_run,
    longer_frame_early_broken_run,
):
    result = find_saturated_runs(long_frame)
    assert "repsat" in result
    for i in range(len(result)):
        assert result.iloc[i].repsat == 0

    result = find_saturated_runs(longer_frame)
    assert "repsat" in result
    for i in range(len(result)):
        assert result.iloc[i].repsat == 1

    result = find_saturated_runs(longer_frame_last_passes)
    assert "repsat" in result
    for i in range(len(result) - 1):
        assert result.iloc[i].repsat == 1
    assert result.iloc[49].repsat == 0

    result = find_saturated_runs(longer_frame_broken_run)
    assert "repsat" in result
    for i in range(len(result)):
        assert result.iloc[i].repsat == 0

    result = find_saturated_runs(longer_frame_early_broken_run)
    assert "repsat" in result
    for i in range(len(result)):
        assert result.iloc[i].repsat == 0


@pytest.fixture
def unrounded_data():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [15.0 + (i * 0.2) for i in range(50)]
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame({"date": date, "lat": lat, "lon": lon, "at": at, "id": id})
    return df


@pytest.fixture
def rounded_data():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [round(15.0 + (i * 0.2)) for i in range(50)]
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame({"date": date, "lat": lat, "lon": lon, "at": at, "id": id})
    return df


def test_find_multiple_rounded_values(rounded_data, unrounded_data):
    result = find_multiple_rounded_values(unrounded_data, "at")
    for i in range(len(result)):
        assert result.iloc[i].rounded == 0

    result = find_multiple_rounded_values(rounded_data, "at")
    for i in range(len(result)):
        assert result.iloc[i].rounded == 1


@pytest.fixture
def repeated_data():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [22.3 for i in range(50)]
    at[49] = 22.5
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame({"date": date, "lat": lat, "lon": lon, "at": at, "id": id})
    return df


@pytest.fixture
def almost_repeated_data():
    lat = [-5.0 + i * 0.1 for i in range(50)]
    lon = [0 for _ in range(50)]
    at = [22.3 for i in range(20)]
    for i in range(20, 50):
        at.append(22.5 + (i - 20) * 0.3)
    id = ["GOODTHING" for _ in range(50)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(lat))
    df = pd.DataFrame({"date": date, "lat": lat, "lon": lon, "at": at, "id": id})
    return df


def test_find_repeated_values(repeated_data, almost_repeated_data):
    result = find_repeated_values(repeated_data, "at")
    for i in range(len(result) - 1):
        assert result.iloc[i].rep == 1
    assert result.iloc[49].rep == 0

    result = find_repeated_values(almost_repeated_data, "at")
    for i in range(len(result)):
        assert result.iloc[i].rep == 0


def iquam_frame(in_pt):
    pt = [in_pt for _ in range(30)]
    lat = [-5.0 + i * 0.1 for i in range(30)]
    lon = [0 for _ in range(30)]
    id = ["GOODTHING" for _ in range(30)]
    date = pd.date_range(start="1850-01-01", freq="1h", periods=len(pt))

    df = pd.DataFrame(
        {
            "date": date,
            "lat": lat,
            "lon": lon,
            "pt": pt,
            "id": id,
        }
    )

    return df


@pytest.fixture
def iquam_drifter():
    return iquam_frame(6)


@pytest.fixture
def iquam_ship():
    return iquam_frame(1)


def test_iquam_track_check(iquam_drifter, iquam_ship):
    result = iquam_track_check(iquam_drifter)
    for i in range(len(result)):
        assert result.iloc[i].iquam_track == 0

    result = iquam_track_check(iquam_ship)
    for i in range(len(result)):
        assert result.iloc[i].iquam_track == 0

    lon = iquam_drifter.lon.array
    lon[15] = 30.0
    iquam_drifter["lon"] = lon
    result = iquam_track_check(iquam_drifter)
    for i in range(len(result)):
        if i == 15:
            assert result.iloc[i].iquam_track == 1
        else:
            assert result.iloc[i].iquam_track == 0

    id = ["SHIP     " for _ in range(30)]
    iquam_ship["id"] = id
    result = iquam_track_check(iquam_ship)
    for i in range(len(result)):
        assert result.iloc[i].iquam_track == 0
