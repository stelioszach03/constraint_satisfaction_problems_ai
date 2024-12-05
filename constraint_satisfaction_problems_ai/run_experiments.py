import time
import pandas as pd
import numpy as np
from exam_scheduler import *

def run_experiment_trials(courses, num_trials=10):
    """Εκτέλεση πολλαπλών δοκιμών κάθε αλγορίθμου και συλλογή μετρικών."""
    all_results = []

    for trial in range(num_trials):
        print(f"\nΔοκιμή {trial + 1}/{num_trials}")
        results = compare_algorithms(courses)

        for algo_name, metrics in results.items():
            metrics['trial'] = trial
            all_results.append(metrics)

    return pd.DataFrame(all_results)

def analyze_results(df):
    """Ανάλυση και παρουσίαση πειραματικών αποτελεσμάτων."""
    # Ομαδοποίηση ανά αλγόριθμο
    grouped = df.groupby('name')

    # Υπολογισμός στατιστικών
    stats = pd.DataFrame({
        'Ποσοστό Επιτυχίας (%)': grouped['solution_found'].mean() * 100,
        'Μέσος Χρόνος (s)': grouped['time'].mean(),
        'Τυπική Απόκλιση Χρόνου (s)': grouped['time'].std(),
        'Μέσος Αριθμός Ημερών': grouped['days_used'].mean(),
        'Μέσος Αριθμός Χρονοθυρίδων': grouped['slots_used'].mean(),
        'Μέσος Αριθμός Παραβιάσεων': grouped.apply(lambda x: x['violations'].str.len().mean(), include_groups=False),
        'Μέσος Αριθμός Παραβιάσεων Εργαστηρίων': grouped['lab_sequencing_violations'].mean(),
        'Μέσος Αριθμός Παραβιάσεων Ίδιας Ημέρας': grouped['same_day_violations'].mean(),
        'Μέσος Αριθμός Παραβιάσεων Δύσκολων Μαθημάτων': grouped['difficult_course_violations'].mean(),
        'Μέσος Αριθμός Παραβιάσεων Καθηγητών': grouped['instructor_violations'].mean()
    })

    return stats.round(2)

if __name__ == "__main__":
    # Φόρτωση δεδομένων μαθημάτων με συγκεκριμένους τύπους δεδομένων
    courses = pd.read_csv('~/attachments/h3-data.csv', dtype={
        'Δύσκολο (TRUE/FALSE)': str,
        'Εργαστήριο (TRUE/FALSE)': str
    })

    # Μετατροπή συμβολοσειρών boolean σε πραγματικά boolean
    courses['is_difficult'] = courses['Δύσκολο (TRUE/FALSE)'].str.strip().str.upper() == 'TRUE'
    courses['has_lab'] = courses['Εργαστήριο (TRUE/FALSE)'].str.strip().str.upper() == 'TRUE'

    courses_dict = courses.to_dict('records')

    print("Έναρξη πειραματικής σύγκρισης...")
    print(f"Σύνολο μαθημάτων: {len(courses)}")
    print(f"Δύσκολα μαθήματα: {courses['is_difficult'].sum()}")
    print(f"Μαθήματα με εργαστήριο: {courses['has_lab'].sum()}")
    print(f"Μοναδικοί καθηγητές: {courses['Καθηγητής'].nunique()}")
    print(f"Εξάμηνα: {sorted(courses['Εξάμηνο'].unique())}")

    # Εκτέλεση πειραμάτων
    results_df = run_experiment_trials(courses_dict)

    # Ανάλυση και εμφάνιση αποτελεσμάτων
    print("\nΠειραματικά Αποτελέσματα:")
    print("=" * 80)
    stats = analyze_results(results_df)
    print("\nΜετρικές Απόδοσης Αλγορίθμων:")
    print(stats.to_string())

    # Αποθήκευση αποτελεσμάτων
    results_df.to_csv('experiment_results.csv', index=False)
    stats.to_csv('algorithm_comparison.csv')

    print("\nΛεπτομερή αποτελέσματα αποθηκεύτηκαν στο 'experiment_results.csv'")
    print("Συνοπτικά στατιστικά αποθηκεύτηκαν στο 'algorithm_comparison.csv'")
