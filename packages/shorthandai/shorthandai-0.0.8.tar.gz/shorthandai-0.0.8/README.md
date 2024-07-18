## shorthandai

This package provides a Python SDK for working with the ShorthandAI platform.

### Installation
```sh
$ pip install shorthandai
```

### Usage
```py
from shorthandai import ShorthandAI

# Token can be passed by setting the environment variable `SHORTHANDAI_TOKEN`.
# token can be generated at https://apiv1.shorthand.ai/console/tokens
SH = ShorthandAI()

# Alternately, pass in the token explicitly
token = 'sh-...' 
SH = ShorthandAI(token)

# Get values
print(SH.get("dev123"))

# Set values
print(SH.set("dev123", 4000))

import datetime
# Get historical
print(SH.geth("dev123", datetime.datetime(2022, 12, 31)))
```

For example, new users can try out the following:
```py
from shorthandai import ShorthandAI

SH = ShorthandAI('demo')
print(SH.info())
print(SH.GET('dev123', '1659994710026'))
print(SH.GET('dev123', 'notexists'))
print(SH.GET('dev123'))
print(SH.GET('dev444'))

print("\nTesting GET-historical\n")
import datetime
print(SH.GETH('dev123', datetime.datetime(2022, 12, 31)))
print(SH.GETH('dev123', datetime.datetime(2022, 11, 1)))
print(SH.GETH('dev123', datetime.datetime(2023, 2, 24)))

print("\nTesting SET\n")
print(SH.SET('dev555-scalar', 1000))
print(SH.GET('dev555-scalar'))

new_df = pd.DataFrame({
    'Name': ['Tom', 'nick', 'krish', 'jack'],
    'Age': [20, 21, 19, 18]
})
print(new_df)
print(SH.SET('dev777-pd', new_df))
print(SH.GET('dev777-pd'))


geth_many_res = list(SH.GETMANY([
    { "topic_name": "dev123", "asOf": datetime.datetime(2024, 4, 18, 15, 0, 0) },
    { "topic_name": 'dev123', "asOf": datetime.datetime(2022, 12, 31)   },
    { "topic_name": 'dev123', "asOf": datetime.datetime(2022, 11, 1)    },
    { "topic_name": 'dev123', "asOf": datetime.datetime(2023, 2, 24)    }
]))

print(geth_many_res)

# Loading large number of topics
import time
start_ts = time.time()

get_many_res = list(SH.GETMANY([
    {
        "topic_name": "dev123",
        "tag": '1659994710026'
    },
    {
        "topic_name": "dev444",
        "tag": '1659994710026'
    },
    {
        "topic_name": "dev444",
    },
    {
        "topic_name": "dev444",
        "tag": 'latest'
    },
    {
        "topic_name": "dev777-pd",
    },
    {
        "topic_name": "dev555-scalar",
        "tag": 'latest'
    }
] * 100))

end_ts = time.time()
elapsed = end_ts - start_ts
print([ str(type(d)) for d in get_many_res ])
print(f'getmany for {len(get_many_res)} topics in {elapsed}s')
# getmany for 600 topics in 7.065880060195923s
```