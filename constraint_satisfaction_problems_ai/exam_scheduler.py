"""Υλοποίηση CSP Χρονοπρογραμματισμού Εξετάσεων βασισμένη στο πλαίσιο AIMA Python CSP."""

import time
import pandas as pd
from csp import *
from collections import defaultdict
import itertools

# Import required functions from AIMA's CSP implementation
from utils import argmin_random_tie

class ExamSchedulerCSP(CSP):
    """CSP για το πρόβλημα χρονοπρογραμματισμού εξετάσεων."""

    def __init__(self, courses):
        """Δημιουργία CSP χρονοπρογραμματισμού εξετάσεων."""
        self.constraint_weights = defaultdict(lambda: 1)

        # Δημιουργία μεταβλητών και αποθήκευση πληροφοριών μαθημάτων
        variables = []
        self.course_info = {}
        lab_pairs = {}  # Παρακολούθηση ζευγών θεωρίας-εργαστηρίου

        # Πρώτο πέρασμα: Δημιουργία εξετάσεων θεωρίας και καταγραφή απαιτήσεων εργαστηρίου
        for course in courses:
            name = str(course['Μάθημα'])  # Μετατροπή σε string για διαχείριση τυχόν NaN
            variables.append(name)

            # Μετατροπή boolean strings σε πραγματικά booleans, διαχείριση διαφόρων μορφών
            is_difficult = str(course['Δύσκολο (TRUE/FALSE)']).strip().upper() in ['TRUE', '1', 'YES', 'T']
            has_lab = str(course['Εργαστήριο (TRUE/FALSE)']).strip().upper() in ['TRUE', '1', 'YES', 'T']

            self.course_info[name] = {
                'semester': int(course['Εξάμηνο']),
                'instructor': str(course['Καθηγητής']),
                'is_difficult': is_difficult,
                'has_lab': has_lab
            }

            if has_lab:
                lab_name = f"{name}_Lab"
                lab_pairs[name] = lab_name
                variables.append(lab_name)
                # Το εργαστήριο κληρονομεί τις πληροφορίες του μαθήματος
                self.course_info[lab_name] = self.course_info[name].copy()

        # Δημιουργία πεδίων (ημέρα, χρονοθυρίδα)
        domains = {}
        for var in variables:
            domains[var] = [(d, s) for d in range(1, 22) for s in range(1, 4)]

        # Αρχικοποίηση γειτόνων
        neighbors = {var: [v for v in variables if v != var] for var in variables}

        # Αρχικοποίηση CSP
        super().__init__(variables, domains, neighbors, self.constraints)
        self.curr_domains = {var: list(domains[var]) for var in variables}

    def constraints(self, A, a, B, b):
        """Επιστρέφει True αν ικανοποιούνται οι περιορισμοί μεταξύ A=a και B=b."""
        # Λήψη πληροφοριών μαθήματος, διαχείριση μεταβλητών συστατικών εργαστηρίου
        course_A = A[:-4] if A.endswith('_Lab') else A
        course_B = B[:-4] if B.endswith('_Lab') else B
        info_A = self.course_info[course_A]
        info_B = self.course_info[course_B]

        day_A, slot_A = a
        day_B, slot_B = b

        # 1. Δεν επιτρέπονται ταυτόχρονες εξετάσεις (διαθέσιμο ένα δωμάτιο)
        if day_A == day_B and slot_A == slot_B:
            return False

        # 2. Περιορισμός ακολουθίας Θεωρίας-Εργαστηρίου (υψηλότερη προτεραιότητα)
        if A.endswith('_Lab'):
            if B == A[:-4]:  # Αυτή είναι η θεωρητική εξέταση για αυτό το εργαστήριο
                return day_A == day_B and slot_A == slot_B + 1
            elif day_A == day_B and slot_A == slot_B:  # Καμία άλλη εξέταση την ίδια ώρα
                return False
        elif B.endswith('_Lab'):
            if A == B[:-4]:  # Αυτή είναι η θεωρητική εξέταση για αυτό το εργαστήριο
                return day_A == day_B and slot_B == slot_A + 1
            elif day_A == day_B and slot_A == slot_B:  # Καμία άλλη εξέταση την ίδια ώρα
                return False

        # Παράκαμψη υπόλοιπων ελέγχων για συστατικά εργαστηρίου με άλλες εξετάσεις
        if A.endswith('_Lab') or B.endswith('_Lab'):
            return True

        # 3. Περιορισμός ίδιου ακαδημαϊκού έτους (εξάμηνο)
        if info_A['semester'] == info_B['semester'] and day_A == day_B:
            return False

        # 4. Περιορισμός απόστασης δύσκολων μαθημάτων
        if info_A['is_difficult'] and info_B['is_difficult']:
            if abs(day_A - day_B) < 2:
                return False

        # 5. Περιορισμός ίδιου καθηγητή
        if info_A['instructor'] == info_B['instructor'] and day_A == day_B:
            return False

        # Ενημέρωση βαρών περιορισμών για την ευρετική dom/wdeg
        self.constraint_weights[(A, B)] += 1
        self.constraint_weights[(B, A)] += 1

        return True

