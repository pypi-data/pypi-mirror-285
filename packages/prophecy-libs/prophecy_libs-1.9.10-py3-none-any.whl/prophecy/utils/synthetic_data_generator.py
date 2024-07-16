import random
from datetime import datetime
from typing import Any

from pyspark.sql import Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType, DateType, \
    TimestampType, LongType

from prophecy.utils.dill import _dill as pickle
from .faker import Faker


# Define a base class for faker functions
class BaseFakerFunction:
    def __init__(self):
        self.faker = Faker()

    def generate(self, row_id: int, **kwargs) -> Any:
        raise NotImplementedError("This method should be overridden by subclasses")


class RandomFullName(BaseFakerFunction):
    def generate(self, row_id: int, **kwargs) -> str:
        return self.faker.name()


class RandomFirstName(BaseFakerFunction):
    def generate(self, row_id: int, **kwargs) -> str:
        return self.faker.first_name()


class RandomLastName(BaseFakerFunction):
    def generate(self, row_id: int, **kwargs) -> str:
        return self.faker.last_name()


class RandomEmail(BaseFakerFunction):
    def generate(self, row_id: int, **kwargs) -> str:
        return self.faker.email()


class RandomAddress(BaseFakerFunction):
    def generate(self, row_id: int, **kwargs) -> str:
        return self.faker.address()


class RandomPhoneNumber(BaseFakerFunction):
    def __init__(self, pattern="###-###-####"):
        super().__init__()
        self.pattern = pattern

    def generate(self, row_id: int, **kwargs) -> str:
        return self.faker.numerify(self.pattern)


class RandomUUID(BaseFakerFunction):
    def generate(self, row_id: int, **kwargs) -> str:
        return self.faker.uuid4()


class RandomInt(BaseFakerFunction):
    def __init__(self, min=0, max=100):
        super().__init__()
        self.min = min
        self.max = max

    def generate(self, row_id: int, **kwargs) -> int:
        return self.faker.random_int(min=self.min, max=self.max)


class RandomFloat(BaseFakerFunction):
    def __init__(self, min_value=0, max_value=100, decimal_places=2):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_places = decimal_places

    def generate(self, row_id: int, **kwargs) -> float:
        return self.faker.pyfloat(min_value=self.min_value, max_value=self.max_value, right_digits=self.decimal_places)


class RandomBoolean(BaseFakerFunction):
    def generate(self, row_id: int, **kwargs) -> bool:
        return self.faker.boolean()


class RandomListElements(BaseFakerFunction):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def generate(self, row_id: int, **kwargs) -> Any:
        return self.faker.random_element(self.elements)


class RandomDate(BaseFakerFunction):
    def __init__(self, start_date, end_date):
        super().__init__()
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    def generate(self, row_id: int, **kwargs) -> datetime:
        return self.faker.date_between_dates(date_start=self.start_date, date_end=self.end_date)


class RandomDateTime(BaseFakerFunction):
    def __init__(self, start_datetime, end_datetime):
        super().__init__()
        self.start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
        self.end_datetime = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")

    def generate(self, row_id: int, **kwargs) -> datetime:
        return self.faker.date_time_between_dates(datetime_start=self.start_datetime, datetime_end=self.end_datetime)


class RandomForeignKey(BaseFakerFunction):
    def __init__(self, ref_table, ref_column):
        super().__init__()
        self.ref_table = ref_table
        self.ref_column = ref_column
        self.ref_values = None  # This will be set later

    def set_ref_values(self, ref_values):
        self.ref_values = ref_values

    def generate(self, row_id: int, **kwargs) -> Any:
        if self.ref_values is None:
            raise ValueError("Reference values not set")
        return self.faker.random_element(self.ref_values)


