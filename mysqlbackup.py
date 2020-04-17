#!/usr/bin/python

import click
import yaml
import os
from datetime import datetime
from shutil import copyfile


@click.group()
def cli():
    pass


@cli.command()
@click.option('--db-user', help='Database username')
@click.option('--db-password', help='Database password')
@click.option('--db-host', help='Database host address')
@click.option('--db-name', help='Database name')
@click.option('--backup-dir', help='Backups directory')
def full_backup(**kwargs):
    destination = compose_backup_destination(kwargs['backup_dir'])
    create_dir_if_not_exists(destination)
    dump_command = "mysqldump -u{db_user} -p{db_password} -h{db_host} --lock-tables=false --flush-logs " \
                   "--master-data=2 {db_name} | gzip > {destination}/{db_name}_$(date +'%Y-%m-%d-%H%M').sql.gz" \
        .format(destination=destination, **kwargs)
    os.system(dump_command)


@cli.command()
@click.option('--db-user', help='Database username')
@click.option('--db-password', help='Database password')
@click.option('--db-host', help='Database host address')
@click.option('--backup-dir', help='Backups directory')
@click.option('--bin-log-index', help='Full path to bin log index file')
def incremental(**kwargs):
    # flush binary logs
    flush_logs_command = "mysqladmin -u{db_user} -p{db_password} -h{db_host} flush-logs".format(**kwargs)
    os.system(flush_logs_command)
    # read the binary log index file to find the path of last but one binary log
    fp = open(kwargs['bin_log_index'], 'r')
    lines = fp.readlines()
    last_but_one_line = lines[-2].replace("\n", "")
    last_but_one_bin_log_number = last_but_one_line.split('.')[-1]
    last_but_one_bin_log_path = kwargs['bin_log_index'].replace('index', last_but_one_bin_log_number)
    # copy binary log to backup destination
    backup_destination = compose_backup_destination(kwargs['backup_dir'])
    copyfile(last_but_one_bin_log_path, os.path.join(backup_destination, last_but_one_bin_log_path.split('/')[-1]))


def get_config():
    with open("config.yaml", 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def compose_backup_destination(backup_dir):
    return os.path.join(
        backup_dir,
        datetime.today().strftime('%Y'),
        datetime.today().strftime('%Y-%m'),
        datetime.today().strftime('%Y-%m-%d')
    )


if __name__ == '__main__':
    config = get_config()
    cli(default_map={
        "full-backup": config,
        "incremental": config
    })
