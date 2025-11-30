#!/usr/bin/python

import argparse
import itertools
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

class TournamentScheduler:
    def __init__(self, num_teams: int):
        if num_teams % 2 != 0:
            raise ValueError("Number of teams must be even")
        self.num_teams = num_teams
        self.num_weeks = num_teams - 1
        self.num_periods = num_teams // 2

        self.var_map = {}
        self.reverse_var_map = {}
        self.next_var = 1
        self.clauses = []

    def get_var(self, week: int, period: int, team1: int, team2: int) -> int:
        """Get variable number for a match between team1 (home) and team2 (away)."""
        key = (week, period, team1, team2)
        if key not in self.var_map:
            self.var_map[key] = self.next_var
            self.reverse_var_map[self.next_var] = key
            self.next_var += 1
        return self.var_map[key]

    def add_constraints(self):
        # 1. Each team must play against every other team exactly once (either home or away)
        for team1 in range(self.num_teams):
            for team2 in range(team1 + 1, self.num_teams):
                plays_once = []
                for week in range(self.num_weeks):
                    for period in range(self.num_periods):
                        # Add both home and away possibilities
                        plays_once.append(self.get_var(week, period, team1, team2))  # team1 at home
                        plays_once.append(self.get_var(week, period, team2, team1))  # team2 at home
                
                # Exactly one match between each pair of teams
                self.clauses.append(plays_once)  # At least one match
                for i, j in itertools.combinations(plays_once, 2):
                    self.clauses.append([-i, -j])  # At most one match

        # 2. Each team can play only once in one week
        for week in range(self.num_weeks):
            for team in range(self.num_teams):
                # Get all possible matches for this team in this week (both home and away)
                week_matches = []
                for period in range(self.num_periods):
                    for other_team in range(self.num_teams):
                        if team != other_team:
                            week_matches.append(self.get_var(week, period, team, other_team))  # home
                            week_matches.append(self.get_var(week, period, other_team, team))  # away
                
                # At most one match per week
                for i, j in itertools.combinations(week_matches, 2):
                    self.clauses.append([-i, -j])

        # 3. Each team can play up to twice in one period (across all weeks)
        for period in range(self.num_periods):
            for team in range(self.num_teams):
                # Get all matches in this period for this team
                period_matches = []
                for week in range(self.num_weeks):
                    for other_team in range(self.num_teams):
                        if team != other_team:
                            # Count both home and away matches for this team in this period
                            var = self.get_var(week, period, team, other_team)  # home
                            if var not in period_matches:
                                period_matches.append(var)
                            var = self.get_var(week, period, other_team, team)  # away
                            if var not in period_matches:
                                period_matches.append(var)
                
                # At most two matches in this period
                for matches in itertools.combinations(period_matches, 3):
                    self.clauses.append([-matches[0], -matches[1], -matches[2]])

        # 4. Only one match per period per week
        for week in range(self.num_weeks):
            for period in range(self.num_periods):
                period_matches = []
                for team1 in range(self.num_teams):
                    for team2 in range(team1 + 1, self.num_teams):
                        period_matches.append(self.get_var(week, period, team1, team2))
                        period_matches.append(self.get_var(week, period, team2, team1))
                
                # At most one match per period
                for i, j in itertools.combinations(period_matches, 2):
                    self.clauses.append([-i, -j])

        # 5. Each week must have at least one match
        for week in range(self.num_weeks):
            week_matches = []
            for period in range(self.num_periods):
                for team1 in range(self.num_teams):
                    for team2 in range(team1 + 1, self.num_teams):
                        week_matches.append(self.get_var(week, period, team1, team2))
                        week_matches.append(self.get_var(week, period, team2, team1))
            self.clauses.append(week_matches)

    def write_cnf(self, output_file: str):
        """CNF formula in DIMACS format."""
        with open(output_file, "w") as f:
            f.write(f"p cnf {len(self.var_map)} {len(self.clauses)}\n")
            for clause in self.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")

    def solve(self) -> Optional[List[List[Tuple[int, int]]]]:
        """Solve the tournament."""
        self.add_constraints()
        
        cnf_file = "tournament.cnf"
        self.write_cnf(cnf_file)
        
        # Run solver
        solver_path = "glucose-syrup" 
        result = subprocess.run(['./' + solver_path, '-model', '-verb=1', cnf_file], stdout=subprocess.PIPE)
        
        solver_output = result.stdout.decode('utf-8')
        """
        print(solver_output)
        """
        # Parse the solution
        solution_lines = solver_output.splitlines()
        model = None
        for line in solution_lines:
            if line.startswith('v '):
                model = list(map(int, line[2:].strip().split()))
                break
        
        if model is None:
            return None
        
        schedule = [[None for _ in range(self.num_periods)] for _ in range(self.num_weeks)]
        
        for var in model:
            if var > 0 and var in self.reverse_var_map:
                week, period, team1, team2 = self.reverse_var_map[var]
                schedule[week][period] = (team1, team2)
        
        return schedule

def print_schedule(schedule: List[List[Optional[Tuple[int, int]]]], align: int = 8):
    """Print the schedule."""
    num_weeks = len(schedule)
    num_periods = len(schedule[0])
    
    print("\t", end="")
    for w in range(num_weeks):
        print(f"Week {w+1}\t", end="")
    print()
    
    for p in range(num_periods):
        print(f"Period {p+1}\t", end="")
        for w in range(num_weeks):
            if schedule[w][p] is not None:
                team1, team2 = schedule[w][p]
                match = f"{team1} v {team2}"
                print(f"{match:<{align}}\t", end="")
            else:
                print(f"{'-----':<{align}}\t", end="")
        print()

def main():
    parser = argparse.ArgumentParser(description='Tournament schedule gen /w SAT')
    parser.add_argument('num_teams', type=int, help='N of teams')
    parser.add_argument('--output-cnf', type=str, help='Output CNF formula to file')
    args = parser.parse_args()

    scheduler = TournamentScheduler(args.num_teams)
    
    if args.output_cnf:
        scheduler.write_cnf(args.output_cnf)
    
    schedule = scheduler.solve()
    
    if schedule is None:
        print("No solution found!")
        return
    
    print(f"\nSchedule for {args.num_teams} teams:")
    print_schedule(schedule)

if __name__ == "__main__":
    main()
