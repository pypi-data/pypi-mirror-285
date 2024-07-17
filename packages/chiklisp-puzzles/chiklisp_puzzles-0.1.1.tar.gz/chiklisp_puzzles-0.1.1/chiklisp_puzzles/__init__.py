from klvm_rs import Program


def load_puzzle(puzzle_name: str) -> Program:
    from chiklisp_loader import load_program

    return load_program("chiklisp_puzzles.puzzles", f"{puzzle_name}.hex")