# Create a class mapping for serialization
CLASS_MAPPING = {
    "RandomFullName": RandomFullName,
    "RandomFirstName": RandomFirstName,
    "RandomLastName": RandomLastName,
    "RandomEmail": RandomEmail,
    "RandomAddress": RandomAddress,
    "RandomPhoneNumber": RandomPhoneNumber,
    "RandomUUID": RandomUUID,
    "RandomInt": RandomInt,
    "RandomFloat": RandomFloat,
    "RandomBoolean": RandomBoolean,
    "RandomListElements": RandomListElements,
    "RandomDate": RandomDate,
    "RandomDateTime": RandomDateTime,
    "RandomForeignKey": RandomForeignKey
}

# Serialize the class mapping for broadcasting
serialized_class_mapping = pickle.dumps(CLASS_MAPPING)


# FakeDataFrame class with improved OOP design
class FakeDataFrame:
    def __init__(self, spark, rows, null_rows=0, seed=None, locale=None):
        self.spark = spark
        self.rows = rows
        self.null_rows = null_rows
        self.seed = seed
        self.locale = locale
        self.df = spark.range(rows).toDF("temp_id")
        self.schema_fields = []
        self.faker_methods_dict = {}
        self.null_columns_dict = {}
        self.data_type_mapping = {
            StringType(): "String",
            IntegerType(): "Integer",
            LongType(): "Long",
            FloatType(): "Float",
            BooleanType(): "Boolean",
            DateType(): "Date",
            TimestampType(): "Timestamp"
        }
        if seed is not None:
            random.seed(seed)

    def addColumn(self, column_name, faker_function: BaseFakerFunction, data_type=None, nulls=0, unique=False):
        if data_type in self.data_type_mapping:
            self.schema_fields.append(StructField(column_name, data_type, nullable=True))
        else:
            raise ValueError(f"Unsupported data type: {data_type}")

        if isinstance(faker_function, RandomForeignKey):
            ref_df = self.spark.read.table(faker_function.ref_table).select(faker_function.ref_column).distinct()
            ref_values = [row[faker_function.ref_column] for row in ref_df.collect()]
            faker_function.set_ref_values(ref_values)  # Set reference values

        self.faker_methods_dict[column_name] = (faker_function.__class__.__name__, faker_function.__dict__)

        self.null_columns_dict[column_name] = nulls

        if unique:
            self.faker_methods_dict[column_name] = (
            "unique_" + self.faker_methods_dict[column_name][0], self.faker_methods_dict[column_name][1])

        return self

    def build(self):
        schema = StructType(self.schema_fields)
        column_list = [field.name for field in self.schema_fields]

        total_rows = self.rows
        null_rows = self.null_rows

        null_indices = {column: random.sample(range(total_rows), nulls) for column, nulls in
                        self.null_columns_dict.items()}

        broadcast_faker_methods_dict = self.spark.sparkContext.broadcast(self.faker_methods_dict)
        broadcast_null_indices = self.spark.sparkContext.broadcast(null_indices)
        broadcast_class_mapping = self.spark.sparkContext.broadcast(serialized_class_mapping)

        def generate_partition(partition):
            faker_methods_dict = broadcast_faker_methods_dict.value
            null_indices = broadcast_null_indices.value
            class_mapping = pickle.loads(broadcast_class_mapping.value)

            # Instantiate Faker and faker function classes on the worker
            fake = Faker()

            def instantiate_faker_function(class_name, params):
                klass = class_mapping[class_name]
                instance = klass.__new__(klass)
                instance.__dict__.update(params)
                instance.faker = fake
                return instance

            result = []
            for row_id in partition:
                row_id = row_id[1]
                if row_id < null_rows:
                    row_data = [None] * len(column_list)
                else:
                    row_data = []
                    for column in column_list:
                        if row_id in null_indices.get(column, []):
                            row_data.append(None)
                        else:
                            faker_class_name, faker_params = faker_methods_dict[column]
                            faker_function = instantiate_faker_function(faker_class_name, faker_params)
                            row_data.append(faker_function.generate(row_id))
                result.append(Row(*row_data))
            return result

        fake_data_rdd = self.df.rdd.zipWithIndex().mapPartitions(generate_partition)
        fake_data_df = self.spark.createDataFrame(fake_data_rdd, schema)

        return fake_data_df
