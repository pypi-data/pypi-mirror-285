# banner_j25ng

```
       _ ___   ______
      (_)__ \ / ____/___  ____ _
     / /__/ //___ \/ __ \/ __ `/
    / // __/____/ / / / / /_/ /
 __/ //____/_____/_/ /_/\__, /
/___/                  /____/
```

# Usage
## source code : banner.py
```
from pyfiglet import Figlet

def show():
    f = Figlet(font='slant')
    print(f.renderText('j25ng'))
```

## add pyproject.toml option
```
[project.scripts]
show-banner = 'banner_j25ng.banner:show'
```

## install
```
pip install
```

## on shell
```
show-banner
```
