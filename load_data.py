import pandas as pd
import numpy as np
import json

YEAR = 2025

# TODO you also have to handle people who forgot to fill in the form

students = []  # array of all student kerbs (distinct)
student_info = {}  # map: student -> np.vector of preferences (TODO)
room_info = {}  # map: room -> list of room properties
squat = {}  # map: student -> (roomtype, room#) if squatting previous room
roommate_pref = {}  # map: student -> student
room_pref = {}  # map: student -> str(room type)

def read_housing_intent(student_info):
    """
    modifies student_info to add personal preference information from the housing intent form
    """
    cleanliness = {
        "I prefer my room to be neat and clean all of the time": 1,
        "I like my room to be neat most of the time but can tolerate some clutter": 0,
        "Mess/clutter does not bother me": -1
    }
    study_environment = {
        "I need a study environment that is quiet with few distractions": 1,
        "No Preference": 0,
        "I can study effectively in either type of environment": -1
    }
    temperature = {
        "I prefer a warm temperature (Above 72°F/22°C)": 1,
        "No Preference": 0,
        "I prefer a cooler temperature (Below 68°F/20°C)": -1
    }
    wakeup_time = {
        "Before 6am": -2,
        "Between 6am - 8am": -1,
        "Between 8am - 10am": 0,
        "Between 10am - 12pm (noon)": 1,
        "After 12pm (noon)": 2
    }
    sleep_time = {
        "Before 8pm": -2,
        "Between 8-10pm": -1, # TODO - is the response format really this inconsistent?!
        "Between 10pm - 12am (midnight)": 0,
        "Between 12am (midnight) - 2am": 1,
        "After 2am": 2
    }
    guests = {
        "Guests should always be coordinated to make sure all residents are comfortable.": -1,
        "Let's talk as a suite/apartment about what rules we want to set around guests coming over.": 0,
        "Spontaneity is awesome! Guests and significant others are always welcome!": 1
    }
    overnight = {
        "I prefer that overnight guests are only hosted on rare occasions.": -1,
        "Hosting overnight guests occasionally is fine with me, maybe a few times a month.": 0,
        "Hosting overnight guests frequently is fine with me, within the housing policy.": 1
    }

    housing_intent = pd.read_csv("./data/confidential/housing_intent.csv")
    
    # check for duplicate entries (e.g. created by supplemental requests), then throw an Error, since these must be resolved manually in case of conflicts
    if housing_intent["Kerberos"].duplicated().empty:
        print("duplicated kerbs:")
        print(housing_intent[housing_intent["Kerberos"].duplicated()])
        raise Exception("duplicated kerbs exist in housing intent form; please merge")
    
    for idx, row in housing_intent.iterrows():
        student_info[row["Kerberos"]] = {
            "firstname": row["Preferred Name"],
            "lastname": row["Last Name"],
            "email": row["Email"],
            "year": YEAR + 5 - (row["Class Year"] or 0),
            "gender": row["Gender Description"],
            "cleanliness": cleanliness.get(row["Room Cleanliness"], 0),
            "environment": study_environment.get(row["Study Environment"], 0),
            "temperature": temperature.get(row["Room Temperature"], 0),
            "same class": not(row["Different Class Year"] == "No"), # set blank/other input -> True
            "weekday_wakeup": wakeup_time.get(row["Weekday Wake Up"], 0),
            "weekday_sleep": sleep_time.get(row["Weekday Sleep"], 0),
            "weekend_wakeup": wakeup_time.get(row["Weekend Wake Up"], 0),
            "weekend_sleep": sleep_time.get(row["Weekend Sleep"], 0),
            "guests": guests.get(row["Guest"], 0),
            "overnight": overnight.get(row["Guest"], 0),
            "esa": row["Living with ESA"] == "Yes"
        }
    
    # TODO - unclear if/where I can obtain a list of all residents
    # assert set(student_info.keys()) == set(students), "not all students found in housing intent forms"

def read_nv_housing_form():
    # TODO - this obviously depends on what the NV housing form looks like
    pass

def compute_housing_points(student_info):
    for student in student_info:
        student["housing points"] = student["year"]
    
    # TODO housing points also depends on # years at NV, but it is unclear where one can find data to calculate this.

    gov_positions = json.load("./data/government_positions.json")
    gov_points = json.load("./data/government_points.json")  # points-per-semester
    for year, positions in gov_positions:
        for position, stud_list in positions.items():
            # get comma-separated kerbs (and remove any whitespace)
            stud_list = list(map(str.strip, stud_list.split(",")))
            for stud in stud_list:
                if stud in students:
                    student_info[stud]["housing points"] += gov_points[position]

def load_rooms(room_info, rooms):
    ## no longer necessary to parse data/new_vassar_rooms.txt, since data/new_vassar_rooms.json is more useful
    # with open("./data/new_vassar_rooms.txt") as room_list_file:
    #     room_list = [line.rstrip() for line in room_list_file]
    #     ct = {}
    #     for room in room_list:
    #         if room not in ct:
    #             ct[room] = 0
    #         ct[room] += 1
    #     for room in room_list:
    #         if ct[room] == 1:
    #             rooms["single"].append(room)
    #         elif ct[room] == 2:
    #             if room not in rooms["double"]:
    #                 rooms["double"].append(room)
    #         else:
    #             raise Exception(f"room list file is corrupted: room {room} appears more than 2 times")
    
    room_info = json.load("./data/new_vassar_rooms.json")
    for rooms in room_info:
        room_info[rooms] = room_info[rooms].split(",")

    assert len(rooms["single"]) == 120, f"there should be 120 singles but room list file contains only {len(rooms["single"])}"
    assert len(rooms["double"]) == 165, f"there should be 165 doubles but room list file contains only {len(rooms["double"])}"

def load_data():
    students = [] # TODO list of all students

    rooms = {"single": [], "double": []}
    room_info = {}
    load_rooms(room_info, rooms)

    read_housing_intent(student_info)
    
    compute_housing_points(student_info) 

    return students, student_info, rooms, room_info
    # return students, student_info, rooms, room_info, squat, roommate_pref, room_pref

load_data()
