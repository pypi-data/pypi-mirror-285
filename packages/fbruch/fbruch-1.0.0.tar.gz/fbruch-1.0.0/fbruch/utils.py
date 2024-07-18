cookie_to_string = lambda data: ';'.join(f'{key}={value}' for key, value in data.items())
password_generator = lambda name: [x+str(y) for x in name.split(' ') for y in [123, 1234, 12345, 321]] + [x +' '+ x for x in name.split(' ')] + [name]
templates = lambda status, data={}, error=None: {'author': 'errucha', 'data': data, 'error': error}


