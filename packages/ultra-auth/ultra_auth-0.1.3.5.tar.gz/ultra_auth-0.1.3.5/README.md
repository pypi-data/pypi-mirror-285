# ultra_auth

A compact Python client for managing a connection with the UltraDNS API. For the "official," and much more ambitious project, go [here](https://github.com/ultradns/python_rest_api_client).

## Features

- Support for authenticating with username and password, or directly with a bearer token.
- Automatic token refreshing when the token expires.
- Built-in handling of various content types.

## Installation

You can easily install `ultra_auth` using `pip`:

```bash
pip install ultra_auth
```

Once installed, you can use the ultra_auth module in your Python scripts:

```python
from ultra_auth import UltraApi
client = UltraApi(args)
```

## Usage

### Authenticating using Username and Password

```python
client = UltraApi(your_username, your_password)
```

### Authenticating using Bearer Token

```python
client = UltraApi(your_bearer_token, use_token=True)
```

### Authenticating using Bearer Token and Refresh Token

```python  
client = UltraApi(your_bearer_token, your_refresh_token, True)
``` 

### Making API Calls

```python
# Make a GET request
response = client.get("/ultra/api/endpoint")

# Make a POST request
response = client.post("/ultra/api/endpoint", payload={"key": "value"})

# ... similarly for PUT, PATCH, DELETE
```

## Response Handling

The client can return data in the form of dictionaries, strings, or bytes depending on the response content type.

For example:
1. The zone export endpoint, when requesting more than one zone, will return a zip file
2. The zone export endpoint, when requesting one zone, returns a plain text response
3. Most endpoints return JSON

## Debugging

### Debug Mode

When debug mode is enabled the client will print some verbose information about the request to stdout.

```python
client = UltraApi(your_username, your_password, debug=True)
# Toggle it on and off
client.toggle_debug()
```

### Pretty Print Mode

When pretty print mode is enabled the client will print the JSON response in a more human-readable format. This returns
a string instead of a dictionary, so be aware of that.

```python
client = UltraApi(your_username, your_password, pprint=True)
# Toggle it on and off
client.toggle_pprint()
```

### User-Agent

The client will send a unique User-Agent header with each request. By default, the User-Agent header will be "python-ultra-auth/vX.X.X (+repository_url)" where X.X.X is the version of the client. 

You can override this by passing a custom User-Agent header to the client.

```python
client = UltraApi(your_username, your_password, user_agent="my-custom-user-agent")
# This can be modified using the set_user_agent method. You return to the default, simply set it to None.
client.set_user_agent(None)
client.set_user_agent("my-new-custom-user-agent")
```

## Managing Tasks

Some endpoints return tasks, indicating that the operation might take some time to complete. For these scenarios, there's a `TaskHandler` helper class.

### Initialization

Create an instance of `UltraApi`.

```python
import ultra_auth
client = ultra_auth.UltraApi(your_username, your_password)
```

Pass this to the `TaskHandler`.

```python
task = ultra_auth.TaskHandler(client)
```

### Getting the Task ID

When an endpoint returns a task, the response will contain a `task_id`. 

```python
response = client.post('/v3/zones/export', {'zoneNames':['your_domain_name.com']})
task_id = response['task_id']
```

### Checking Task Status

You can check the current status of a task using `check` or implicitly wait for it to be completed using `wait`.

```python
print(task.check(task_id))
print(task.wait(task_id, 5))
```

The second `wait` arg is the number of seconds to pause between polling. The default is 10.

### Task Results

Once a task is completed, you can retrieve the result using the `result` method:

```python
print(task.result(task_id))
```

## Note

Using a bearer token without a refresh token means the client state will expire in approximately 1 hour (assuming the token was just generated). The client won't stop you from doing this, but be warned.

## Contribute

Contributions are always welcome! Please open a pull request with your changes, or open an issue if you encounter any problems or have suggestions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
