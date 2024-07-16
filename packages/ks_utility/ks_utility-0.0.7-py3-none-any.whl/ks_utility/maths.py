from sympy import sympify

def cal_exp(exp, values):
    # 将表达式字符串转换为 SymPy 表达式
    expression = sympify(exp)
    expression = expression.subs(values)
    result = expression.evalf()
    return result
# t = cal_exp('a+b+c', {'a': 1, 'b': 2, 'c': 3})