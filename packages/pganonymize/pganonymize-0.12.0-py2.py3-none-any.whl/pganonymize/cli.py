"""Commandline implementation"""

from __future__ import absolute_import, print_function

import argparse
import logging
import time

from pganonymize.config import config, validate_args_with_config
from pganonymize.constants import DATABASE_ARGS, DEFAULT_SCHEMA_FILE
from pganonymize.providers import provider_registry
from pganonymize.utils import anonymize_tables, create_database_dump, get_connection, truncate_tables


def get_pg_args(args):
    """
    Map all commandline arguments with database keys.

    :param argparse.Namespace args: The commandline arguments
    :return: A dictionary with database arguments
    :rtype: dict
    """
    return ({name: value for name, value in
             zip(DATABASE_ARGS, (args.dbname, args.user, args.password, args.host, args.port))})


def list_provider_classes():
    """List all available provider classes."""
    print('Available provider classes:\n')
    for key, provider_cls in provider_registry.providers.items():
        print('{:<10} {}'.format(key, provider_cls.__doc__))


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Anonymize data of a PostgreSQL database')
    parser.add_argument('-v', '--verbose', action='count', help='Increase verbosity')
    parser.add_argument('-l', '--list-providers', action='store_true', help='Show a list of all available providers',
                        default=False)
    parser.add_argument('--schema', help='A YAML schema file that contains the anonymization rules',
                        default=DEFAULT_SCHEMA_FILE)
    parser.add_argument('--dbname', help='Name of the database')
    parser.add_argument('--user', help='Name of the database user')
    parser.add_argument('--password', default='', help='Password for the database user')
    parser.add_argument('--host', help='Database hostname', default='localhost')
    parser.add_argument('--port', help='Port of the database', default='5432')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t commit changes made on the database',
                        default=False)
    parser.add_argument('--dump-file', help='Create a database dump file with the given name')
    parser.add_argument('--dump-options', help='Options to pass to the pg_dump command',
                        default='--format custom --compress 9')
    parser.add_argument('--init-sql', help='SQL to run before starting anonymization', default=False)
    parser.add_argument(
        '--parallel',
        action='store_true',
        help=(
            'Parallelize anonymization of value.'
            'WARNING: `fake.unique.*` providers are not compatible with this option'
        ),
        default=False,
    )

    return parser


def main(args):
    """Main method"""

    loglevel = logging.WARNING
    if args.verbose:
        loglevel = logging.DEBUG
    logging.basicConfig(format='%(levelname)s: %(message)s', level=loglevel)

    if args.list_providers:
        list_provider_classes()
        return 0

    config.schema_file = args.schema

    validate_args_with_config(args, config)

    pg_args = get_pg_args(args)
    connection = get_connection(pg_args)
    if args.init_sql:
        cursor = connection.cursor()
        logging.info('Executing initialisation sql {}'.format(args.init_sql))
        cursor.execute(args.init_sql)
        cursor.close()

    start_time = time.time()
    truncate_tables(connection)
    anonymize_tables(
        connection,
        verbose=args.verbose,
        dry_run=args.dry_run,
        parallel=args.parallel,
    )

    if not args.dry_run:
        connection.commit()
    connection.close()

    end_time = time.time()
    logging.info('Anonymization took {:.2f}s'.format(end_time - start_time))

    if args.dump_file:
        create_database_dump(args.dump_file, pg_args, args.dump_options)
