# Использование

### Полный бэкап
```shell script
$ python mysqlbackup.py full-backup
```
Эта команда снимает полный бэкап с помощью `mysqldump`, сжимает с помощью `gzip` и сохраняет в папку в формате `/<backup_dir>/2020/2020-01/2020-01-01/db_name_2020-01-01-0000.sql.gz`

### Инкрементальный бэкап
```shell script
$ python mysqlbackup.py incremental
``` 

Эта команда выполняет команду [FLUSH LOGS](https://dev.mysql.com/doc/refman/8.0/en/flush.html#flush-logs), и копирует предпоследний бинарный лог в папку рядом с полным бэкапом

[Подробнее](https://dev.mysql.com/doc/refman/5.7/en/backup-methods.html) о разных методах бэпапа в mysql

# Установка

### Скачаем утилиту и распакуем
```shell script
$ wget https://github.com/alifcapital/mysqlbackup/archive/master.zip
$ unzip master.zip
$ cd mysqlbackup-master
```

### Устанавливаем все зависимости 
```shell script
$ pip install -r requirements.txt
```

### Создадим файл конфигурации
```shell script
$ cp config.yaml.example config.yaml
```

### Укажем в `config.yaml` все необходимые параметры:

- `db_name` — название БД
- `db_user` — имя пользователя БД
- `db_password` — пароль пользователя
- `db_host` — адрес БД
- `backup_dir` – путь директории, куда будут сохраняться бэкапы
- `bin_log_index` – путь к индексовому файлу бинарных логов mysql. Этот путь можно узнать выполнив запрос `show variables like "log_bin_index"`

### Включаем бинарные логи
 
Для этого нужно в файле конфигурации mysql `my.cnf` указать следующее:
```shell script
log_bin = /var/log/mysql/mysql-bin.log
```

Если БД является слейвом, то изменения БД, которые приходят с мастера по умолчанию не будут записываться в бинарных логах. Чтобы включить запись в бинарные логи для слейва, нужно дополнительно указать такой параметр:
```shell script
log_slave_updates = ON
``` 

# Использование в `cron`

Допустим у нас такая стратегия бэкапирования:

- Каждый день в полночь снимаем полный бэкап
- Каждые 15 минут снимаем инкрементальный бэкап

Открываем для редактирования файл `crontab`:
```shell script
$ sudo crontab -e
```  

Добавляем следующие строки:
```shell script
0 0 * * * python /home/johndoe/mysqlbackup-master/mysqlbackup.py full-backup
*/15 * * * * python /home/johndoe/mysqlbackup-master/mysqlbackup.py incremental
```

# Восстановление

Восстановление данных состоит из двух шагов:
1. Восстановление полного бэкапа
2. Применение бинарных логов снятых после полного бэкапа

Подробнее о восстановлении данных:

- [Using Backups for Recovery](https://dev.mysql.com/doc/refman/8.0/en/recovery-from-backups.html)
- [Point-in-Time (Incremental) Recovery Using the Binary Log](https://dev.mysql.com/doc/refman/5.7/en/point-in-time-recovery.html)

