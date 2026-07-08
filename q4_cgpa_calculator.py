# ==========================================
#        STUDENT CGPA CALCULATOR
# ==========================================

def get_grade_point(mark):
    if mark >= 90:
        return 10
    elif mark >= 80:
        return 9
    elif mark >= 70:
        return 8
    elif mark >= 60:
        return 7
    elif mark >= 50:
        return 6
    else:
        return 0


def get_classification(cgpa):
    if cgpa >= 9:
        return "Outstanding"
    elif cgpa >= 8:
        return "First Class with Distinction"
    elif cgpa >= 7:
        return "First Class"
    elif cgpa >= 6:
        return "Second Class"
    elif cgpa >= 5:
        return "Pass"
    else:
        return "Fail"


student_name = input("Enter Student Name: ")
register_no = input("Enter Register Number: ")

num_semesters = int(input("Enter Number of Semesters: "))

semester_sgpas = []

print("\n========== CGPA CALCULATION ==========\n")

for sem in range(1, num_semesters + 1):

    print(f"\nSemester {sem}")

    subjects = int(input("Enter Number of Subjects: "))

    total_credits = 0
    total_credit_points = 0

    print("\nEnter Subject Details")

    for i in range(1, subjects + 1):

        subject = input(f"\nSubject {i} Name: ")

        marks = float(input("Marks: "))

        credit = float(input("Credit: "))

        grade_point = get_grade_point(marks)

        credit_point = grade_point * credit

        total_credits += credit
        total_credit_points += credit_point

        print("Grade Point:", grade_point)

    sgpa = total_credit_points / total_credits

    semester_sgpas.append(sgpa)

    print("\nSemester", sem, "SGPA =", round(sgpa, 2))

cgpa = sum(semester_sgpas) / len(semester_sgpas)

print("\n===================================")
print("STUDENT RESULT")
print("===================================")
print("Student Name :", student_name)
print("Register No  :", register_no)

print("\nSemester-wise SGPA")
for i in range(len(semester_sgpas)):
    print("Semester", i + 1, ":", round(semester_sgpas[i], 2))

print("\nFinal CGPA :", round(cgpa, 2))
print("Classification :", get_classification(cgpa))
print("===================================")