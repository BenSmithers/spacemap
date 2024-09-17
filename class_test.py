class Foo(object): pass
class Bar(Foo): pass
class Baz(Foo): pass
class Bing(Bar): pass

print([cls.__name__ for cls in Foo.__subclasses__()])

print(Foo.__subclasses__())
