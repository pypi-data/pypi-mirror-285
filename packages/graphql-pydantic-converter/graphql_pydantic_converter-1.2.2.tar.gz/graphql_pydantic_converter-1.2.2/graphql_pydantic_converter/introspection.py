def generate_type(depth: int) -> str:
    if depth <= 0:
        return ''
    return f"""ofType {{ name kind {generate_type(depth - 1)} }}"""


def generate_schema_request(depth: int) -> str:
    request = f"""{{
  __schema {{
    queryType {{
      name
    }}
    subscriptionType {{
      name
    }}
    mutationType {{
      name
    }}
    types {{
      kind
      name
      {generate_type(depth)}
      fields {{
        name
        args {{
          name
          type {{
            name
            kind
            {generate_type(depth)}
          }}
        }}
        type {{
          name
          kind
          {generate_type(depth)}
        }}
      }}
      inputFields {{
        name
        type {{
          kind
          name
          {generate_type(depth)}
        }}
      }}
      interfaces {{
        name
        kind
        {generate_type(depth)}
      }}
      enumValues {{
        name
      }}
    }}
  }}
}}
"""
    return request
