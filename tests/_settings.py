from __future__ import annotations


def get_settings(dataset):
    if dataset == "C-RAID_1.2":
        import _settings_CRAID12

        return _settings_CRAID12
    if dataset == "ICOADS_R3.0.2T":
        import _settings_ICOADS302

        return _settings_ICOADS302
    if dataset == "ICOADS_R3.0.0T":
        import _settings_ICOADS300

        return _settings_ICOADS300
