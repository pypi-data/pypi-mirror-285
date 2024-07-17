# GraphQL to Pydantic Converter & Pydantic to Query Builder

## Overview

The **GraphQL to Pydantic Converter** is a Python package designed to simplify the process of transforming GraphQL 
schemas in JSON format into Pydantic models. This tool is particularly useful for developers working with GraphQL
APIs who want to generate Pydantic models from GraphQL types for efficient data validation 
and serialization/deserialization.


## Features

- Converts GraphQL schemas in JSON format into Pydantic models.
- Build query or mutation from pydantic dataclass

## Installation

You can install the **GraphQL to Pydantic Transformer** package via pip:

```bash
pip install graphql-pydantic-converter
# or
poetry add git+https://github.com/FRINXio/frinx-services-python-api.git@main#subdirectory=utils/graphql-pydantic-converter
```

## Usage

### Cli tool to transform GraphQL JSON to Pydantic

```bash
graphql-pydantic-converter [-h] [-i INPUT_FILE] [-o OUTPUT_FILE] [--url URL] [--headers HEADERS [HEADERS ...] ]

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE 
  -o OUTPUT_FILE, --output-file OUTPUT_FILE      
  --url URL 
  --headers HEADERS [HEADERS ...] # --headers "HeaderName: HeaderValue" "HeaderName: HeaderValue"
```

### Output from cli tool

```python
import typing

from pydantic import Field
from pydantic import PrivateAttr
from graphql_pydantic_converter.graphql_types import Input
from graphql_pydantic_converter.graphql_types import Mutation
from graphql_pydantic_converter.graphql_types import Payload

Boolean: typing.TypeAlias = bool
DateTime: typing.TypeAlias = typing.Any
Float: typing.TypeAlias = float
ID: typing.TypeAlias = str
Int: typing.TypeAlias = int
JSON: typing.TypeAlias = typing.Any
String: typing.TypeAlias = str

class CreateScheduleInput(Input):
    name: String
    workflow_name: String = Field(default=None, alias='workflowName')
    workflow_version: String = Field(default=None, alias='workflowVersion')
    cron_string: String = Field(default=None, alias='cronString')
    enabled: typing.Optional[Boolean] = Field(default=None)
    parallel_runs: typing.Optional[Boolean] = Field(default=None, alias='parallelRuns')
    workflow_context: typing.Optional[String] = Field(default=None, alias='workflowContext')
    from_date: typing.Optional[DateTime] = Field(default=None, alias='fromDate')
    to_date: typing.Optional[DateTime] = Field(default=None, alias='toDate')

class Schedule(Payload):
    name: typing.Optional[bool] = Field(default=False)
    enabled: typing.Optional[bool] = Field(default=False)
    parallel_runs: typing.Optional[bool] = Field(alias='parallelRuns', default=False)
    workflow_name: typing.Optional[bool] = Field(alias='workflowName', default=False)
    workflow_version: typing.Optional[bool] = Field(alias='workflowVersion', default=False)
    cron_string: typing.Optional[bool] = Field(alias='cronString', default=False)
    workflow_context: typing.Optional[bool] = Field(alias='workflowContext', default=False)
    from_date: typing.Optional[bool] = Field(alias='fromDate', default=False)
    to_date: typing.Optional[bool] = Field(alias='toDate', default=False)
    status: typing.Optional[bool] = Field(default=False)


class CreateScheduleMutation(Mutation):
    _name: str = PrivateAttr('createSchedule')
    input: CreateScheduleInput
    payload: Schedule

CreateScheduleInput.model_rebuild()
CreateScheduleMutation.model_rebuild()
Schedule.model_rebuild()

```

### Query & Mutation builder


