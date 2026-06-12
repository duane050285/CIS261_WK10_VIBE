# Duane Spurgeon
# CIS261
# VIBE Coding

import json
from pathlib import Path
from typing import List, Optional

DATA_FILE = Path("students.json")

LETTER_GRADES = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


def calculate_letter_grade(average: float) -> str:
    for threshold, grade in LETTER_GRADES:
        if average >= threshold:
            return grade
    return "F"


def normalize_scores(scores: Optional[List[float]]) -> List[float]:
    if scores is None:
        return [0.0, 0.0, 0.0]
    normalized = [float(score) for score in scores][:3]
    normalized += [0.0] * (3 - len(normalized))
    return normalized


class Student:
    def __init__(self, student_id: str, name: str, scores: Optional[List[float]] = None):
        self.student_id = student_id.strip()
        self.name = name.strip()
        self.scores = normalize_scores(scores)
        self.average = 0.0
        self.grade = ""
        self.update_average_and_grade()

    def update_average_and_grade(self) -> None:
        self.average = sum(self.scores) / 3.0
        self.grade = calculate_letter_grade(self.average)

    def set_scores(self, scores: List[float]) -> None:
        self.scores = normalize_scores(scores)
        self.update_average_and_grade()

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "scores": self.scores,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        return cls(
            student_id=data.get("student_id", ""),
            name=data.get("name", ""),
            scores=data.get("scores", []),
        )


class StudentManager:
    def __init__(self):
        self.students: List[Student] = []
        self.load()

    def load(self) -> None:
        if not DATA_FILE.exists():
            return
        try:
            data = json.loads(DATA_FILE.read_text())
            self.students = [StudentRecord.from_dict(item) for item in data]
        except (json.JSONDecodeError, IOError):
            self.students = []

    def save(self) -> None:
        DATA_FILE.write_text(json.dumps([student.to_dict() for student in self.students], indent=2))

    def add_student(self, student_id: str, name: str, scores: List[float]) -> Student:
        student = Student(student_id=student_id, name=name, scores=scores)
        self.students.append(student)
        self.save()
        return student

    def find_student(self, student_id: str) -> Optional[StudentRecord]:
        normalized_id = student_id.strip().lower()
        for student in self.students:
            if student.student_id.lower() == normalized_id:
                return student
        return None

    def list_students(self) -> List[StudentRecord]:
        return list(self.students)

    def print_student_report(self, student: Student) -> None:
        print("\nname|id|test1|test2|test3|average|grade")
        print(
            f"{student.name}|{student.student_id}|"
            f"{student.scores[0]:.1f}|{student.scores[1]:.1f}|{student.scores[2]:.1f}|"
            f"{student.average:.2f}|{student.grade}"
        )
        print()

    def remove_student(self, student_id: str) -> bool:
        student = self.find_student(student_id)
        if student:
            self.students.remove(student)
            self.save()
            return True
        return False


def prompt_score(test_number: int) -> float:
    while True:
        try:
            value = float(input(f"Enter Test {test_number} score (0-100): ").strip())
            if 0 <= value <= 100:
                return value
            print("Score must be between 0 and 100.")
        except ValueError:
            print("Please enter a numeric value.")


def prompt_three_scores() -> List[float]:
    return [prompt_score(i) for i in range(1, 4)]


def main_menu() -> None:
    manager = StudentManager()

    while True:
        print("\nStudent Records Manager")
        print("1. Add student")
        print("2. Update test scores")
        print("3. View student report")
        print("4. List all students")
        print("5. Remove student")
        print("6. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            student_id = input("Student ID: ").strip()
            if not student_id:
                print("Student ID cannot be blank.")
                continue
            name = input("Student name: ").strip()
            if not name:
                print("Student name cannot be blank.")
                continue
            if manager.find_student(student_id):
                print(f"A student with ID '{student_id}' already exists.")
                continue
            scores = prompt_three_scores()
            manager.add_student(student_id, name, scores)
            print(f"Added student {name} ({student_id}) with test scores.")

        elif choice == "2":
            student_id = input("Student ID: ").strip()
            student = manager.find_student(student_id)
            if not student:
                print(f"Student with ID '{student_id}' not found.")
                continue
            scores = prompt_three_scores()
            student.set_scores(scores)
            manager.save()
            print(f"Updated scores for {student.name}.")

        elif choice == "3":
            student_id = input("Student ID: ").strip()
            student = manager.find_student(student_id)
            if not student:
                print(f"Student with ID '{student_id}' not found.")
                continue
            manager.print_student_report(student)

        elif choice == "4":
            students = manager.list_students()
            if not students:
                print("No students available.")
                continue
            print("\nAll Students")
            for student in students:
                print(f"- {student.name} ({student.student_id}): {student.average:.2f} {student.letter_grade}")

        elif choice == "5":
            student_id = input("Student ID to remove: ").strip()
            if manager.remove_student(student_id):
                print(f"Removed student with ID {student_id}.")
            else:
                print(f"Student with ID '{student_id}' not found.")

        elif choice == "6":
            print("Goodbye.")
            break

        else:
            print("Please select a valid option.")


if __name__ == "__main__":
    main_menu()
