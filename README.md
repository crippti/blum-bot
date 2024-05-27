# Blum Drop Game Bot
Bot emulates playing Drop Game in Blum using Blum API.
Can farm points in multiple telegram accounts.

## Installation
Download Python 3.12 and install the bot from root folder of project.
```python
pip install .
```

## Usage
### Obtaining JWT token
1) Open Telegram Web, open Google Chrome DevTools, go to Network tab.
2) Open Blum app in Telegram Web and find in Network any request to Blum. For example balance.
3) There are will be `Authorization` header containing JWT token in headers. 
![](./docs/screen.png)

### Config file
Setup `yaml` file like this:

```yaml
min_points: 240
max_points: 270

telegrams:
  - jwt_token: "Bearer eyJ...."
#    proxy: "http://user:password@host:port"
#  - jwt_token: "Bearer eyJ...."
#    proxy: "https://user:password@host:port"

cpu_count: 12
```

- cpu_count: Count of cpus. Do not add this parameter to set cpu count to auto.
- min_points: Minimal value of random number of points that will be applied.  
- max_points: Maximum value of random number of points that will be applied. Must be not greater than 270.
- telegrams: settings for telegram accounts.
  - jwt_token: Token in format like "Bearer ..."
  - proxy: Optional value in format "http://user:password@host:port" 

### Obtaining jwt token.