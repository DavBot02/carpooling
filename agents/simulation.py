MOCK_SIMULATION_STATE = {
    "state": {
        "total_cars": 50,
        "carpooling_cars": 25,
        "active_people": 50
    },
    "cars": [
        {
            "unique_id": 0,
            "position": {
                "x": 13.0,
                "y": 15.0
            },
            "next_poisition": {
                "x": 14.0,
                "y": 15.0
            },
            "people_onboard": 3,
            "capacity": 4
        }
    ],
    "persons": [
        {
            "unique_id": 0,
            "position": {
                "x": 13.0,
                "y": 15.0
            },
            "next_poisition": {
                "x": 14.0,
                "y": 15.0
            },
            "is_onboard": True
        }
    ],
    "intersection": {
        "unique_id": 0,
        "upper_left_corner": {
            "x": 0.0,
            "y": 0.0
        },
        "bottom_right_corner": {
            "x": 12.0,
            "y": 12.0
        },
        "direction": "NORTH"
    }
}

def get_step():
    return MOCK_SIMULATION_STATE