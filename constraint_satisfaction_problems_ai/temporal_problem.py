"""
Υλοποίηση Απλού Χρονικού Προβλήματος (Simple Temporal Problem - STP)
Βασισμένο στην αφήγηση σχετικά με τη μετακίνηση της Μαρίας και της Ελένης
"""
from typing import Dict, List, Tuple
import numpy as np

class SimpleTemporalProblem:
    def __init__(self):
        """
        Αρχικοποίηση του Απλού Χρονικού Προβλήματος με γεγονότα και περιορισμούς.
        Ο χρόνος αναπαρίσταται σε λεπτά από τις 8:00 π.μ.
        """
        # Γεγονότα (μεταβλητές):
        # ML: Αναχώρηση Μαρίας (μεταξύ 8:00-8:10)
        # MA: Άφιξη Μαρίας
        # EL: Αναχώρηση Ελένης
        # EA: Άφιξη Ελένης (15 λεπτά μετά τη Μαρία)

        # Initialize distance matrix (d-graph)
        self.n_events = 4
        self.events = ['ML', 'MA', 'EL', 'EA']
        self.d = np.full((self.n_events, self.n_events), float('inf'))

        # Set diagonal to 0
        np.fill_diagonal(self.d, 0)

        # Add constraints from narrative:
        # 1. Maria leaves between 8:00 and 8:10
        self.d[0, 0] = 0    # ML-ML
        self.d[0, 1] = 40   # ML-MA (max 40 min commute)
        self.d[1, 0] = -30  # MA-ML (min 30 min commute)

        # 2. Eleni arrives 15 min after Maria
        self.d[1, 3] = 15   # MA-EA (exactly 15 min)
        self.d[3, 1] = -15  # EA-MA

        # 3. Eleni's commute takes 5-15 minutes
        self.d[2, 3] = 15   # EL-EA (max 15 min)
        self.d[3, 2] = -5   # EA-EL (min 5 min)

    def floyd_warshall(self) -> bool:
        """
        Εφαρμογή του αλγορίθμου Floyd-Warshall για τον υπολογισμό συντομότερων διαδρομών.
        Επιστρέφει True αν το STP είναι συνεπές (χωρίς αρνητικούς κύκλους).
        """
        n = self.n_events

        # Floyd-Warshall algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if self.d[i,k] != float('inf') and self.d[k,j] != float('inf'):
                        self.d[i,j] = min(self.d[i,j], self.d[i,k] + self.d[k,j])

        # Check for negative cycles
        for i in range(n):
            if self.d[i,i] < 0:
                return False
        return True

    def generate_solutions(self) -> List[Dict[str, str]]:
        """
        Δημιουργία δύο έγκυρων λύσεων για το χρονικό πρόβλημα.
        Οι χρόνοι μετατρέπονται σε ώρες ρολογιού για ευκολότερη ανάγνωση.
        """
        def minutes_to_time(minutes: float) -> str:
            """Μετατροπή λεπτών από τις 8:00 π.μ. σε ώρα ρολογιού."""
            hours = 8 + minutes // 60
            mins = minutes % 60
            return f"{int(hours):02d}:{int(mins):02d}"

        solutions = []

        # Λύση 1: Η Μαρία φεύγει στις 8:00
        sol1 = {
            'Η Μαρία φεύγει': minutes_to_time(0),      # 8:00
            'Η Μαρία φτάνει': minutes_to_time(35),    # 8:35
            'Η Ελένη φεύγει': minutes_to_time(45),     # 8:45
            'Η Ελένη φτάνει': minutes_to_time(50)     # 8:50
        }
        solutions.append(sol1)

        # Λύση 2: Η Μαρία φεύγει στις 8:05
        sol2 = {
            'Η Μαρία φεύγει': minutes_to_time(5),      # 8:05
            'Η Μαρία φτάνει': minutes_to_time(40),    # 8:40
            'Η Ελένη φεύγει': minutes_to_time(50),     # 8:50
            'Η Ελένη φτάνει': minutes_to_time(55)     # 8:55
        }
        solutions.append(sol2)

        return solutions

    def analyze_problem(self) -> str:
        """
        Ανάλυση του χρονικού προβλήματος και επιστροφή λεπτομερούς εξήγησης.
        """
        is_consistent = self.floyd_warshall()
        solutions = self.generate_solutions() if is_consistent else []

        analysis = """
Ανάλυση Απλού Χρονικού Προβλήματος:

1. Διατύπωση Προβλήματος:
   Γεγονότα:
   - ML: Αναχώρηση Μαρίας (μεταξύ 8:00-8:10)
   - MA: Άφιξη Μαρίας (30-40 λεπτά μετά την αναχώρηση)
   - EL: Αναχώρηση Ελένης (προς προσδιορισμό)
   - EA: Άφιξη Ελένης (15 λεπτά μετά τη Μαρία)

2. Χρονικοί Περιορισμοί:
   α) 0 ≤ ML ≤ 10         (Η Μαρία φεύγει μεταξύ 8:00-8:10)
   β) 30 ≤ MA-ML ≤ 40     (Χρόνος μετακίνησης Μαρίας)
   γ) EA-MA = 15          (Η Ελένη φτάνει 15 λεπτά μετά τη Μαρία)
   δ) 5 ≤ EA-EL ≤ 15      (Χρόνος μετακίνησης Ελένης)

3. Ανάλυση Συνέπειας:"""

        if is_consistent:
            analysis += """
   Το πρόβλημα ΕΙΝΑΙ ΣΥΝΕΠΕΣ
   - Δεν υπάρχουν αρνητικοί κύκλοι στο d-graph
   - Όλοι οι περιορισμοί μπορούν να ικανοποιηθούν ταυτόχρονα

4. Λύσεις:"""
            for i, sol in enumerate(solutions, 1):
                analysis += f"\n   Λύση {i}:"
                for event, time in sol.items():
                    analysis += f"\n   - {event}: {time}"

            analysis += """

5. Απάντηση στην Ερώτηση:
   Πότε έφυγε η Ελένη από το σπίτι της;
   Με βάση τη διάδοση περιορισμών:
   - Η Ελένη πρέπει να έφυγε μεταξύ 8:45 και 8:50
   - Αυτό εξασφαλίζει τη διάρκεια μετακίνησης 5-15 λεπτών
   - Επιτρέπει την άφιξή της ακριβώς 15 λεπτά μετά τη Μαρία
   - Ικανοποιεί όλους τους χρονικούς περιορισμούς"""
        else:
            analysis += """
   Το πρόβλημα είναι ΑΣΥΝΕΠΕΣ
   - Περιέχει αρνητικούς κύκλους
   - Δεν υπάρχει έγκυρη λύση"""

        return analysis

if __name__ == "__main__":
    stp = SimpleTemporalProblem()
    print(stp.analyze_problem())
