from functions.get_files_info import run_python_file


def test() -> None:
    print("Running in calculator: main.py")
    print(run_python_file("calculator", "main.py"))
    print("")

    print("Running in calculator: main.py 3 + 5")
    print(run_python_file("calculator", "main.py", ["3 + 5"]))
    print("")

    print("Running in calculator tests.py")
    print(run_python_file("calculator", "tests.py"))
    print("")

    print("Running calculator ../main.py")
    print(run_python_file("calculator", "../main.py"))
    print("")

    print("Running calculator nonexistent.py")
    print(run_python_file("calculator", "nonexistent.py"))
    print("")

    print("Running calculator lorem.txt")
    print(run_python_file("calculator", "lorem.txt"))
    print("")

if __name__ == "__main__":
    test()
