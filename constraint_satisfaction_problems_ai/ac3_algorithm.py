"""
Υλοποίηση Αλγορίθμου AC-3 για CSP Χρονοπρογραμματισμού
"""
from typing import Dict, List, Set, Tuple
from collections import deque

class AC3Scheduler:
    def __init__(self):
        # Αρχικοποίηση πεδίων τιμών
        self.domains = {
            'A1': {9, 10, 11},
            'A2': {9, 10, 11},
            'A3': {9, 10, 11},
            'A4': {9, 11},     # Δεν μπορεί να ξεκινήσει στις 10:00
            'A5': {9, 10, 11}
        }

        # Αρχικοποίηση περιορισμών ως τόξα (Xi, Xj, συνάρτηση_περιορισμού)
        self.constraints = [
            ('A3', 'A1', lambda x, y: x < y),    # A1 μετά το A3
            ('A5', 'A3', lambda x, y: x < y),    # A3 μετά το A5
            ('A3', 'A4', lambda x, y: x < y),    # A3 πριν το A4
            ('A2', 'A1', lambda x, y: x != y),   # A2 όχι ταυτόχρονα με A1
            ('A2', 'A4', lambda x, y: x != y),   # A2 όχι ταυτόχρονα με A4
        ]

    def revise(self, Xi: str, Xj: str, constraint) -> bool:
        """
        Αναθεώρηση πεδίου τιμών του Xi σε σχέση με το Xj.
        Επιστρέφει True αν το πεδίο τιμών του Xi άλλαξε.
        """
        revised = False
        to_remove = set()

        # Έλεγχος κάθε τιμής στο πεδίο του Xi
        for x in self.domains[Xi]:
            # Αναζήτηση τιμής στο πεδίο του Xj που ικανοποιεί τον περιορισμό
            satisfied = False
            for y in self.domains[Xj]:
                if constraint(x, y):
                    satisfied = True
                    break

            if not satisfied:
                to_remove.add(x)
                revised = True

        # Αφαίρεση τιμών που δεν έχουν υποστήριξη
        self.domains[Xi] -= to_remove
        return revised

    def ac3(self) -> Tuple[bool, Dict[str, Set[int]]]:
        """
        Εκτέλεση αλγορίθμου AC-3 για επίτευξη συνέπειας τόξων.
        Επιστρέφει (επιτυχία, προκύπτοντα_πεδία_τιμών).
        """
        # Αρχικοποίηση ουράς με όλα τα τόξα
        queue = deque([(Xi, Xj, constraint)
                      for Xi, Xj, constraint in self.constraints])

        while queue:
            Xi, Xj, constraint = queue.popleft()

            if self.revise(Xi, Xj, constraint):
                if not self.domains[Xi]:
                    return False, {}  # Άδειο πεδίο, καμία λύση

                # Προσθήκη όλων των τόξων που δείχνουν στο Xi πίσω στην ουρά
                for Xk, Xl, c in self.constraints:
                    if Xl == Xi and Xk != Xj:
                        queue.append((Xk, Xi, c))

        return True, self.domains

    def explain_arc_consistency(self) -> str:
        """
        Παρέχει λεπτομερή εξήγηση της διαδικασίας συνέπειας τόξων.
        """
        consistent, domains = self.ac3()

        explanation = """
Εφαρμογή Αλγορίθμου AC-3 στο CSP Χρονοπρογραμματισμού:

1. Αρχικά Πεδία Τιμών:
   A1: {9, 10, 11}
   A2: {9, 10, 11}
   A3: {9, 10, 11}
   A4: {9, 11}     # Δεν μπορεί να ξεκινήσει στις 10:00
   A5: {9, 10, 11}

2. Περιορισμοί (Τόξα):
   α) A3 → A1: Έναρξη(A1) > Έναρξη(A3)
   β) A5 → A3: Έναρξη(A3) > Έναρξη(A5)
   γ) A3 → A4: Έναρξη(A4) > Έναρξη(A3)
   δ) A2 ↔ A1: Έναρξη(A2) ≠ Έναρξη(A1)
   ε) A2 ↔ A4: Έναρξη(A2) ≠ Έναρξη(A4)

3. Διαδικασία AC-3:
"""
        if consistent:
            explanation += """
   Αποτέλεσμα: Επιτεύχθηκε Συνέπεια Τόξων!

   Τελικά Πεδία Τιμών μετά το AC-3:"""
            for var, domain in sorted(domains.items()):
                explanation += f"\n   {var}: {sorted(domain)}"

            explanation += """

4. Εξήγηση Μείωσης Πεδίων Τιμών:
   - Το A5 πρέπει να είναι πριν το A3: Το A5 δεν μπορεί να είναι 11:00
   - Το A3 πρέπει να είναι μετά το A5 και πριν τα A1,A4: Το A3 δεν μπορεί να είναι 11:00
   - Το A1 πρέπει να είναι μετά το A3: Το A1 δεν μπορεί να είναι 9:00
   - Το A4 πρέπει να είναι μετά το A3 και όχι 10:00
   - Το A2 δεν μπορεί να συμπίπτει με τα A1 ή A4

5. Παράδειγμα Έγκυρης Λύσης:
   A5: 9:00
   A3: 10:00
   A1: 11:00
   A4: 11:00
   A2: 10:00"""
        else:
            explanation += """
   Αποτέλεσμα: Δεν υπάρχει Λύση με Συνέπεια Τόξων!
   Οι περιορισμοί είναι υπερβολικά περιοριστικοί."""

        return explanation

if __name__ == "__main__":
    scheduler = AC3Scheduler()
    print(scheduler.explain_arc_consistency())
