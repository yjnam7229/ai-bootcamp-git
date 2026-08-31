# 학생 클래스를 생성
class Student:
    def study(self):
        print("공부합니다")
    # def __init__(self):
    #     pass

# Teacher 클래스를 생성
class Teacher:
    def teach(self):
        print("학생을 가르칩니다")

# 교실내부의 객체 리스트를 생성
classRom = [Student(), Student(), Teacher(), Student(), Student()]  # 리스트 내부에 여러종류의 인스턴스가 선언되었을 때

# 반복을 이용하면서 적절한 함수를 호출
for person in classRom:
    if isinstance(person, Student):
        person.study()
    elif isinstance(person, Teacher):
        person.teach()
        


