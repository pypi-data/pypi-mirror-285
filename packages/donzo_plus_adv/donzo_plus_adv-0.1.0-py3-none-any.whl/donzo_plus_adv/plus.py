import sys

def main():
    # 스크립트 실행 시 받은 인자들
    args = sys.argv[1:]  # 첫 번째 인자는 스크립트 자체의 이름이므로 제외합니다.

    # 여기서 인자값을 계산하거나 처리할 수 있습니다.
    if len(args) < 2:
        print("적어도 두 개의 인자가 필요합니다.")
        return

    arg1 = args[0]
    arg2 = args[1]

    # 계산 예시: 두 개의 인자를 더합니다.
    result = int(arg1) + int(arg2)
    print(f"두 수의 합: {result}")

if __name__ == "__main__":
    main()
