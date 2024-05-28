# Blum Drop Game Bot
Бот имитирует Drop Game в Blum, используя Blum API.
Можно фармить очки с нескольких аккаунтов Telegram.
При запуске бот будет запускать игры до тех пор, пока не кончатся алмазы. 

## Установка
Скачайте Python 3.12 и установите бота из корневой папки проекта.

```python
pip install .
```

## Usage
### Получение JWT токена
1) Включаем DevTools в Telegram. Открываем Telegram на компьютере, заходим в "настройки" -> "продвинутые настройки", и в самом низу открываем "экспериментальные настройки". Нужно включить "Enable webview inspecting".
![](./docs/tg1.png)
![](./docs/tg2.png)
![](./docs/tg3.png)
2) Откройте приложение Blum, откройте DevTools на правую кнопку мыши, перейдите на вкладку Сеть (Network).
3) Найдите на вкладке Сеть любой запрос к Blum. Например, `balance`.
4) Во вкладке заголовки (Headers) будет заголовок `Авторизация`, содержащий JWT Token. 
![](./docs/screen.png)

### Конфигурационный файл
Отредактируйте файл `yaml` похожим образом:

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

- cpu_count: Количество процессоров. Не добавляйте этот параметр для автоматической установки количества процессоров.
- min_points: Минимальное значение случайного количества баллов, которое будет получено за игру.  
- max_points: Максимальное значение случайного количества баллов, которое будет начислено. Должно быть не более 270.
- telegrams: Настройки для аккаунтов telegram.
  - jwt_token: Токен в формате "Bearer ..."
  - proxy: Необязательное значение в формате "http://user:password@host:port" 


### Running script
```cmd
blum-drop-game-bot.exe --config path/to/config.yaml
```
