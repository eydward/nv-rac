import pandas as pd
import numpy as np
import json

# TODO you also have to handle people who forgot to fill in the form

students = []  # array of all student kerbs (distinct)
student_info = {}  # map: student -> np.vector of preferences (TODO)
rooms = {"single": [], "double": []}
room_info = {}  # map: room -> list of room properties
squat = {}  # map: student -> (roomtype, room#) if squatting previous room
roommate_pref = {}  # map: student -> student
room_pref = {}  # map: student -> str(room type)

def load_data():
    return students, student_info, rooms, room_info, squat, roommate_pref, room_pref

def read_housing_intent(student_info):
    """
    modifies student_info to add personal preference information from the housing intent form
    """
    housing_intent = pd.read_csv("./data/confidential/housing_intent.csv")
    # TODO - transform all the string form responses into actual data
    for idx, row in housing_intent.iterrows():
        print(row)
        break

    # TODO - deal with students that aren't on the housing intent form

def read_nv_housing_form():
    pass

def add_housegov_points(student_info):
    """
    modifies student_info to give extra housing points to students in NV-gov.
    """
    gov_positions = json.load("./data/government_positions.json")
    gov_points = json.load("./data/government_points.json")  # points-per-semester
    for year, positions in gov_positions:
        for position, stud_list in positions.items():
            # get comma-separated kerbs (and remove any whitespace)
            stud_list = list(map(str.strip, stud_list.split(",")))
            for stud in stud_list:
                if stud in students:
                    student_info[stud]["housing points"] += gov_points[position]

def load_data():
    # students
    students = [] # TODO list of all students

    # rooms
    rooms = [] # TODO list of all rooms

    # years
    years = {} # TODO map student -> year
    return students, rooms, years, squat, roommate_pref, room_pref, student_embeddings

read_housing_intent(student_info)