def verify_solution(solution, csp):
    """Επαλήθευση ότι η λύση ικανοποιεί όλους τους περιορισμούς."""
    if not solution:
        print("Δε βρέθηκε λύση!")
        return False

    violations = []
    for A, a in solution.items():
        for B, b in solution.items():
            if A < B:  # Έλεγχος κάθε ζεύγους μία φορά
                if not csp.constraints(A, a, B, b):
                    violations.append((A, B))

    if violations:
        print(f"Προειδοποίηση: Βρέθηκαν {len(violations)} παραβιάσεις περιορισμών!")
        for A, B in violations[:3]:  # Εμφάνιση πρώτων 3 παραβιάσεων
            print(f"Παραβίαση μεταξύ {A} και {B}")
        return False

    print("Επαλήθευση λύσης: Όλοι οι περιορισμοί ικανοποιούνται!")
    return True

def revise(csp, Xi, Xj, removals):
    """Επιστρέφει true αν αφαιρέσουμε μια τιμή από curr_domains[Xi]."""
    revised = False
    for x in csp.curr_domains[Xi][:]:  # Σημείωση: χρήση αντιγράφου λίστας
        # Αν Xi=x συγκρούεται με κάθε πιθανή τιμή στο πεδίο του Xj
        if not any(csp.constraints(Xi, x, Xj, y) for y in csp.curr_domains[Xj]):
            csp.curr_domains[Xi].remove(x)
            if removals is not None:
                removals.append((Xi, x))
            revised = True
    return revised

def mac_inference(csp, var, value, assignment, removals):
    """MAC ως μέθοδος συμπερασμού για αναζήτηση οπισθοδρόμησης."""
    # Πρώτα έλεγχος προώθησης
    if not forward_checking(csp, var, value, assignment, removals):
        return False

    # Στη συνέχεια καθιέρωση συνεκτικότητας τόξου
    queue = [(X, var) for X in csp.neighbors[var]]
    while queue:
        (X, Y) = queue.pop(0)
        if revise(csp, X, Y, removals):
            if not csp.curr_domains[X]:
                return False
            for Z in csp.neighbors[X]:
                if Z != Y:
                    queue.append((Z, X))
    return True

def combined_heuristic_selector(assignment, csp):
    """Συνδυάζει ευρετικές MRV και dom/wdeg για επιλογή μεταβλητών."""
    unassigned = [v for v in csp.variables if v not in assignment]
    if not unassigned:
        return None

    def compute_weight(var):
        return sum(csp.constraint_weights.get((var, n), 1)
                  for n in csp.neighbors[var])

    # Λήψη βαθμολογίας MRV (λιγότερες εναπομένουσες τιμές = υψηλότερη βαθμολογία)
    mrv_scores = {var: 1.0 / len(csp.curr_domains[var]) for var in unassigned}

    # Λήψη βαθμολογίας dom/wdeg (μικρότερο μέγεθος πεδίου / βάρος = υψηλότερη βαθμολογία)
    wdeg_scores = {var: len(csp.curr_domains[var]) / compute_weight(var)
                  for var in unassigned}

    # Κανονικοποίηση βαθμολογιών στο εύρος [0,1]
    max_mrv = max(mrv_scores.values())
    max_wdeg = max(wdeg_scores.values())

    # Συνδυασμός βαθμολογιών (υψηλότερη βαθμολογία = καλύτερη επιλογή)
    return min(unassigned,
              key=lambda var: (wdeg_scores[var] / max_wdeg +
                             mrv_scores[var] / max_mrv))

