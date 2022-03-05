from functools import wraps


def log(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        print(f"Called \"{f.__name__}\"")
        f(*args, **kwargs)
    
    return wrapped

if __name__ == "__main__":
    @log
    def test(a):
        print("Coucou", a)
    
    test(12)