# Tournament Schedule SAT Solver

A Python SAT solver for optimal tournament schedules.

## Features

- Generates optimal tournament schedules for even number of teams
- Each team plays against every other team exactly once
- Maintains scheduling constraints:
  - One match per team per week
  - Maximum two matches per team in any period
  - One match per period per week
- Performance analysis for different team sizes

## Requirements

- Python 3.11+
- External Glucose SAT Solver

## Test Instances

1. n = 4  | Unsolvable
2. n = 6  | Easy example
3. n = 8  | Medium
4. n = 10 | Hard

## Usage

```python
from tournament_solver import TournamentScheduler, print_schedule

# Create a scheduler for 6 teams
scheduler = TournamentScheduler(6)

# Generate the schedule
schedule = scheduler.solve()

# Print the schedule
if schedule:
    print_schedule(schedule)
```

## **Formal Problem Description (Tournament Scheduling as SAT)**

We schedule a tournament of **$n$ teams** over **$n-1$ weeks**.
Each week contains **$n/2$ periods**, and each period contains **two slots** (home team vs. away team).

Let:

* $T = {1,\dots,n}$ be the teams
* $W = {1,\dots,n-1}$ the weeks
* $P = {1,\dots,n/2}$ the periods
* $S = {1,2}$ the slots
* Boolean variable
  $$x_{a,b,w,p,s} = 1 \quad \text{if team } a \text{ plays team } b \text{ in week } w,\text{ period } p,\text{ slot } s$$
  Slot $1$: **a plays at home**.
  Slot $2$: **a plays away**.

---

### **1. Every team plays exactly one match per week**

At least one match per week:

$$
\forall a\in T,\ \forall w\in W:\quad
\bigvee_{b\neq a,; p\in P,; s\in S} x_{a,b,w,p,s}
$$

At most one:

$$
\forall a,w,\ \forall (b_1,p_1,s_1)\neq(b_2,p_2,s_2):
\quad \neg\big(x_{a,b_1,w,p_1,s_1} \wedge x_{a,b_2,w,p_2,s_2}\big)
$$

---

### **2. Every pair of teams plays exactly once**

Each unordered pair ${a,b}$ appears somewhere:

$$
\bigvee_{w,p,s} \big(x_{a,b,w,p,s} ;\vee; x_{b,a,w,p,s}\big)
$$

And not twice:

$$
\forall (w_1,p_1,s_1)\neq(w_2,p_2,s_2):;
\neg\big(x_{a,b,w_1,p_1,s_1} \wedge x_{a,b,w_2,p_2,s_2}\big)
$$

---

### **3. Team appears in a period at most twice**

For each team $a$ and period $p$:

$$
\sum_{w\in W,\ b\neq a,\ s\in S}
\left(x_{a,b,w,p,s} + x_{b,a,w,p,s}\right)
\le 2
$$

---

### **4. No overlapping inside one slot**

A single slot can host only one match:

$$
\forall w,p,s,\ \forall (a_1,b_1)\neq(a_2,b_2):
\neg\big(x_{a_1,b_1,w,p,s} \wedge x_{a_2,b_2,w,p,s}\big)
$$

---

## Performance Analysis

The solver's performance has been analyzed for different team sizes:
- 4 teams: NOT SOLVABLE
- 6 teams: 1.77 seconds
- 8 teams: 13.72 seconds
- 10 teams: 153.22 seconds
- 12 teams: Solvable, just not on my machine.

![Performance Analysis](performance_analysis.png)

The graph shows exponential growth in solving time as the number of teams increases. This is expected due to the NP-complete nature of the SAT problem.

## Limitations

- Only supports even number of teams
- Performance degrades exponentially with team size
- Practical limit around 6-10 teams

## File Structure

- `tournament_solver.py`: Main solver implementation
- `README.md`: Project documentation
- `glucose-syrup`: Required SAT solver

## Author

- Oleksandr Yatsenko
