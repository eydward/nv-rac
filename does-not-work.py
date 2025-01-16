"""
this doesn't work because TODO
leaving here for future reference
"""

import numpy as np
import itertools as it
from ortools.graph.python import min_cost_flow
from example import load_data
import pprint

SCALE_STUD = 0.05    # scale factor on compatibility(student, student)
SCALE_ROOMTYPE = 1  # scale factor on compatibility(student, room type)
SCALE_ROOMLOC = 0.8 # scale factor on compatibility(student, room location)
SCALE_SQUAT = 5     # scale factor on squatting rooms

FREE_SINGLES = 0    # reserve singles to keep empty
FREE_DOUBLES = 0    # reserve doubles to keep empty

students, student_info, rooms, room_info, years, squat, roommate_pref, room_pref = load_data()

MAX_SINGLES = len(rooms["single"]) - FREE_SINGLES
MAX_DOUBLES = len(rooms["double"]) - FREE_DOUBLES

def housing_points(student: str) -> int:
    """housing points based on time spent in NV + time spent at MIT, tiebroken by time spent in NV"""
    return 8 * (years[student][0]+years[student][1]) + 2 * years[student][0]

def affinity_roomtype(student: str, roomtype: str) -> int: 
    if student in squat:
        base_affinity = int(roomtype == squat[student][0])
        base_affinity *= SCALE_SQUAT
    else:
        base_affinity = int(roomtype == room_pref[student])
    return SCALE_ROOMTYPE * housing_points(student) * base_affinity

def affinity_roomloc(student: str, room: str) -> int:
    # room location ONLY (not including room type)
    # TODO
    return 0

def affinity_student(student1: str, student2: str) -> int:
    base_affinity = sum(c**2 for c in student_info[student1] - student_info[student2])
    return int(SCALE_STUD * (housing_points(student1) + housing_points(student2)) * base_affinity)

################ assign room types & double rooms ################
# assign room types
single_students = [(affinity_roomtype(s,"single"), s) for s in students if room_pref[s] == "single"]
double_students = [(affinity_roomtype(s,"double"), s) for s in students if room_pref[s] == "double"]

single_students.sort(reverse=True) # sort students by decreasing order of their right to a single
if len(single_students) > MAX_SINGLES:
    double_students.extend([(affinity_roomtype(s,"double"),s) for (saff, s) in single_students[MAX_SINGLES:]])
    single_students = single_students[:MAX_SINGLES]
elif len(double_students) > MAX_DOUBLES:
    assert False, "TODO what to do if too many people want doubles (we expect this to not happen)"
if len(double_students) % 2 != 0: # make sure number of people assigned to doubles is eve 
    s = single_students[-1]
    double_students.append((affinity_roomtype(s,"double"),s))
    single_students = single_students[:-1]

single_students = [s[1] for s in single_students]
double_students = [s[1] for s in double_students]
assert len(double_students) % 2 == 0, "TODO sanity check"
assert len(double_students) <= 2*MAX_DOUBLES, "no assignment possible: free singles/doubles constraint too tight"

# assign double rooms
def double_heuristic(double):
    return sum(affinity_roomloc(student, double) for student in double_students)

squat_doubles = set(squat[s][1] for s in students if (s in squat) and (squat[s][0] == "double")) # find all doubles being squatted (will be added to filled_doubles)
scored_doubles = sorted([(double_heuristic(double), double) for double in rooms["double"] if double not in squat_doubles], reverse=True) # score the rest of the doubles & sort from best-to-worst

