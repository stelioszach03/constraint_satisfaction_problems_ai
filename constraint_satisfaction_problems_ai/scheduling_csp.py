"""
Υλοποίηση CSP Προβλήματος Χρονοπρογραμματισμού
5 ενέργειες (A1-A5) με χρονικούς περιορισμούς
"""
from typing import Dict, List, Set, Tuple

class SchedulingCSP:
    def __init__(self):
        # Μεταβλητές: Ενέργειες A1-A5
        self.actions = ['A1', 'A2', 'A3', 'A4', 'A5']

        # Πεδίο: Πιθανοί χρόνοι έναρξης (9:00, 10:00, 11:00)
        self.domain = {
            action: {9, 10, 11} for action in self.actions
        }
        # Η A4 δεν μπορεί να ξεκινήσει στις 10:00
        self.domain['A4'].remove(10)

    def get_constraints(self) -> List[str]:
        """Επιστρέφει τους τυπικούς περιορισμούς CSP."""
        return [
            "# Μεταβλητές:",
            "Ενέργειες = {A1, A2, A3, A4, A5}",
            "Πεδίο = {9, 10, 11} (αναπαριστά ώρες έναρξης)",
            "",
            "# Χρονικοί Περιορισμοί:",
            "1. Έναρξη(A1) > Έναρξη(A3)  # A1 μετά την A3",
            "2. Έναρξη(A3) < Έναρξη(A4)  # A3 πριν την A4",
            "3. Έναρξη(A3) > Έναρξη(A5)  # A3 μετά την A5",
            "4. Έναρξη(A2) ≠ Έναρξη(A1)  # A2 όχι ταυτόχρονα με A1",
            "5. Έναρξη(A2) ≠ Έναρξη(A4)  # A2 όχι ταυτόχρονα με A4",
            "6. Έναρξη(A4) ≠ 10         # A4 δεν μπορεί να ξεκινήσει στις 10:00",
            "",
            "# Περιορισμοί Πεδίου:",
            "∀a ∈ Ενέργειες: Έναρξη(a) ∈ {9, 10, 11}",
            "",
            "# Πρόσθετοι Παράγωγοι Περιορισμοί:",
            "Από 1,2,3: Έναρξη(A5) < Έναρξη(A3) < Έναρξη(A4) ∧ Έναρξη(A3) < Έναρξη(A1)",
            "Από 4,5: Έναρξη(A2) ∉ {Έναρξη(A1), Έναρξη(A4)}",
        ]

    def verify_solution(self, assignment: Dict[str, int]) -> Tuple[bool, List[str]]:
        """
        Επαλήθευση αν μια λύση ικανοποιεί όλους τους περιορισμούς.
        Επιστρέφει (είναι_έγκυρη, παραβιάσεις).
        """
        violations = []

        # Έλεγχος περιορισμών χρονικής διάταξης
        if assignment['A1'] <= assignment['A3']:
            violations.append("Παραβίαση: Η A1 πρέπει να ξεκινήσει μετά την A3")

        if assignment['A3'] >= assignment['A4']:
            violations.append("Παραβίαση: Η A3 πρέπει να ξεκινήσει πριν την A4")

        if assignment['A3'] <= assignment['A5']:
            violations.append("Παραβίαση: Η A3 πρέπει να ξεκινήσει μετά την A5")

        # Έλεγχος περιορισμών μη-ταυτοχρονισμού
        if assignment['A2'] == assignment['A1']:
            violations.append("Παραβίαση: Η A2 δεν μπορεί να συμβεί ταυτόχρονα με την A1")

        if assignment['A2'] == assignment['A4']:
            violations.append("Παραβίαση: Η A2 δεν μπορεί να συμβεί ταυτόχρονα με την A4")

        # Έλεγχος χρονικού περιορισμού A4
        if assignment['A4'] == 10:
            violations.append("Παραβίαση: Η A4 δεν μπορεί να ξεκινήσει στις 10:00")

        return len(violations) == 0, violations

    def example_solution(self) -> Dict[str, int]:
        """
        Επιστρέφει ένα παράδειγμα έγκυρης λύσης.
        """
        solution = {
            'A5': 9,   # Πρώτη ενέργεια
            'A3': 10,  # Μετά την A5, πριν τις A1 και A4
            'A1': 11,  # Μετά την A3
            'A4': 11,  # Μετά την A3, όχι στις 10:00
            'A2': 10   # Διαφορετική ώρα από A1 και A4
        }

        is_valid, violations = self.verify_solution(solution)
        if not is_valid:
            raise ValueError(f"Μη έγκυρη λύση! Παραβιάσεις: {violations}")

        return solution

if __name__ == "__main__":
    csp = SchedulingCSP()

    print("Μοντέλο CSP Χρονοπρογραμματισμού:")
    print("============================")
    print("\nΤυπικοί Περιορισμοί:")
    for constraint in csp.get_constraints():
        print(constraint)

    print("\nΠαράδειγμα Έγκυρης Λύσης:")
    solution = csp.example_solution()
    print("\nΧρόνοι Έναρξης:")
    for action, time in solution.items():
        print(f"{action}: {time}:00")

    is_valid, violations = csp.verify_solution(solution)
    print(f"\nΗ λύση είναι {'έγκυρη' if is_valid else 'μη έγκυρη'}")
    if violations:
        print("Παραβιάσεις:", violations)