def schedule_exams_fc(courses):
    """Επίλυση χρονοπρογραμματισμού εξετάσεων με Forward Checking."""
    print("\nΈναρξη αλγορίθμου Forward Checking...")
    csp = ExamSchedulerCSP(courses)
    solution = backtracking_search(
        csp,
        select_unassigned_variable=combined_heuristic_selector,
        inference=forward_checking
    )
    if solution:
        print(f"FC: Βρέθηκε λύση με {len(solution)}/{len(csp.variables)} μεταβλητές")
        verify_solution(solution, csp)
    return solution

def schedule_exams_mac(courses):
    """Επίλυση χρονοπρογραμματισμού εξετάσεων με MAC."""
    print("\nΈναρξη αλγορίθμου MAC...")
    csp = ExamSchedulerCSP(courses)

    def mac(csp, var, value, assignment, removals):
        """MAC ως μέθοδος συμπερασμού."""
        if not forward_checking(csp, var, value, assignment, removals):
            return False

        # Στη συνέχεια καθιέρωση συνεκτικότητας τόξου
        queue = [(X, var) for X in csp.neighbors[var]]
        while queue:
            (X, Y) = queue.pop(0)
            if revise(csp, X, Y, removals):
                if not csp.curr_domains[X]:
                    return False
                for Z in csp.neighbors[X]:
                    if Z != Y:
                        queue.append((Z, X))
        return True

    solution = backtracking_search(
        csp,
        select_unassigned_variable=combined_heuristic_selector,
        order_domain_values=lcv,
        inference=mac
    )
    if solution:
        print(f"MAC: Βρέθηκε λύση με {len(solution)}/{len(csp.variables)} μεταβλητές")
        verify_solution(solution, csp)
    return solution

def schedule_exams_minconflicts(courses, max_steps=1000):
    """Επίλυση χρονοπρογραμματισμού εξετάσεων με Min-Conflicts."""
    print("\nΈναρξη αλγορίθμου Min-Conflicts...")
    csp = ExamSchedulerCSP(courses)

    def conflicts(csp, var, val, assignment):
        """Επιστρέφει τον αριθμό συγκρούσεων που έχει το var=val με άλλες μεταβλητές."""
        count = 0
        for other in csp.neighbors[var]:
            if other in assignment:
                if not csp.constraints(var, val, other, assignment[other]):
                    count += 1
                    # Ενημέρωση βαρών περιορισμών για dom/wdeg
                    csp.constraint_weights[(var, other)] += 1
                    csp.constraint_weights[(other, var)] += 1
        return count

    # Αρχικοποίηση με τυχαία πλήρη ανάθεση
    solution = min_conflicts(csp, max_steps=max_steps)

    if solution:
        print(f"Min-Conflicts: Βρέθηκε λύση με {len(solution)}/{len(csp.variables)} μεταβλητές")
        verify_solution(solution, csp)
    return solution

def format_solution(solution):
    """Μορφοποίηση της λύσης σε αναγνώσιμο πρόγραμμα."""
    schedule = []
    time_slots = ['9:00-12:00', '12:00-15:00', '15:00-18:00']

    for var, (day, slot) in sorted(solution.items()):
        schedule.append({
            'course': var,
            'day': day,  # Διατήρηση 0-based για συνέπεια
            'time': time_slots[slot - 1]  # Μετατροπή 1-based slot σε 0-based index
        })

    return sorted(schedule, key=lambda x: (x['day'], x['time']))

