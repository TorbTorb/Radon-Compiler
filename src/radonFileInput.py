def readFiletoStr() -> tuple[str,str]:
    source = ""
    with open("test.rd") as file:
        source = file.read()
    return source, "test"
