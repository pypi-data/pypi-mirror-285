<div align="center">
  <h1>Edgedb DTO</h1>
  <a href="https://gitlab.com/linguacustodia/edgedb-dto" rel="nofollow">
    <img src="https://img.shields.io/gitlab/stars/linguacustodia/edgedb-dto" alt="Stars">
  </a>
  <a href="https://gitlab.com/linguacustodia/edgedb-dto/-/blob/main/LICENSE">
    <img alt="license" src="https://img.shields.io/badge/license-MIT-blue" />
  </a>
  <br />
  <br />
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <a href="https://gitlab.com/linguacustodia/edgedb-dto/-/tree/main/tests">Example</a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <!-- <a href="https://gitlab.com/linguacustodia/edgedb-dto/-/tree/main/tests">Tutorial</a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span> -->
  <br />
</div>

## Introduction

EdgeDB DTO Generator is a Python package that generates classes for edgeql queries methods for better type validation using pydantic.


## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Example](#example)
- [Limitations](#limitations)
- [Contributors](#contributors)
- [License](#license)

## Installation

To install the EdgeDB DTO Generator from pypi :

```sh
pip install edgedb-dto

````

Usage
-----

The main entry point for using the EdgeDB DTO Generator is through the CLI tool :

```sh
# First Run edgedb-py command to generate the python methods for your .edgeql files.
edgedb-py

# edgedb-dto will scan for those file and generate the classes
# -i option will generate init file to export the classes
edgedb-dto -i
```

### CLI Options

*   `--source-directory` (`-s`) [Optional argument]: Source directory containing EdgeQL files.
*   `--output-directory` (`-o`) [Optional argument]: Output directory for generated DTO classes.
*   `--init` (`-i`) [Flag]: Generate `__init__.py` file for the generated DTO classes.


PS : 
- `source-directory` is optional. Use it only if you want specific queries to be targeted otherwise, edgedb-dto will scan for the generated files.
- Please note that it's better for type safety to not specify the `output-directory` and in that case, the files will be generated in a folder named dto in the parent folder of the edgeql python files.


Features
--------
*   **Asynchronous and Synchronous Support**: Supports both asynchronous and synchronous DTO generation.
*   **Recursive Attribute Processing**: Recursively processes attributes for DTOs, lists, tuples, and namedtuples allowing to mix and match multiple DTOs.

Dependencies
------------
*   `python`: version=^3.11 is required to run this library.
*   `jinja2`: For templating the DTO classes.
*   `pydantic`: For data validation and settings management.
*   `edgedb`: For interacting with the EdgeDB database.

Example
--------
Let's see what edgedb-dto can do :
### Schema
```esdl
module default {
    abstract type Person {
        required first_name: str;
        required last_name: str;
        age: int16;
        email: str {
            constraint exclusive;
        }
    }

    type Student extending Person {
        supervisor : Instructor;
        enrollment_date: datetime;
        multi courses: Course;
    }

    type Instructor extending Person {
        hire_date: datetime;
        multi courses: Course;
    }

    type Course {
        required title: str;
        required code: str {
            constraint exclusive;
        }
        description: str;
    }
}

```
### Edgeql queries
Let's create 3 edgeql queries one for creating a student, and instructor and a course 
```edgeql
# insert_student.edgeql

select(
    insert Student{
        first_name := <str>$first_name,
        last_name := <str>$last_name,
        age := <optional int16>$age,
        email := <str>$email,
        enrollment_date := <optional datetime>$enrollment_date,

        supervisor := <Instructor>supervisor,
        courses := (select Course filter .id in array_unpack(<array<uuid>>$courses))
    }
){**}
```

```edgeql
# insert_instructor.edgeql

insert Instructor{
    first_name := <str>$first_name,
    last_name := <str>$last_name,
    age := <optional int16>$age,
    email := <str>$email,
    hire_date := <datetime>$hire_date,
    courses := (select Course filter .id in array_unpack(<array<uuid>>$courses))
}
```

```edgeql
# insert_course.edgeql

insert Course {
    title := <str>$title,
    code := <str>$code,
    description := <str>$description
} unless conflict on .code
else(
    select Course filter .code = code
)
```

now that we have our edgeql files let's run the following commands : 
```bash
edgedb-py
edgedb-dto -i
```
here is our generated classes : 
```python
# insert_student_async_edgeql_dto.py
import datetime
import uuid
from ..insert_student_async_edgeql import (
    insert_student,
    InsertStudentResult,
)
...

# You can modify this class as you wish.
# You can add type validation for the email for exemple you can also modify or add default values. But do not remove any attributes
# or remove any of the functions defined.
@dataclass
class InsertStudentAsync(DTO):
    supervisor: DTO | uuid.UUID
    first_name: str
    last_name: str
    email: str
    courses: list[DTO | uuid.UUID] = field(default_factory=list)
    age: int | None = None
    enrollment_date: datetime.datetime | None = None

    async def _query(self, **kwargs):
        return await insert_student(**kwargs)

    async def run(
        self, executor: AsyncIOClient, transaction: bool = False
    ) -> InsertStudentResult:
        return await self._run_async(executor, transaction)
```
```python
# insert_course_async_edgeql_dto.py
import uuid
from ..insert_course_async_edgeql import InsertCourseResult, insert_course
...

@dataclass
class InsertCourseAsync(DTO):
    title: str
    code: str
    description: str

    async def _query(self, **kwargs):
        return await insert_course(**kwargs)

    async def run(
        self, executor: AsyncIOClient, transaction: bool = False
    ) -> InsertCourseResult | None:
        return await self._run_async(executor, transaction)
```
```python
# insert_instructor_async_edgeql_dto.py
import datetime
import uuid
from ..insert_instructor_async_edgeql import insert_instructor, InsertInstructorResult
...

@dataclass
class InsertInstructorAsync(DTO):
    first_name: str
    last_name: str
    email: str
    hire_date: datetime.datetime
    age: int | None = None
    courses: list[DTO | uuid.UUID] = field(default_factory=list)

    async def _query(self, **kwargs):
        return await insert_instructor(**kwargs)

    async def run(
        self, executor: AsyncIOClient, transaction: bool = False
    ) -> InsertInstructorResult:
        return await self._run_async(executor, transaction)
```
### DTO Classes usecase :
Now let's populate our database with ease : 
- insert 2 courses (java and cpp)
- insert a supervisor
- insert a student

```python
from queries.dto import InsertCourseAsync, InsertStudentAsync, InsertInstructorAsync

import uuid
import asyncio
import edgedb
from datetime import datetime, timezone

executor = edgedb.create_async_client()

java = InsertCourseAsync(
    title="title",
    code=uuid.uuid4().hex,
    description="description",
)
cpp = InsertCourseAsync(
    title="title",
    code=uuid.uuid4().hex,
    description="description",
)
jerome = InsertInstructorAsync(
    first_name="first_name",
    last_name="last_name",
    email=uuid.uuid4().hex,
    hire_date=datetime.now(timezone.utc),
    age=100,
    courses=[java],
)
alice = InsertStudentAsync(
    supervisor=jerome,
    courses=[java, cpp],
    first_name="first_name",
    last_name="last_name",
    age=1,
    email=uuid.uuid4().hex,
    enrollment_date=datetime.now(timezone.utc),
)


async def main():
    print(await alice.run(executor=executor, transaction=True))
    await executor.aclose()


asyncio.run(main())
```
By calling 'run' on alice dto class we managed to insert all of our data into the database in a single transaction.

Limitations
-----------
#### N + 1 Problem 
edgedb-dto does not act like a query builder. So the more dtos you link the more back and forth calls are made to the database.
In the last exemple, 4 queries to the database are made to complete the transaction.

Contributors
------------

*   [Mohamed SAHNOUN](https://gitlab.com/mohammed.sahnounn)
*   [Jean-Gabriel BARTHELEMY](https://gitlab.com/jgcb00)   

License
-------

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
