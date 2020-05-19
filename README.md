**home-rpi**

Директория проекта:
```
.
├── database                        # Директория для хранения данных
│   ├── cam_content                 # Сохранённые фото и видео
│   │   ├── photo
│   │   └── video
│   ├── model                       # Директория с обученной моделью
│   │   └── model.yml
│   ├── settings                    # Директория с текущими и настройками по умолчанию
│   │   ├── default_settings.json
│   │   └── settings.json
│   └── _temp                       # Директория с лицами для обучения 
├── recognizer                      # Директория скриптов для работы с нейросетью
│   ├── recognizer.py
│   └── trainer.py
├── server                          # Директория для работы с сервером
│   ├── main.py
│   ├── static                      # Директория стилей 
│   │   └── style4.css
│   └── templates                   # Директория html-кода страниц
│       ├── index.html
│       └── train.html
├── tbot                            # Директория для работы с телеграм-ботом
│   ├── start.py
│   └── tbot.py
└── tools                           # Директория со вспомогательными скриптами
    └── tools.py
```    
