if __name__ == "__main__":
    string = "Og dagens tal er _{TAL} og TAL"
    replace_dict = {"TAL" : 1}

    print(string.format(**replace_dict))
