# DS-RL-Master

Build docker image:

> docker build . -t master-service:lstest

To run image:

> dorker run -p 30000:30000 master-service:lstest


## ІТЕРАЦІЯ 1 

>The Replicated Log should have the following deployment architecture: one Master and any number of Secondaries.

У проекті реалізований один Master та три відмінних Secondary: secondary-1, secondary-2-1, та laggy-secondary-1 зі змінним часу затримки, що передається за допомогою параметру -l.

>Master should expose simple HTTP server with: <br />
>POST method - appends a message into the in-memory list <br />
>GET method - returns all messages from the in-memory list

>Secondary should expose simple  HTTP server with:
>GET method - returns all replicated messages from the in-memory list

Обробка POST/GET-запитів у Master або Secondary здійснюється за допомогою інстансів класу MasterService з ``MasterService.py`` або SecondaryService з ``SecondaryService.py`` відповідно, що успадковує клас BaseHTTPRequestsHandler з бібліотеки http.server
НІ ![alt text](https://github.com/Qlorry/DS-labs/assets/62158298/b912e210-c55f-49f0-8fb6-15711212a4ee)


- Надсилаємо POST request із ``message1`` на Master, що на сокеті ``127.0.0.1:30000``
<img width="1005" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/e90cc6f6-6df7-455f-bf00-9b1c4d6238ac">
<img width="668" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/ffad5f74-fdf3-40db-b87a-ede1eb40e191">


- Отримуємо ``message1`` через GET на Secondary, що на сокеті ``127.0.0.1:20000``
 <img width="997" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/d511c83a-420d-4434-b44b-a3f68da0a248">

- Надсилаємо двічі ``message2`` та тричі ``message3``, у тілі відповіді на POST бачимо, що різні згачення "message" з однаковим вмістом мають різні індекси:
<img width="1027" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/f63f4187-e9fe-4b9f-849d-3b8a714c468d">


>to test that the replication is blocking, introduce the delay/sleep on the Secondary

Для симуляції затримки потрібно задати величику затримки в секундах за допомогою параметра ``-l`` при ініціалізації докер-контейнера laggy-secondary-1 в ``compose.yaml``:

<img width="312" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/dd9f8836-5311-4d35-9425-b1e4fa8e6517">

>Master should ensure that Secondaries have received a message via ACK
>Master’s POST request should be finished only after receiving ACKs from all Secondaries (blocking replication approach)

Звірка наявності ACK проводиться інстансами класів MessageSheduler та MasterDomain з ``MasterDomain.py``

Для перевірки міняємо -l на 15 і спостерігаємо за часом отримання клієнтом Postman відповіді на POST (10+ секунд змінюється на 15+ секунд):

<img width="666" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/1c849573-07ef-42c1-8765-ccd7774ce9cb">

<img width="1036" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/0e230a19-f7fb-4b5f-acf7-5d05ad157aea">

Також Master не відповідає на POST, якщо Secondary недоступні (вимкнені у Докері):
<img width="1017" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/e5c640e6-b469-401e-8afe-73bee955aec0">
<img width="1008" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/43e27bd5-ec07-47ff-a1eb-1a8abd639e5e">






>at this stage assume that the communication channel is a perfect link (no failures and messages lost)

Оскільки у даному проекті Docker-контейнери розгорнуті локально, за замовчуванням ми не втрачаємо повідомлення у межах цієї ітерації виконання проекту.

>your implementation should support logging 

Логіка логування описана у ``Logging.py``, що присутній в Master та Secondary. Логи поділяються на три шари: 'App', 'Service', 'Domain', та складаються у форматі, визначеному функцією configure_logging. 

<img width="833" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/3668614e-c509-4168-8c27-9f8eec81af2f">


Додатково Master регулярно - кожні 5 секунд, - пінгує Secondary сервіси:
<img width="656" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/08f2f097-fc42-4565-9c7f-a1fb00bf7f16">

Це реалізовано за допомогою функції ping в інстансі класу MasterDomain з ``MasterDomain.py``
<img width="542" alt="image" src="https://github.com/Qlorry/DS-RL-Master/assets/62158298/97789a80-8f39-48aa-a05e-3f71674b8a1d">




