# module_example 폴더 test_module.py

PI = 3.141592

def number_input():
    output = input("숫자 입력> ")
    return float(output)

def get_circumference(radius):
    return 2 * PI * radius

def get_circle_area(radius):
    return PI * radius * radius


# 모듈의 실행여부 체크, main.py 실행시에는 16라인의 if 조건에 해당 되지 않음
if __name__ == "__main__":   # 모듈에서는 필요없는 부분 기능을 체크하기 위해 테스트 단계에서는 실행이 됨, main.py를 실행하면 __name__ 은 test_module이 되어서 16라인은 실행이 되지 않은
    # 활용 예 
    print("get_circumference(10):", get_circumference(10))
    print("get_circle_area(10): ", get_circle_area(10))