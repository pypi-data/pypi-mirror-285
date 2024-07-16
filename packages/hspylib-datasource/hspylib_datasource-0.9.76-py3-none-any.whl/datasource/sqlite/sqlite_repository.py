#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
   @project: HsPyLib-Datasource
   @package: datasource.sqlite
      @file: sqlite_repository.py
   @created: Tue, 4 May 2021
    @author: <B>H</B>ugo <B>S</B>aporetti <B>J</B>unior"
      @site: https://github.com/yorevs/hspylib
   @license: MIT - Please refer to <https://opensource.org/licenses/MIT>

   Copyright·(c)·2024,·HSPyLib
"""
from abc import abstractmethod
from datasource.crud_entity import CrudEntity
from datasource.db_configuration import DBConfiguration
from datasource.db_repository import Connection, Cursor, DBRepository, ResultSet, Session
from datasource.exception.exceptions import DatabaseConnectionError, DatabaseError
from datasource.identity import Identity
from hspylib.core.metaclass.singleton import AbstractSingleton
from hspylib.core.namespace import Namespace
from hspylib.core.tools.text_tools import quote
from sqlite3 import Error
from typing import Generic, List, Optional, Set, Tuple, TypeVar

import contextlib
import logging as log
import sqlite3

E = TypeVar("E", bound=CrudEntity)
C = TypeVar("C", bound=DBConfiguration)


class SQLiteRepository(Generic[E, C], DBRepository[E, C], metaclass=AbstractSingleton):
    """Implementation of a data access layer for a SQLite persistence store."""

    @property
    def database(self) -> str:
        return self._config.database

    @property
    def info(self) -> str:
        return f"{self.database}"

    def _create_session(self) -> Tuple[Connection, Cursor]:
        log.debug("%s Attempt to connect to database: %s", self.logname, str(self))
        conn = sqlite3.connect(self.database)
        return conn, conn.cursor()

    @contextlib.contextmanager
    def _session(self) -> Session:
        log.debug("%s Attempt to connect to database: %s", self.logname, self.database)
        conn, dbs = None, None
        try:
            conn, dbs = self._create_session()
            log.debug("%s Successfully connected to database: %s [ssid=%d]", self.logname, self.info, hash(dbs))
            yield dbs
        except Error as err:
            raise DatabaseConnectionError(f"Unable to open/execute-on database: {self.database} => {err}") from err
        finally:
            if conn:
                log.debug("%s Closing connection [ssid=%d]", self.logname, hash(dbs))
                conn.commit()
                conn.close()

    def execute(self, sql_statement: str, **kwargs) -> Tuple[int, Optional[ResultSet]]:
        with self._session() as dbs:
            try:
                args = dict(kwargs)
                log.debug(
                    "%s Executing SQL statement [ssid=%s]:\n" "\t|-Arguments: %s\n" "\t|-Statement: %s",
                    self.logname,
                    hash(dbs),
                    args,
                    sql_statement,
                )
                rows = dbs.execute(sql_statement, tuple(args.values())).fetchall()
                return dbs.rowcount, rows
            except (sqlite3.ProgrammingError, sqlite3.OperationalError) as err:
                raise DatabaseError(f"Unable to execute statement => {sql_statement}") from err

    def count(self) -> int:
        sql = f"SELECT COUNT(*) FROM {self.table_name()}"
        return int(self.execute(sql)[1][0][0])

    def delete(self, entity: E) -> None:
        self.delete_by_id(entity.identity)

    def delete_by_id(self, entity_id: Identity) -> None:
        clauses = [f"{k} = {quote(v)}" for k, v in zip(entity_id.attributes, entity_id.values)]
        sql = f"DELETE FROM {self.table_name()} WHERE " + " AND ".join(clauses)
        self.execute(sql)

    def delete_all(self, entities: List[E]) -> None:
        values, s = [], entities[0]
        list(map(lambda e: values.append(str(e.values)), entities))
        sql = f"DELETE FROM " f"{self.table_name()} WHERE ({s.as_columns()}) IN ({', '.join(values)}) "
        self.execute(sql)

    def save(self, entity: E) -> None:
        columns, ids = entity.as_columns(), set(entity.identity.attributes)
        sql = (
            f"INSERT INTO "
            f"{self.table_name()} ({columns}) VALUES {entity.values} "
            f"ON CONFLICT DO UPDATE SET {entity.as_column_set(prefix='EXCLUDED.', exclude=ids)}"
        )
        self.execute(sql)

    def save_all(self, entities: List[E]) -> None:
        values, sample = [], entities[0]
        columns, ids = sample.as_columns(), set(sample.identity.attributes)
        list(map(lambda e: values.append(str(e.values)), entities))
        sql = (
            f"INSERT INTO "
            f"{self.table_name()} ({columns}) VALUES {', '.join(values)} "
            f"ON CONFLICT DO UPDATE SET {sample.as_column_set(prefix='EXCLUDED.', exclude=ids)}"
        )
        self.execute(sql)

    def find_all(
        self,
        columns: Optional[Set[str]] = None,
        filters: Optional[Namespace] = None,
        order_bys: Optional[List[str]] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> List[E]:
        columns = "*" if not columns else ", ".join(columns)
        clauses = list(filter(None, filters.values)) if filters else None
        orders = list(filter(None, order_bys)) if order_bys else None
        sql = (
            f"SELECT {columns} FROM {self.table_name()} "
            f"{('WHERE ' + ' AND '.join(clauses)) if clauses else ''} "
            f"{('ORDER BY ' + ', '.join(orders)) if orders else ''} "
            f"LIMIT {limit} OFFSET {offset}"
        )

        return list(map(self.to_entity_type, self.execute(sql)[1]))

    def find_by_id(self, entity_id: Identity, columns: Optional[Set[str]] = None) -> Optional[E]:
        columns = "*" if not columns else ", ".join(columns)
        clauses = [f"{k} = {quote(v)}" for k, v in zip(entity_id.attributes, entity_id.values)]
        sql = f"SELECT {columns} FROM {self.table_name()} " f"WHERE {' AND '.join(clauses)}"
        result = next((e for e in self.execute(sql)[1]), None)

        return self.to_entity_type(result) if result else None

    def exists_by_id(self, entity_id: Identity) -> bool:
        clauses = [f"{k} = {quote(v)}" for k, v in zip(entity_id.attributes, entity_id.values)]
        sql = f"SELECT EXISTS(SELECT 1 FROM {self.table_name()} WHERE {' AND '.join(clauses)})"

        return self.execute(sql)[1][0][0] > 0

    @abstractmethod
    def table_name(self) -> str:
        pass

    @abstractmethod
    def to_entity_type(self, entity_dict: dict | tuple) -> E:
        pass