assert len(double_students) >= 2*len(squat_doubles), "double-squatting and room preference counts misaligned"
filled_doubles = list(squat_doubles) + scored_doubles[:len(double_students)//2 - len(squat_doubles)]
assert 2 * len(filled_doubles) == len(double_students), "TODO sanity check"

print(f"students getting singles ({len(single_students)}): {single_students}")
print(f"students getting doubles ({len(double_students)}): {double_students}")
print(f"doubles to be filled ({len(filled_doubles)}): {filled_doubles}")


################ create min-cost flow network ################

vtx = [("source",), ("sink",), ("singles all",), ("doubles all",)] \
    + [("student",s) for s in students] \
    + [("single",s) for s in single_students] \
    + [("double in",s1,s2) for s1, s2 in it.combinations(double_students,2)] \
    + [("double out",s1,s2) for s1, s2 in it.combinations(double_students, 2)] \
    + [("single room",single) for single in rooms["single"]] \
    + [("double room",double) for double in filled_doubles]
vtx_inv = {string: index for index, string in enumerate(vtx)}

edges = []  # array of edges, as 4-tuples (start node, end node, capacity, unit cost)

#### all edges of the form source->student
for student in students:
    edges.append((("source",), ("student", student), 1, 0))

#### all edges of the form student->single(student)
for student in single_students:
    edges.append((("student", student), ("single", student), 1, -affinity_roomtype(student, "single")))

#### all edges of the form student->double(student1, student2)
for student1, student2 in it.combinations(double_students,2):
    # do not add edges if either student1 or student2 are already in a roommate zip
    if (student1 in roommate_pref) and (roommate_pref[student1] != student2):
        continue
    if (student2 in roommate_pref) and (roommate_pref[student2] != student1):
        continue
    
    double_in_node = ("double in", student1, student2)
    double_out_node = ("double out", student1, student2)
    for student in [student1, student2]:
        edges.append((("student", student), double_in_node, 1, -affinity_roomtype(student, "double")))
    edges.append((double_in_node, double_out_node, 2, -affinity_student(student1, student2)))

#### all edges of the form single(student)->room# and double(student1,student2)->room#
for student, room in it.product(single_students, rooms["single"]):
    edges.append((("single", student), ("single room",room), 1, -affinity_roomloc(student,room)))
for (student1,student2), room in it.product(it.combinations(double_students,2),filled_doubles):
    edges.append((("double out", student1, student2), ("double room", room), 2, 
                    -affinity_roomloc(student1,room) - affinity_roomloc(student2,room)))

#### edges to group together singles & move to sink
for single in rooms["single"]:
    edges.append((("single room",single), ("singles all",), 1, 0))
edges.append((("singles all",), ("sink",), len(rooms["single"]) - FREE_SINGLES, 0))

#### edges to group together doubles & move to sink
for double in filled_doubles:
    edges.append((("double room",double), ("doubles all",), 2, 0))
edges.append((("doubles all",), ("sink",), 2*(len(filled_doubles) - FREE_DOUBLES), 0))

# pprint.pprint(edges)

# ################ solve min-cost flow network ################

smcf = min_cost_flow.SimpleMinCostFlow()

start_nodes = []
end_nodes = []
capacities = []
unit_costs = []
for edge in edges:
    start_nodes.append(vtx_inv[edge[0]])
    end_nodes.append(vtx_inv[edge[1]])
    capacities.append(edge[2])
    unit_costs.append(edge[3])

all_arcs = smcf.add_arcs_with_capacity_and_unit_cost(
    start_nodes, end_nodes, capacities, unit_costs
)

# out-flow from source, in-flow to sink
smcf.set_node_supply(vtx_inv[("source",)], len(students))
smcf.set_node_supply(vtx_inv[("sink",)], -len(students))

# solve
status = smcf.solve()
if status != smcf.OPTIMAL:
    print("There was an issue with the min cost flow input.")
    print(f"Status: {status}")
    exit(1)

print(f"Minimum cost: {smcf.optimal_cost()}")
print("")
solution_flows = smcf.flows(all_arcs)
costs = solution_flows * unit_costs

# use the optimal flow to identify room assignments
room_assignments = {}
student_assignments = {}
for arc, flow, cost in zip(all_arcs, solution_flows, costs):
    tail, head = vtx[smcf.tail(arc)], vtx[smcf.head(arc)]
    print(f"{tail}\t->\t{head}\t\t\t{flow}/{smcf.capacity(arc)}\t{cost}")
    if flow == 0:
        continue
    if tail[0] == "single":
        student = tail[1]
        assert(head[0] == "single room")
        # assert flow == 1
        room = head[1]
        room_assignments[room] = (student,)
    if tail[0] == "double out":
        student1, student2 = tail[1], tail[2]
        assert head[0] == "double room"
        # assert flow == 2
        room = head[1]
        room_assignments[room] = (student1, student2)

pprint.pprint(room_assignments)
