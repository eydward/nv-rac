import numpy as np

# TODO you also have to handle people who forgot to fill in the form

students = []           # array of all student kerbs (distinct)
rooms = {"single": [], "double": []}
student_embeddings = {} # map: student -> np.vector of preferences (TODO)
room_info = {}          # map: room -> list of room properties
years = {}              # map: student -> (years in New Vassar, years at MIT)
squat = {}              # map: student -> (True, roomtype, room#) if squatting previous room, or False if not
roommate_pref = {}      # map: student -> student (TODO check that this is commutative)
room_pref = {}          # map: student -> str(room type)

def get_form_results():
    """
    map: student -> a whole ton of stuff
    if student failed to fill out form, then 
    """
    data = np.genfromtxt(path_to_csv, dtype=float, delimiter=",", names=True)
    form_results = {}
    return form_results()

def load_data():
    return students, rooms, years, squat, roommate_pref, room_pref, student_embeddings
