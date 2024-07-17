# mijoon_cmd
## install
```
$ pip install mijoon_cmd
```

## Usage
### zsh
```
$ t_cmd p 5 3

8

$ t_cmd m 5 3

15

$ t_cmd d 10 5

2.0

```

### Python
```py
from mijoon_cmd.cmd import p # 더하기
from mijoon_cmd.cmd import m # 곱하기
from mijoon_cmd.cmd import d # 나누기
p(a,b)
# result = a+b

m(a,b)
# result = a*b

d(a,b)
# result = a/b

```

## Dependencies
```
team_plus
team_mul
team_divide
```
