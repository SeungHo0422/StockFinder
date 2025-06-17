# 트러블슈팅 기록

1. pytest importError
### 문제 상황
tests/data/test_collector.py를 테스트 실행하니, from src.data ~~ 에서 importError가 발생했다.

### 해결 방법
'.venv': venv 환경에서 진행했고, test_collector.py에 system에 수동으로 루트 경로를 지정해주는 방식으로 해결했다.

```python
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
from src.data import collector
```

왜 됐는지는 모르겠다. pytest.ini 에 프로젝트 루트 경로를 띄워줘도 안되는데 이렇게 수동으로 지정해줘야만 되는 게 찜찜하다.