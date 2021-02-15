from yacc import parse

def dfs(ast):
    if type(ast) != tuple:
        return
    else:
        for i in ast:
            dfs(i)

    print(ast)


if __name__ == '__main__':
    dfs(parse('test.erb'))
