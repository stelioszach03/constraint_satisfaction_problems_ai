import pandas as pd
from exam_scheduler import *

def analyze_schedule(schedule, course_info):
    """Ανάλυση του προγράμματος εξετάσεων για παραβιάσεις περιορισμών."""
    violations = []

    # Ομαδοποίηση εξετάσεων ανά ημέρα
    exams_by_day = {}
    for exam in schedule:
        day = exam['day']
        if day not in exams_by_day:
            exams_by_day[day] = []
        exams_by_day[day].append(exam)

    # Έλεγχος περιορισμών
    for day, exams in exams_by_day.items():
        # Έλεγχος περιορισμού ίδιας χρονοθυρίδας
        for i, exam1 in enumerate(exams):
            for exam2 in exams[i+1:]:
                if exam1['time'] == exam2['time']:
                    violations.append(f"Ίδια χρονοθυρίδα: {exam1['course']} και {exam2['course']} την ημέρα {day}")

        # Έλεγχος περιορισμού ίδιου εξαμήνου
        semester_groups = {}
        for exam in exams:
            course = exam['course']
            if not course.endswith('_Lab'):
                semester = course_info[course]['semester']
                if semester in semester_groups:
                    violations.append(f"Ίδιο εξάμηνο την ίδια ημέρα: {course} και {semester_groups[semester]}")
                semester_groups[semester] = course

    return violations

# Φόρτωση δεδομένων μαθημάτων
courses = pd.read_csv('~/attachments/h3-data.csv')

print("Έναρξη σύγκρισης αλγορίθμων...")
print(f"Σύνολο μαθημάτων: {len(courses)}")
print(f"Μαθήματα με εργαστήρια: {courses['Εργαστήριο (TRUE/FALSE)'].value_counts()['TRUE']}")
print(f"Δύσκολα μαθήματα: {courses['Δύσκολο (TRUE/FALSE)'].value_counts()['TRUE']}")

# Εκτέλεση αλγορίθμων
results = compare_algorithms(courses.to_dict('records'))

# Ανάλυση αποτελεσμάτων
for algo_name, metrics in results.items():
    print(f"\n=== Ανάλυση {algo_name} ===")
    print(f"Χρόνος εκτέλεσης: {metrics['time']:.3f} δευτερόλεπτα")
    print(f"Εύρεση λύσης: {metrics['solution_found']}")
    print(f"Μεταβλητές που ανατέθηκαν: {metrics['num_assigned']}/{metrics['num_variables']}")

    if metrics['schedule']:
        schedule = metrics['schedule']
        print(f"\nΣτατιστικά Προγράμματος:")
        print(f"Σύνολο ημερών που χρησιμοποιήθηκαν: {metrics['max_day']}")
        print(f"Χρονοθυρίδες που χρησιμοποιήθηκαν: {len(schedule)}")

        # Ανάλυση ακολουθίας εργαστηρίων
        lab_courses = [exam for exam in schedule if exam['course'].endswith('_Lab')]
        print(f"\nΑκολουθία Εργαστηρίων:")
        for lab in lab_courses:
            theory = next((exam for exam in schedule
                         if exam['course'] == lab['course'][:-4]
                         and exam['day'] == lab['day']), None)
            if theory:
                print(f"- {theory['course']}: {theory['time']} -> {lab['course']}: {lab['time']}")
            else:
                print(f"! Μη έγκυρος προγραμματισμός εργαστηρίου για {lab['course']}")

        # Εκτύπωση λεπτομερών παραβιάσεων
        violations = analyze_schedule(schedule, metrics['course_info'])
        if violations:
            print("\nΠαραβιάσεις Περιορισμών:")
            for violation in violations:
                print(f"- {violation}")
