import numpy as np
import itertools as it
from ortools.graph.python import min_cost_flow
from load_data import load_data

SCALE_STUD = 0.2    # scale factor on compatibility(student, student)
SCALE_ROOMTYPE = 1  # scale factor on compatibility(student, room type)
SCALE_ROOMLOC = 0.8 # scale factor on compatibility(student, room location)
SCALE_SQUAT = 5     # scale factor on squatting rooms

FREE_SINGLES = 0    # reserve singles to keep empty
FREE_DOUBLES = 0    # reserve doubles to keep empty


students, rooms, years, squat, roommate_pref, room_pref, student_embeddings = load_data()

def housing_points(student: str) -> int: # TODO check that this is actually an integer
    """housing points based on time spent in NV + time spent at MIT, tiebroken by time spent in NV"""
    return 2**(2*(years[student][0]+years[student][1])) + 2*years[student][0]

def affinity_roomtype(student: str, roomtype: str) -> int: 
    if squat[student]:
        base_affinity = int(roomtype == squat[student][1])
    else:
        base_affinity = int(roomtype == room_pref[student])
    return SCALE_ROOMTYPE * housing_points(student) * base_affinity

def affinity_roomloc(student: str, room: str) -> int:
    # room location ONLY (not including room type)
    # TODO
    return 0

def affinity_student(student1: str, student2: str) -> int:
    base_affinity = np.linalg.norm(student_embeddings[student1] - student_embeddings[student2])
    return SCALE_STUD * (housing_points(student1) + housing_points(student2)) * base_affinity


################ create min-cost flow network ################

vertices = ["source", "sink"] \
    + [f"student:{s}" for s in students] \
    + [f"single:{s}" for s in students] \
    + [f"double:in:{s1},{s2}" for s1, s2 in it.combinations(students,2)] \
    + [f"double:out:{s1},{s2}" for s1, s2 in it.combinations(students, 2)] \
    + [f"single:{single}" for single in rooms["single"]] \
    + [f"double:{double}" for double in rooms["double"]]

edges = []  # array of edges, as 4-tuples (start node, end node, capacity, unit cost)


#### all edges of the form source->student
for student in students:
    edges.append(tuple("source", f"student:{student}", 1, 0))

#### all edges of the form student->single(student)
for student in students:
    edges.append(tuple(f"student:{student}", f"single:{student}", 1, -affinity_roomtype(student, "single")))

#### all edges of the form student->double(student1, student2)
for student1, student2 in it.combinations(students,2):
    # do not add edges if either student1 or student2 are already in a roommate zip
    if (student1 in roommate_pref) and (roommate_pref[student1] != student2):
        continue
    if (student2 in roommate_pref) and (roommate_pref[student2] != student1):
        continue
    
    double_in_node = f"double:in:{student1},{student2}"
    double_out_node = f"double:out:{student1},{student2}"
    for student in [student1, student2]:
        edges.append(tuple(student, double_in_node, 1, -affinity_roomtype(student, "double")))
    edges.append(tuple(double_in_node, double_out_node, 1, -affinity_student(student1, student2)))

#### all edges of the form single(student)->room# and double(student1,student2)->room#
for student, room in it.product(students, rooms["single"]):
    edges.append(tuple(f"single:{student}", f"single:{room}", 1, -affinity_roomloc(student,room)))
for (student1,student2), room in it.product(it.combinations(students,2),rooms["double"]):
    edges.append(tuple(f"double:out:{student1},{student2}", f"double:{room}", 1, 
                       -affinity_roomloc(student1,room) - affinity_roomloc(student2,room)))

#### edges to group together singles & move to sink
for single in rooms["single"]:
    edges.append("single:{room}", "singles:all", 1, 0)
edges.append("singles:all", "sink", len(rooms["single"]) - FREE_SINGLES, 0)

#### edges to group together singles
for double in rooms["double"]:
    edges.append("double:{room}", "doubles:all", 2, 0)
edges.append("doubles:all", "sink", len(rooms["double"]) - FREE_DOUBLES, 0)

################ solve min-cost flow network ################

smcf = min_cost_flow.SimpleMinCostFlow()

# arcs
start_nodes, end_nodes, capacities, unit_costs = (list(x) for x in zip(*edges))
all_arcs = smcf.add_arcs_with_capacity_and_unit_cost(
    start_nodes, end_nodes, capacities, unit_costs
)

# out-flow from source, in-flow to sink
smcf.set_node_supply("source", len(students))
smcf.set_node_supply("sink", len(students))

# solve
status = smcf.solve()
if status != smcf.OPTIMAL:
    print("There was an issue with the min cost flow input.")
    print(f"Status: {status}")
    exit(1)

print(f"Minimum cost: {smcf.optimal_cost()}")
print("")
print(" Arc    Flow / Capacity Cost")
solution_flows = smcf.flows(all_arcs)
costs = solution_flows * unit_costs
for arc, flow, cost in zip(all_arcs, solution_flows, costs):
    print(
        f"{smcf.tail(arc):1} -> {smcf.head(arc)}  {flow:3}  / {smcf.capacity(arc):3}       {cost}"
    )
