# 여러 개의 데이터를 담을 수 있는 내가 만든 자료형을 클래스라 정의한다
# 클래스를 선언합니다. 표를 만든다
# 객체 : 만들어진 클래스에 실제 데이터를 담아두는 것
# 객체지향(Object Orientied Programming)

# 생성자 함수 호출
# 1. 클래스를 찾는다
# 2. __init__() 호출
# 3. 메모리 할당(매개변수 선언해서 정의)
# 4. 입력으로 전달하고 있는 self라는 매개변수에 시작주소 값을 저장해줌, self는 할당된 메모리의 시작주소 값이 됨 (self. 하는 순간 데이터를 저장할 수 있음)
# 5. 할당한 주소값을 가지고 복귀 
##   할당된 메모리 공간(주소) : 인스턴스 = Object
##   인스턴스 변수
##   클래스 안에 선언된 함수 : 멤버함수(member함수) = 메서드(method)
##   클래스 안에 선언된 변수 : 멤버변수

class Students:
    def __init__(self, name, korean, math, engish, science):  # 매개변수 반드시 선언, 파이썬에 의해 호출되는 콜백 함수
        self.name = name
        self.korean = korean
        self.math = math
        self.engish = engish
        self.science = science

    # 총점 계산
    def get_sum(self):
        return self.korean + self.math + self.engish + self.science
    
    # 평균 계산
    def get_average(self):
        return self.get_sum() / 4
    
    # 출력
    def to_string(self):
        return f"이름:{self.name} {self.get_sum()}\t {self.get_average()}"
        # return f"이름:{self.name}\t 총점:{self.get_sum}\t 평균:{self.get_average}"
    
# 학생을 선언합니다
# students = Students()  # 반드시 클래스의 이름와 동일하게 호출(생성자 함수) __init__()함수 호출

# hongildong = Students("홍길동", 90, 79, 95, 80)  # 생성자 함수 호출
# print(f"이름 : {hongildong.name}")
# print(f"국어점수 : {hongildong.korean}")
# print(f"수학점수 : {hongildong.math}")
# print(f"영어점수 : {hongildong.engish}")
# print(f"과학점수 : {hongildong.science}")

# younghee = Students("이영희", 90, 79, 95, 80)  # 생성자 함수 호출
# print(f"이름 : {younghee.name}")
# print(f"국어점수 : {younghee.korean}")
# print(f"수학점수 : {younghee.math}")
# print(f"영어점수 : {younghee.engish}")
# print(f"과학점수 : {younghee.science}")

# younghee.name = "오영희"
# print(f"이름 : {younghee.name}")

# students = [hongildong, younghee]
# 학생 리스트를 선언합니다.
stuents = [
           Students("홍길동", 90, 79, 95, 80),
           Students("이영희", 90, 79, 95, 80),
]

# 개별적 접근 방법
# print(f"홍길동 국어점수 : {stuents[0].korean}")

# 인스턴스 확인
# print(f"isIncstance(student, Student) {isinstance(student, Student)}")

print("-" * 70)
print("이름", "국어점수", "수학점수", "영어점수", "과학점수", sep="\t")
print("-" * 70)

# # 학생을 한 명씩 반복합니다.
for student in stuents:
    print(f"{student.name}\t    {student.korean}\t    {student.math}\t    {student.engish}\t    {student.science}")
    # print(str(student))

print(f"총점 : {stuents[0].get_sum()}")
print(f"평균 : {stuents[0].get_average()}")
print(stuents[0].to_string())