import numpy as np
import itertools as it
from example import load_data, diagnostics
from queue import PriorityQueue

from ortools.graph.python import min_cost_flow

import pprint

SCALE_STUD = 0.05  # scale factor on compatibility(student, student)
SCALE_ROOMTYPE = 1  # scale factor on compatibility(student, room type)
SCALE_ROOMLOC = 0.8  # scale factor on compatibility(student, room location)
SCALE_SQUAT = 5  # scale factor on squatting rooms

FREE_SINGLES = 2  # reserve singles to keep empty
FREE_DOUBLES = 2  # reserve doubles to keep empty

students, student_info, rooms, room_info, years, squat, roommate_pref, room_pref = load_data()

MAX_SINGLES = len(rooms["single"]) - FREE_SINGLES
MAX_DOUBLES = len(rooms["double"]) - FREE_DOUBLES
print("allocatable singles: ", MAX_SINGLES)
print("allocatable doubles: ", MAX_DOUBLES)
assert MAX_SINGLES + 2*MAX_DOUBLES >= len(students), "too few rooms allocatable"


def housing_points(student: str):
    """housing points based on time spent in NV + time spent at MIT, tiebroken by time spent in NV"""
    return 8 * (years[student][0] + years[student][1]) + 2 * years[student][0]

def affinity_roomtype(student: str, roomtype: str):
    if student in squat:
        base_affinity = 1 if roomtype == squat[student][0] else -1
        base_affinity *= SCALE_SQUAT
    else:
        base_affinity = 1 if roomtype == room_pref[student] else -1
    return SCALE_ROOMTYPE * housing_points(student) * base_affinity

def student_similarity(student1: str, student2: str):
    """
    returns tuple: bool = False if you can't put them together, bool = True if you can
    second term is a float; lower values indicate more similar
    """
    # TODO consider banned pairs & gender diffs or something
    # return False, 0

    base_affinity = np.linalg.norm(student_info[student1] - student_info[student2])
    return True, SCALE_STUD * (housing_points(student1) + housing_points(student2)) * base_affinity

def affinity_roomloc(student: str, roomtype: str) -> int:
    # TODO account for lounge location, potentially other things, and
    # TODO account for squatting
    return SCALE_ROOMLOC * 0


################ assign room types & double rooms ################

def assign_roomtypes(students):
    # TODO randomize tiebreaking
    # descending order of their priority on this roomtype
    single_students = PriorityQueue()
    double_students = PriorityQueue()
    for s in students:
        if room_pref[s] == "single":
            single_students.put((affinity_roomtype(s, "single"), s))
        else:
            double_students.put((affinity_roomtype(s, "double"), s))

    # ensure #singles <= MAX_SINGLES
    while len(single_students.queue) > MAX_SINGLES or len(double_students.queue) % 2 != 0:
        saff, s = single_students.get()
        double_students.put((affinity_roomtype(s, "double"), s))

    # ensure #doubles <= MAX_DOUBLES
    while len(double_students.queue) > 2*MAX_DOUBLES or len(double_students.queue) % 2 != 0:
        saff, s = double_students.get()
        single_students.put((affinity_roomtype(s, "single"), s))

    single_students = [s[1] for s in single_students.queue]
    double_students = [s[1] for s in double_students.queue]
    print("students assigned to singles: ", single_students)
    print("students assigned to doubles: ", double_students)
    return single_students, double_students


################ find a stable matching of roommates in doubles ################

from matching import Player
from matching.games import StableRoommates

def assign_roommates(double_students):
    def preference_list(student):
        """
        list of preference order for roommates. if preferred roommate exists, put them first. everyone else is ranked in order of most-similar to least-similar.
        """
        prefs = []
        rem_students = [s for s in double_students if s != student and student_similarity(s,student)[0]]
        if student in roommate_pref:
            prefs.append(roommate_pref[student])
            rem_students.remove(roommate_pref[student])
        prefs += sorted(rem_students, key = lambda s : student_similarity(student, s))
        return prefs
    
    sp_map = {student: Player(student) for student in double_students}
    for student in double_students:
        sp_map[student].set_prefs(
            [sp_map[s] for s in preference_list(student)]
        )
    game = StableRoommates(list(sp_map.values()))
    roommates = [(p1.name, p2.name) for p1, p2 in dict(game.solve()).items() if p1.name < p2.name]
    print("roommate pairs: ", roommates)
    return roommates

