# phoenixia
A repository for phoenix-ia models 
This repository is using Hugging Face's PyTorchModelHubMixin classes

## How to use

```
pip install phoenixia
```

```python
from phoenixia import Hannibal
model = Hannibal(a=2,b=1)
model.push_to_hub(repo_id)

pretrained_model = Hannibal.from_pretrained(repo_id)
```


![pheonixia](https://github.com/not-lain/phoenixia/blob/main/logo.png?raw=true)