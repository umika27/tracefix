from runner import run_safely

@run_safely
def test():
    x = 10 + "hello"

test()