################ match students into rooms ################

def solve_min_cost_flow(vertices, edges, net_flow):
    """
    TODO describe helper function (basically just turns this into flow & solves it)
    requires a ("source",) and a ("sink",) vertex btw
    returns map: (tail, head) -> (flow, cost)
    """
    vertices_inv = {label: index for index, label in enumerate(vertices)}
    smcf = min_cost_flow.SimpleMinCostFlow()

    start_nodes = []
    end_nodes = []
    capacities = []
    unit_costs = []
    for edge in edges:
        start_nodes.append(vertices_inv[edge[0]])
        end_nodes.append(vertices_inv[edge[1]])
        capacities.append(edge[2])
        unit_costs.append(edge[3])

    all_arcs = smcf.add_arcs_with_capacity_and_unit_cost(
        start_nodes, end_nodes, capacities, unit_costs
    )

    # out-flow from source, in-flow to sink
    smcf.set_node_supply(vertices_inv[("source",)], net_flow)
    smcf.set_node_supply(vertices_inv[("sink",)], -net_flow)

    # solve
    status = smcf.solve()
    if status != smcf.OPTIMAL:
        print("There was an issue with the min cost flow input.")
        print(f"Status: {status}")
        exit(1)

    solution_flows = smcf.flows(all_arcs)
    costs = solution_flows * unit_costs

    sol_flow = {} # map: (tail, head) -> (flow, cost)
    for arc, flow, cost in zip(all_arcs, solution_flows, costs):
        tail, head = vertices[smcf.tail(arc)], vertices[smcf.head(arc)]
        # print(f"{tail}\t->\t{head}\t\t\t{flow}/{smcf.capacity(arc)}\t{cost}")
        sol_flow[(tail,head)] = (flow,cost)
    return sol_flow

def assign_singles(single_students):
    vertices = [("source",),("sink",)] \
        + [("student", student) for student in single_students] \
        + [("single", single) for single in rooms["single"]]

    edges = [(("source",), ("student", student), 1, 0) for student in single_students] \
        + [(("student", student), ("single", single), 1, affinity_roomloc(student, single))
           for student, single in it.product(single_students, rooms["single"])] \
        + [(("single", single), ("sink",), 1, 0) for single in rooms["single"]]

    flow = solve_min_cost_flow(vertices, edges, len(single_students))
    nonzero_flow_edges = [e for e in flow.keys() if flow[e][0] != 0]
    single_assignment = {}
    for e in nonzero_flow_edges:
        if e[0][0] == "student":
            single_assignment[e[0][1]] = e[1][1]
    assert set(single_assignment.keys()) == set(single_students), "all single_students should be assigned"
    return single_assignment


def assign_doubles(roommates):
    vertices = [("source",),("sink",)] \
        + [("roommate", roommate) for roommate in roommates] \
        + [("double", double) for double in rooms["double"]]

    edges = [(("source",), ("roommate", roommate), 1, 0) for roommate in roommates] \
        + [(("roommate", roommate), ("double", double), 1, affinity_roomloc(roommate[0], double) + affinity_roomloc(roommate[1], double))
           for roommate, double in it.product(roommates, rooms["double"])] \
        + [(("double", double), ("sink",), 1, 0) for double in rooms["double"]]

    flow = solve_min_cost_flow(vertices, edges, len(roommates))
    nonzero_flow_edges = [e for e in flow.keys() if flow[e][0] != 0]
    double_assignment = {}
    for e in nonzero_flow_edges:
        if e[0][0] == "roommate":
            double_assignment[e[0][1]] = e[1][1]
    assert set(double_assignment.keys()) == set(roommates), "all roommates should be assigned"
    return double_assignment

single_students, double_students = assign_roomtypes(students)
roommates = assign_roommates(double_students)
single_assignment = assign_singles(single_students)
double_assignment = assign_doubles(roommates)

students_in_room = {room: () for room in rooms["single"] + rooms["double"]} # map: room -> () or (student,) or (student, student)
room_assignment = {} # map: student -> room

for student, single in single_assignment.items():
    students_in_room[single] = (student,)
    room_assignment[student] = single
for roommate, double in double_assignment.items():
    students_in_room[double] = roommate
    room_assignment[roommate[0]] = double
    room_assignment[roommate[1]] = double

pprint.pprint(room_assignment)
pprint.pprint(students_in_room)

diagnostics(room_assignment, students_in_room)