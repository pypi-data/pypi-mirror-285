# device_type
type_map = {
    "switch": {
        "1-001": "on",
        "1-002": "on",
        "1-003": "on",
        "1-005": "on",
        "1-006": "on",
        "1-004": "on",
        "107-001": "on",
    },
    "light": {
        "3-001": "dim",
        "3-002": "temp",
        "3-003": "dim_temp",
        "3-004": "rgbw",
        "3-005": "rgb",
        "3-006": "rgbcw",
    },
    "cover": {
        "4-001": "roll",
        "4-002": "roll",
        "4-003": "shutter",
        "4-004": "shutter",
    },
}

group_type_map = {
    "switch": {
        "breaker": "on",
    },
    "light": {
        "light": "dim",
        "color": "temp",
        "lightcolor": "dim_temp",
        "rgbw": "rgbw",
        "rgb": "rgb",
    },
    "cover": {
        "retractable": "roll",
        "roller": "roll",
    },
}

media_type_map = {
    "8-001-001": "hua_ersi_music",
    "8-001-002": "xiang_wang_music_s7_mini_3s",
    "8-001-003": "xiang_wang_music_s8",
    "8-001-004": "sheng_bi_ke_music",
    "8-001-005": "bo_sheng_music",
    "8-001-006": "sonos_music",
}