```python
from schedule_api import Schedule, CreateScheduleMutation, CreateScheduleInput

SCHEDULE: Schedule = Schedule(
    name=True,
    enabled=True,
    workflow_name=True,
    workflow_version=True,
    cron_string=True
)

mutation = CreateScheduleMutation(
    payload=SCHEDULE,
    input=CreateScheduleInput(
        name='name',
        workflow_name='workflowName',
        workflow_version='workflowVersion',
        cron_string='* * * * *',
        enabled=True,
        parallel_runs=False,
    )
)


```


Created query with inlined variables as string

```

mutation.render(form='inline')

mutation {
  createSchedule(
    input: {
      name: "name"
      workflowName: "workflowName"
      workflowVersion: "workflowVersion"
      cronString: "* * * * *"
      enabled: true
      parallelRuns: false
    }
  ) {
    name
    enabled
    workflowName
    workflowVersion
    cronString
  }
}

```
Created query with extracted variables

```
mutation, variables = mutation.render(form='extracted)

# mutation as a string
mutation ($input: CreateScheduleInput!) { 
  createSchedule(input: $input) { 
    name 
    enabled 
    workflowName
    workflowVersion 
    cronString 
  } 
}

# variables as a dict[str, Any]
{
  "input": {
    "name": "name",
    "workflowName": "workflowName",
    "workflowVersion": "workflowVersion",
    "cronString": "* * * * *",
    "enabled": true,
    "parallelRuns": false
  }
}
```

### Response parser

Example of generated model.py

```python 
import typing
from pydantic import BaseModel, Field
from graphql_pydantic_converter.graphql_types import ENUM

Boolean: typing.TypeAlias = bool
DateTime: typing.TypeAlias = typing.Any
Float: typing.TypeAlias = float
ID: typing.TypeAlias = str
Int: typing.TypeAlias = int
JSON: typing.TypeAlias = typing.Any
String: typing.TypeAlias = str

class Status(ENUM):
    UNKNOWN = 'UNKNOWN'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    PAUSED = 'PAUSED'
    RUNNING = 'RUNNING'
    TERMINATED = 'TERMINATED'
    TIMED_OUT = 'TIMED_OUT'

    
class SchedulePayload(BaseModel):
    name: typing.Optional[typing.Optional[String]] = Field(default=None)
    enabled: typing.Optional[typing.Optional[Boolean]] = Field(default=None)
    parallel_runs: typing.Optional[typing.Optional[Boolean]] = Field(default=None, alias='parallelRuns')
    workflow_name: typing.Optional[typing.Optional[String]] = Field(default=None, alias='workflowName')
    workflow_version: typing.Optional[typing.Optional[String]] = Field(default=None, alias='workflowVersion')
    cron_string: typing.Optional[typing.Optional[String]] = Field(default=None, alias='cronString')
    workflow_context: typing.Optional[typing.Optional[String]] = Field(default=None, alias='workflowContext')
    from_date: typing.Optional[typing.Optional[DateTime]] = Field(default=None, alias='fromDate')
    to_date: typing.Optional[typing.Optional[DateTime]] = Field(default=None, alias='toDate')
    status: typing.Optional[typing.Optional[Status]] = Field(default=None)


class CreateScheduleData(BaseModel):
    create_schedule: SchedulePayload = Field(default=None, alias='createSchedule')

    
class CreateScheduleResponse(BaseModel):
    data: typing.Optional[CreateScheduleData] = Field(default=None)
    errors: typing.Optional[typing.Any] = Field(default=None)


```

### Example of response

```python

from model import CreateScheduleResponse

# send previously created request to backend service
payload = {'query': mutation.render()}
resp = requests.post(SCHELLAR_URL, json=payload)
response = resp.json()

# Example of response
# { 
#    'data': {
#         'createSchedule': {
#              'name': 'name', 
#              'enabled': True, 
#              'workflowName': 'workflowName', 
#              'workflowVersion': 'workflowVersion', 
#              'cronString': '* * * * *'
#          }
#     }
# }

schedule = CreateScheduleResponse(**response)

if schedule.errors is None:
    print(schedule.data.create_schedule.workflow_name)
else:
    print(schedule.errors)
```
