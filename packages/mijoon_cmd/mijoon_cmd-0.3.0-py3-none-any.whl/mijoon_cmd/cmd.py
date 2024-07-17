import sys
from team_plus.t_plus import plus
from team_mul.mul import mul
from team_divide.div import div
def p(j,k):
    plus(j,k)
def m(j,k):
    mul(j,k)
def d(j,k):
    div(j,k)
def main():
    cal = sys.argv[1]
    b = int(sys.argv[2])
    c = int(sys.argv[3])
    if cal == "p":
        p(b,c)
    elif cal == "m":
        m(b,c)
    else:
        d(b,c)
if __name__ == "__main__":
    main()
