# rac
tool to compute housing assignments in new vassar

## algorithm

### parameters

todo

### heuristic-selection component

min-cost-flow setup works only when (#doubles) = 2*(#people being assigned to doubles).
the first stage decides what room type each person gets assigned to, and then decides the set of doubles that are going to be filled. (note that we do *not* need to decide the set of single rooms that are going to be filled, though we do need to decide the set of people that are getting singles)

we do this as follows: first calculate maximum number of singles $S$ and maximum number of doubles $D$ that we can assign. Then place all people into their desired room type. This should result in too many singles being assigned; move those with lowest priority into the doubles list until the number of people in singles is at most $S$, and the number of people in doubles is even.

Next we determine the set of doubles to assign; we do this heuristically by
- including all doubles that are being squatted
- for each remaining double, summing the compatibility scores of the double with all people assigned to doubles, and discarding the ones with lowest sum to make up everything else


### min-cost flow component

todo