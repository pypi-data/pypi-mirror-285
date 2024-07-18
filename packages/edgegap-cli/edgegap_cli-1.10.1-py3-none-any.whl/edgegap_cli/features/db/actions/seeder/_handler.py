import logging

from pydantic import PostgresDsn
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import Session, sessionmaker

from ._enum import OperationEnum
from ._models import SeedBinding, SeederElement, SeederModel
from ._operator import SeederOperator


class SeederHandler:
    def __init__(self, uri: PostgresDsn, seeds: list[SeederModel], logger: logging.Logger):
        self.__logger = logger
        self.__seeds = seeds
        self.__engine = create_engine(str(uri))
        self.__metadata = MetaData()
        self.__session_maker = sessionmaker(self.__engine)

    def seed(self):
        for seed in self.__seeds:
            self.__logger.info(seed)
            self.__seed(seed)

    def __seed(self, seed: SeederModel):
        table = Table(
            seed.table,
            self.__metadata,
            autoload_with=self.__engine,
        )

        for element in seed.elements:
            with self.__session_maker() as session:
                try:
                    self.__seed_element(
                        keys=seed.lookup_keys,
                        operation=seed.operation,
                        table=table,
                        element=element,
                        session=session,
                    )
                    session.commit()
                except Exception as e:
                    self.__logger.error(f"{seed} - Could not seed the element {element.name} : {e}")
                    session.rollback()
                finally:
                    session.close()

    def __seed_element(
            self,
            keys: list[str],
            operation: OperationEnum,
            table: Table,
            element: SeederElement,
            session: Session,
            binding: SeedBinding | None = None,
    ):
        self.__logger.info(f"{element} - Processing")
        operator = SeederOperator(
            element=element,
            table=table,
            binding=binding,
        )
        rows = operator.lookup(keys, session)

        if len(rows) > 1:
            raise Exception(f"{element} - Multiple rows found!")

        if len(rows) == 0:
            self.__logger.info(f"{element} - does not exists and will be created")
            result = operator.create(session)
            primary_key = result.inserted_primary_key[0]
            self.__logger.info(f"{element} - created primary key: [#{primary_key}]")
        else:
            primary_key_name = table.primary_key.columns[0].name
            primary_key = getattr(rows[0], primary_key_name)

            if operation == OperationEnum.CREATE_OR_UPDATE:
                self.__logger.info(f"{element} - already exists (#{primary_key}) and will be updated")
                operator.update(primary_key, session)
                self.__logger.info(f"{element} - updated element with primary key: [#{primary_key}]")
            else:
                self.__logger.info(f"{element} - already exists (#{primary_key}) and won't be updated")

        self.__sub_elements(
            element=element,
            primary_key=primary_key,
            session=session,
        )

    def __sub_elements(self, element: SeederElement, primary_key: int, session: Session):
        for sub_elements in element.sub_elements:
            sub_elements.binding.value = primary_key
            self.__logger.info(sub_elements)

            for sub_element in sub_elements.elements:
                table = Table(
                    sub_elements.table,
                    self.__metadata,
                    autoload_with=self.__engine,
                )
                self.__seed_element(
                    keys=sub_elements.lookup_keys,
                    operation=sub_elements.operation,
                    table=table,
                    element=sub_element,
                    session=session,
                    binding=sub_elements.binding,
                )