sensor_type_map = {
    "7-001-001": ["temperature"],
    "7-002-001": ["humidity"],
    "7-003-001": ["light"],
    "7-004-001": ["formaldehyde"],
    "7-005-001": ["pm25"],
    "7-006-001": ["carbon_dioxide"],
    "7-007-001": ["air_quality"],
    "7-008-001": ["human"],
    "7-008-002": ["human"],
    "7-008-003": ["human", "light"],
    "7-009-001": ["trigger"],
    "7-009-002": ["human"],
    "7-009-003": ["human", "light"],
    "7-009-004": ["trigger"],
    "7-009-005": ["trigger"],
    "7-009-006": ["trigger"],
    "7-009-007": ["trigger"],
    "7-009-008": ["trigger"],
    "7-009-009": ["human"],
    "7-009-010": ["human"],
    "7-010-001": ["carbon_monoxide"],
    "7-011-001": ["tvoc"],
    "7-012-001": ["temperature", "humidity", "tvoc", "pm25", "formaldehyde", "carbon_dioxide", "pm10"],
    "7-012-002": ["carbon_monoxide"],
    "7-013-001": ["light", "human"],
}
havc_type_map = {
    "5-001-001": {
        "type": "ac",
        "ac_set_temp_range": [15, 35],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet", "air"],
        "ac_lock_mode": ["lock", "half_lock", "unlock"],
        "ac_wind_speed": ["auto", "super_strong", "super_high", "high", "mid", "low", "super_low", "super_quiet"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-002": {
        "type": "ac",
        "ac_set_temp_range": [10, 30],
        "ac_mode": ["cold", "hot"],
        "ac_lock_mode": ["lock", "unlock"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-003": {
        "type": "ac",
        "ac_set_temp_range": [16, 32],
        "ac_mode": ["cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-004": {
        "type": "ac",
        "ac_set_temp_range": [15, 35],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-005": {
        "type": "ac",
        "ac_set_temp_range": [15, 45],
        "ac_mode": ["cold", "hot", "fan", "wet", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-006": {
        "type": "ac",
        "ac_set_temp_range": [5, 35],
        "ac_mode": ["cold", "hot", "fan"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-007": {
        "type": "ac",
        "ac_set_temp_range": [5, 35],
        "ac_mode": ["cold", "hot", "fan", "heat", "mix"],
        "ac_lock_mode": ["lock", "unlock"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-008": {
        "type": "ac",
        "ac_set_temp_range": [5, 35],
        "ac_mode": ["cold", "hot", "fan", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-009": {
        "type": "ac",
        "ac_set_temp_range": [10, 32],
        "ac_mode": ["cold", "hot", "fan", "wet", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-010": {
        "type": "ac",
        "ac_set_temp_range": [5, 30],
        "ac_mode": ["cold", "hot", "fan", "wet", "auto", "heat", "mix", "wet_reheat"],
        "ac_wind_speed": ["auto", "super_high", "high", "mid_high", "mid", "mid_low", "low", "super_low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-011": {
        "type": "ac",
        "ac_set_temp_range": [10, 30],
        "ac_mode": ["cold", "hot", "fan", "wet", "auto"],
        "ac_wind_speed": ["auto", "high", "mid_high", "mid", "mid_low", "low", "super_low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-012": {
        "type": "ac",
        "ac_set_temp_range": [5, 35],
        "ac_mode": ["cold", "hot", "fan", "wet", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
        "ac_set_humidity_range": [40, 75],
    },
    "5-001-013": {
        "type": "ac",
        "ac_set_temp_range": [10, 35],
        "ac_mode": ["cold", "hot", "fan", "wet", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-014": {
        "type": "ac",
        "ac_set_temp_range": [10, 35],
        "ac_mode": ["cold", "hot", "fan", "wet", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-015": {
        "type": "ac",
        "ac_set_temp_range": [16, 30],
        "ac_mode": ["cold", "hot", "fan", "wet", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-016": {
        "type": "ac",
        "ac_set_temp_range": [5, 45],
        "ac_mode": ["cold", "hot", "fan", "wet", "heat", "mix"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-017": {
        "type": "ac",
        "ac_set_temp_range": [16, 32],
        "ac_mode": ["cold", "hot", "fan", "wet", "humidify"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-018": {
        "type": "ac",
        "ac_set_temp_range": [19, 30],
        "ac_mode": ["cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-019": {
        "type": "ac",
        "ac_set_temp_range": [16, 30],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-020": {
        "type": "ac",
        "ac_set_temp_range": [16, 32],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
        "ac_set_humidity_range": [40, 80],
    },
    "5-001-021": {
        "type": "ac",
        "ac_set_temp_range": [16, 30],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-022": {
        "type": "ac",
        "ac_set_temp_range": [17, 30],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "super_high", "high", "mid_high", "mid", "mid_low", "low", "super_low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-023": {
        "type": "ac",
        "ac_set_temp_range": [17, 30],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-024": {
        "type": "ac",
        "ac_set_temp_range": [10, 32],
        "ac_mode": ["cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-025": {
        "type": "ac",
        "ac_set_temp_range": [10, 32],
        "ac_mode": ["cold", "hot", "fan"],
        "ac_wind_speed": ["auto", "super_high", "high", "mid", "low", "super_low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-026": {
        "type": "ac",
        "ac_set_temp_range": [17, 35],
        "ac_mode": ["cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["super_high", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-027": {
        "type": "ac",
        "ac_set_temp_range": [16, 32],
        "ac_mode": ["cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-028": {
        "type": "ac",
        "ac_set_temp_range": [5, 45],
        "ac_mode": ["cold", "hot", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-029": {
        "type": "ac",
        "ac_set_temp_range": [17, 30],
        "ac_mode": ["auto", "super_high", "high", "mid_high", "mid", "mid_low", "low", "super_low"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-030": {
        "type": "ac",
        "ac_set_temp_range": [17, 30],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-031": {
        "type": "ac",
        "ac_set_temp_range": [16, 30],
        "ac_mode": ["auto", "cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "super_high", "high", "mid", "low", "super_low"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-001-032": {
        "type": "ac",
        "ac_set_temp_range": [16, 30],
        "ac_mode": ["cold", "hot", "fan", "wet"],
        "ac_wind_speed": ["auto", "high", "mid", "low", "super_low", "stop"],
        "ac_temp_adjust": ["up", "down"],
    },
    "5-002-001": {
        "type": "fh",
        "fh_lock_mode": ["lock", "half_lock", "unlock"],
        "fh_set_temp_range": [10, 30],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-002": {
        "type": "fh",
        "fh_lock_mode": ["lock", "half_lock", "unlock"],
        "fh_set_temp_range": [5, 35],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-003": {
        "type": "fh",
        "fh_lock_mode": ["lock", "half_lock", "unlock"],
        "fh_set_temp_range": [5, 35],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-004": {
        "type": "fh",
        "fh_lock_mode": ["lock", "half_lock", "unlock"],
        "fh_set_temp_range": [5, 35],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-005": {
        "type": "fh",
        "fh_set_temp_range": [10, 32],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-006": {
        "type": "fh",
        "fh_set_temp_range": [16, 45],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-007": {
        "type": "fh",
        "fh_set_temp_range": [16, 45],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-008": {
        "type": "fh",
        "fh_set_temp_range": [16, 45],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-009": {
        "type": "fh",
        "fh_set_temp_range": [16, 32],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-010": {
        "type": "fh",
        "fh_set_temp_range": [0, 100],
        "fh_temp_adjust": ["up", "down"],
        "fh_real_humidity": True
    },
    "5-002-011": {
        "type": "fh",
        "fh_set_temp_range": [16, 32],
        "fh_temp_adjust": ["up", "down"],
        "fh_real_humidity": True
    },
    "5-002-012": {
        "type": "fh",
        "fh_set_temp_range": [16, 32],
        "fh_lock_mode": ["lock", "half_lock", "unlock"],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-013": {
        "type": "fh",
        "fh_set_temp_range": [10, 32],
        "fh_temp_adjust": ["up", "down"],
        "fh_real_humidity": True
    },
    "5-002-014": {
        "type": "fh",
        "fh_set_temp_range": [17, 35],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-015": {
        "type": "fh",
        "fh_set_temp_range": [5, 35],
        "fh_temp_adjust": ["up", "down"],
    },
    "5-002-016": {
        "type": "fh",
        "fh_set_temp_range": [5, 35],
        "fh_temp_adjust": ["up", "down"],
    },

    "5-003-001": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "mid", "low"],
        "fa_set_humidity_range": [20, 95],
        "fa_humidity_adjust": ["up", "down"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-002": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "mid", "low"],
        "fa_set_humidity_range": [20, 95],
        "fa_humidity_adjust": ["up", "down"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-003": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "mid", "low"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-004": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["auto", "manual", "timing"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-005": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
    },
    "5-003-006": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
        "fa_work_mode": ["heat_exchange", "common", "indoor_loop", "outdoor_loop"],
    },
    "5-003-007": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["manual", "timing"],
        "fa_real_temp": True
    },
    "5-003-008": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
    },
    "5-003-009": {
        "type": "fa",
        "fa_wind_speed": ["air", "clean", "wet"],
        "fa_set_humidity_range": [0, 100],
        "fa_work_mode": ["auto", "manual", "timing"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-010": {
        "type": "fa",
        "fa_wind_speed": ["auto", "super_strong", "super_high", "high", "mid", "low", "super_low", "stop"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-011": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "mid", "low", "super_low", "stop"],
        "fa_work_mode": ["air", "wet"],
    },
    "5-003-012": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
    },
    "5-003-013": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["indoor_loop", "fresh", "fresh_wet", "wet"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-014": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-015": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
    },
    "5-003-016": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
    },
    "5-003-017": {
        "type": "fa",
        "fa_wind_speed": ["high", "low"],
        "fa_real_temp": True
    },
    "5-003-018": {
        "type": "fa",
        "fa_wind_speed": ["high", "low"],
        "fa_work_mode": ["fresh", "wet"],
        "fa_set_humidity_range": [0, 100],
        "fa_real_humidity": True
    },
    "5-003-019": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-020": {
        "type": "fa",
        "fa_wind_speed": ["extreme_strong", "super_high", "high", "mid", "low", "super_low"],
        "fa_set_humidity_range": [40, 90],
        "fa_work_mode": ["auto", "manual", "program"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-021": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "low"],
        "fa_set_humidity_range": [30, 70],
        "fa_work_mode": ["wet", "ventilate"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-022": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
        "fa_work_mode": ["high", "mid", "low"],
        "fa_set_humidity_range": [30, 70],
    },
    "5-003-023": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-024": {
        "type": "fa",
        "fa_wind_speed": ["high", "low"],
    },
    "5-003-025": {
        "type": "fa",
        "fa_wind_speed": ["high", "low"],
        "fa_work_mode": ["exhaust", "heat_exchange", "smart", "powerful"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-026": {
        "type": "fa",
        "fa_wind_speed": ["high", "low"],
        "fa_work_mode": ["exhaust", "heat_exchange", "smart", "powerful", "cold_room", "heat_room"],
        "fa_real_temp": True
    },
    "5-003-027": {
        "type": "fa",
        "fa_wind_speed": ["super_high", "high", "mid", "low"],
        "fa_work_mode": ["auto", "timing", "exhaust", "fresh", "energy_recycle", "night", "holiday"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-028": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "mid", "low", "super_low", "stop"],
        "fa_work_mode": ["auto", "manual", "timing", "sleep"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-029": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["auto", "manual", "timing", "sleep"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-030": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_set_humidity_range": [10, 95],
        "fa_work_mode": ["indoor_loop", "fresh", "fresh_wet", "wet"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-031": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
        "fa_work_mode": ["auto", "manual", "night", "holiday"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-032": {
        "type": "fa",
        "fa_wind_speed": ["high", "low"],
        "fa_set_humidity_range": [0, 100],
        "fa_work_mode": ["fresh", "wet"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-033": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "super_low", "stop"],
        "fa_work_mode": ["auto", "manual", "timing", "sleep"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-034": {
        "type": "fa",
        "fa_set_humidity_range": [0, 100],
        "fa_work_mode": ["auto", "fresh", "clean", "wet"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-035": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
        "fa_real_temp": True
    },
    "5-003-036": {
        "type": "fa",
        "fa_wind_speed": ["super_high", "high", "mid", "low", "super_low", "stop"],
        "fa_work_mode": ["fresh", "clean", "cold_room", "sleep", "smart", "powerful"],
        "fa_real_temp": True
    },
    "5-003-037": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
        "fa_work_mode": ["night", "holiday"],
    },
    "5-003-038": {
        "type": "fa",
        "fa_set_humidity_range": [0, 100],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-039": {
        "type": "fa",
        "fa_wind_speed": ["auto", "extreme_strong", "super_high", "high", "mid", "low", "super_low", "super_quiet"],
        "fa_work_mode": ["auto", "exhaust", "heat_exchange", "indoor_loop", "fresh", "pass"],
        "fa_real_temp": True
    },
    "5-003-040": {
        "type": "fa",
        "fa_wind_speed": ["extreme_strong", "super_high", "high", "mid", "low", "super_low", "super_quiet"],
    },
    "5-003-041": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "mid", "low"],
        "fa_work_mode": ["auto", "manual", "timing"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-042": {
        "type": "fa",
        "fa_wind_speed": ["high", "low"],
    },
    "5-003-043": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
    },
    "5-003-044": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["auto", "manual", "timing"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-045": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["auto", "manual", "timing"],
        "fa_real_temp": True,
        "fa_real_humidity": True
    },
    "5-003-046": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["auto", "manual", "timing"],
    },
    "5-003-047": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["manual", "timing"],
    },
    "5-003-048": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
        "fa_work_mode": ["auto", "manual", "sleep"],
    },
    "5-003-049": {
        "type": "fa",
        "fa_wind_speed": ["auto", "super_high", "high", "mid", "low", "super_low"],
        "fa_work_mode": ["auto", "manual"],
    },
    "5-003-050": {
        "type": "fa",
        "fa_wind_speed": ["auto", "high", "mid", "low", "super_low", "stop"],
    },
    "5-003-051": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low"],
        "fa_work_mode": ["auto", "manual"],
        "fa_real_temp": True
    },
    "5-003-052": {
        "type": "fa",
        "fa_wind_speed": ["high", "mid", "low", "stop"],
        "fa_work_mode": ["auto", "manual"],
        "fa_real_temp": True
    },

    "5-004-001": {
        "type": "hp",
        "hp_set_temp_range": [5, 55],
        "hp_mode": ["cold", "hot"],
    },
    "5-004-002": {
        "type": "hp",
        "hp_set_temp_range": [7, 55],
        "hp_mode": ["cold", "hot"],
        "hp_temp_adjust": ["up", "down"],
    },
    "5-004-003": {
        "type": "hp",
    },
    "5-004-004": {
        "type": "hp",
        "hp_set_temp_range": [5, 55],
        "hp_mode": ["cold", "hot"],
        "hp_temp_adjust": ["up", "down"],
    },
    "5-004-005": {
        "type": "hp",
        "hp_set_temp_range": [7, 55],
        "hp_mode": ["cold", "hot", "hotwater", "cold_comp_hotwater", "hot_comp_hotwater"],
        "hp_hotwater_temp_adjust": ["up", "down"],
    },
    "5-004-006": {
        "type": "hp",
        "hp_set_temp_range": [5, 55],
        "hp_mode": ["cold", "hot", "cold_common_hotwater", "cold_fast_hotwater", "hot_common_hotwater",
                    "hot_fast_hotwater", "common_hotwater", "fast_hotwater", "water_pump_loop"],
        "hp_temp_adjust": ["up", "down"],
    },
    "5-004-007": {
        "type": "hp",
        "hp_set_temp_range": [12, 50],
        "hp_mode": ["cold", "hot"],
    },
    "5-004-008": {
        "type": "hp",
        "hp_set_temp_range": [12, 55],
        "hp_mode": ["cold", "hot"],
    },
    "5-004-009": {
        "type": "hp",
        "hp_set_temp_range": [5, 55],
        "hp_mode": ["cold", "hot"],
    },
    "5-004-010": {
        "type": "hp",
        "hp_hot_set_temp": [30, 70],
        "hp_mode": ["cold", "hot"],
    },
    "5-005-001": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_lock_mode": ["mode", "mode_wind", "mode_wind_temp", "unlock"],
        "tc_mode": ["cold", "hot", "wet", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid_high", "mid", "mid_low", "low", "super_low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_set_humidity_range": [40, 75],
        "tc_humidity_adjust": ["up", "down"],
        "tc_real_humidity": True,
        "tc_real_temp": True
    },
    "5-005-002": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_lock_mode": ["mode", "mode_wind", "mode_wind_temp", "child", "unlock"],
        "tc_mode": ["cold", "hot", "wet", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_set_humidity_range": [40, 75],
        "tc_humidity_adjust": ["up", "down"],
        "tc_real_humidity": True,
        "tc_real_temp": True
    },
    "5-005-003": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_lock_mode": ["unlock", "lock"],
        "tc_mode": ["cold", "hot", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-004": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_lock_mode": ["unlock", "lock"],
        "tc_mode": ["cold", "hot", "wet", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["extreme_strong", "strong", "super_high", "high", "mid_high", "mid", "mid_low", "low",
                          "super_low", "extreme_low", "stop"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-005": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "wet", "ventilate", "floorheat", "smart_floorheat"],
        "tc_wind_speed": ["auto", "high", "mid_high", "mid", "mid_low", "low", "super_low", "stop"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-006": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["auto", "cold", "hot", "wet", "ventilate", "floorheat", "smart_floorheat"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-007": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["auto", "cold", "hot", "wet", "ventilate", "floorheat", "smart_floorheat"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-008": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["auto", "cold", "hot", "wet", "ventilate", "wet_reheat", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "super_high", "high", "mid_high", "mid", "mid_low", "low", "super_low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-009": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-010": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "floorheat", "mix", "clean"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-011": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "super_high", "high", "mid", "low", "super_low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-012": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-013": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "wet", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_humidity": True,
        "tc_real_temp": True
    },
    "5-005-014": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
    "5-005-015": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "ventilate"],
    },
    "5-005-016": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["cold", "hot", "wet", "ventilate", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "high", "mid", "low"],
        "tc_real_temp": True
    },
    "5-005-017": {
        "type": "tc",
        "tc_set_temp_range": [5, 35],
        "tc_mode": ["auto", "cold", "hot", "wet", "ventilate", "wet_reheat", "floorheat", "mix"],
        "tc_wind_speed": ["auto", "super_high", "high", "mid_high", "mid", "mid_low", "low", "super_low"],
        "tc_temp_adjust": ["up", "down"],
        "tc_real_temp": True
    },
}
