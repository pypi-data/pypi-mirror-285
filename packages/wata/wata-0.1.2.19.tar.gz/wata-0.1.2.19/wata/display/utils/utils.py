


def wataprint(content,type):
    color_map = {
        "r_": "\x1b[1;4;31m{}\x1b[0m",
        "b": "\x1b[36m{}\x1b[0m",
        "r": "\x1b[1;31m{}\x1b[0m",
        "g": "\x1b[32m{}\x1b[0m",
        "p": "\x1b[35m{}\x1b[0m"
    }
    print(color_map[type].format(content))