def compare_algorithms(courses):
    """Σύγκριση αλγορίθμων FC, MAC και MinConflicts με λεπτομερείς μετρικές."""
    import time
    results = {}

    def collect_metrics(name, solution, csp, start_time):
        if not solution:
            return {
                'name': name,
                'solution_found': False,
                'time': time.time() - start_time,
                'num_variables': len(csp.variables),
                'num_assigned': 0,
                'constraints_checked': csp.constraint_weights.copy(),
                'violations': [],
                'schedule': None,
                'days_used': 0,
                'slots_used': 0,
                'lab_sequencing_violations': 0,
                'same_day_violations': 0,
                'difficult_course_violations': 0,
                'instructor_violations': 0
            }

        # Ανάλυση παραβιάσεων περιορισμών ανά τύπο
        violations = []
        lab_seq = 0
        same_day = 0
        difficult = 0
        instructor = 0

        for A, a in solution.items():
            for B, b in solution.items():
                if A < B and not csp.constraints(A, a, B, b):
                    violations.append((A, B))
                    # Κατηγοριοποίηση παραβίασης
                    if A.endswith('_Lab') or B.endswith('_Lab'):
                        lab_seq += 1
                    elif csp.course_info[A]['semester'] == csp.course_info[B]['semester']:
                        same_day += 1
                    elif csp.course_info[A]['is_difficult'] and csp.course_info[B]['is_difficult']:
                        difficult += 1
                    elif csp.course_info[A]['instructor'] == csp.course_info[B]['instructor']:
                        instructor += 1

        days_used = len(set(day for day, _ in solution.values()))
        slots_used = len(set((day, slot) for day, slot in solution.values()))

        return {
            'name': name,
            'solution_found': True,
            'time': time.time() - start_time,
            'num_variables': len(csp.variables),
            'num_assigned': len(solution),
            'constraints_checked': csp.constraint_weights.copy(),
            'violations': violations,
            'schedule': format_solution(solution),
            'days_used': days_used,
            'slots_used': slots_used,
            'lab_sequencing_violations': lab_seq,
            'same_day_violations': same_day,
            'difficult_course_violations': difficult,
            'instructor_violations': instructor
        }

    # Δοκιμή Forward Checking
    start = time.time()
    fc_solution = schedule_exams_fc(courses)
    results['Forward Checking'] = collect_metrics('Forward Checking', fc_solution, ExamSchedulerCSP(courses), start)

    # Δοκιμή MAC
    start = time.time()
    mac_solution = schedule_exams_mac(courses)
    results['MAC'] = collect_metrics('MAC', mac_solution, ExamSchedulerCSP(courses), start)

    # Δοκιμή MinConflicts
    start = time.time()
    minconf_solution = schedule_exams_minconflicts(courses)
    results['MinConflicts'] = collect_metrics('MinConflicts', minconf_solution, ExamSchedulerCSP(courses), start)

    return results

if __name__ == '__main__':
    # Φόρτωση μαθημάτων από CSV
    import csv
    import pandas as pd

    df = pd.read_csv('~/attachments/h3-data.csv')
    courses = []

    for _, row in df.iterrows():
        courses.append({
            'name': row['Μάθημα'],
            'semester': row['Εξάμηνο'],
            'instructor': row['Καθηγητής'],
            'is_difficult': row['Δύσκολο (TRUE/FALSE)'],
            'has_lab': row['Εργαστήριο (TRUE/FALSE)']
        })

    # Σύγκριση και των τριών αλγορίθμων
    results = compare_algorithms(courses)

    print("\nΑποτελέσματα Σύγκρισης Αλγορίθμων:")
    for algo, result in results.items():
        print(f"\n{algo}:")
        print(f"Χρόνος εκτέλεσης: {result['time']:.2f} δευτερόλεπτα")
        print(f"Βρέθηκε λύση: {result['solution_found']}")
        if result['schedule']:
            print("\nΠαράδειγμα προγράμματος:")
            for exam in result['schedule'][:5]:  # Εμφάνιση πρώτων 5 εξετάσεων
                print(f"Ημέρα {exam['day']}, {exam['time']}: {exam['course']}")
