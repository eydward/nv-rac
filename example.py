# TODO you also have to handle people who forgot to fill in the form
import numpy as np

students = ["a", "b", "c", "d", "e", "f"] # array of all student kerbs (distinct)
student_info = {
    "a": np.array([1, 2, 0, 1], dtype=int),
    "b": np.array([-1, 0, 1, -2], dtype=int),
    "c": np.array([1, -2, -2, 2], dtype=int),
    "d": np.array([2, 2, 2, 2], dtype=int),
    "e": np.array([2, -2, -1, 2], dtype=int),
    "f": np.array([2, 2, 2, 1], dtype=int),
}  # map: student -> np.vector of preferences (TODO)
rooms = {"single": ["1", "2", "7", "8"], "double": ["3", "4", "5", "6"]}
room_info = {}          # map: room -> list of room properties
years = {
    "a": (3, 3),
    "b": (4, 3),
    "c": (1, 1),
    "d": (0, 0),
    "e": (2, 0),
    "f": (3, 2),
}  # map: student -> (years in New Vassar, years at MIT)
squat = {}              # map: student -> (roomtype, room#) if squatting previous room
roommate_pref = {}      # map: student -> student (TODO check that this is commutative & matches squat)
room_pref = {
    "a": "single",
    "b": "single",
    "c": "double",
    "d": "double",
    "e": "single",
    "f": "single",
}  # map: student -> str(room type)

# students = ["a", "b"] # array of all student kerbs (distinct)
# student_info = {
#     "a": np.array([1, 2, 0, 1], dtype=int),
#     "b": np.array([1, 2, 0, 1], dtype=int),
# }  # map: student -> np.vector of preferences (TODO)
# rooms = {"single": [], "double": ["3", "4"]}
# room_info = {}          # map: room -> list of room properties
# years = {
#     "a": (3, 3),
#     "b": (3, 3),
# }  # map: student -> (years in New Vassar, years at MIT)
# squat = {}              # map: student -> (roomtype, room#) if squatting previous room
# roommate_pref = {}      # map: student -> student
# room_pref = {
#     "a": "double",
#     "b": "double",
# }  # map: student -> str(room type)


def load_data():
    return students, student_info, rooms, room_info, years, squat, roommate_pref, room_pref
