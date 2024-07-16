import click
from .process_monitor import get_process_info, kill_process, suggest_kill_process
from .postgres_monitor import kill_idle_transactions
from .config_parser import parse_config
from .redis_cleaner import clean_idle_redis_keys


@click.group()
def cli():
    pass


@cli.command()
def monitor_processes():
    for info in get_process_info():
        print(info)


@cli.command()
@click.argument('pid', type=int)
def terminate_process(pid):
    kill_process(pid)
    print(f"Process {pid} terminated.")


@cli.command()
@click.argument('threshold', type=int, default=20)
def suggest_process_termination(threshold):
    suggest_kill_process(threshold)


@cli.command()
@click.argument('config_path', type=click.Path(exists=True))
def read_config(config_path):
    config = parse_config(config_path)
    for section in config.sections():
        print(section)
        for key, value in config.items(section):
            print(f"  {key} = {value}")


@cli.command()
@click.argument('conn_info', type=dict)
@click.argument('idle_threshold', type=int, default=150)
def clean_idle_transactions(conn_info, idle_threshold):
    kill_idle_transactions(conn_info, idle_threshold)
    print("Idle transactions cleaned.")


@cli.command()
@click.argument('redis_host')
@click.argument('redis_port', type=int, default=6379)
@click.argument('db', type=int, default=0)
@click.argument('startswithkey', type=str, default=None)
@click.argument('idletime', type=int, default=604800)
def clean_redis(redis_host, redis_port, db, startswithkey, idletime):
    clean_idle_redis_keys(redis_host, redis_port, db, startswithkey, idletime)
    print("Redis keys cleaned.")
