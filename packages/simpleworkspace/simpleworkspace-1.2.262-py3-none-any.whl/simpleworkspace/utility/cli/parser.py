from typing import TypeVar as _TypeVar, Generic as _Generic, Type as _Type, Callable as _Callable, Iterable as _Iterable, Literal as _Literal, Sequence as _Sequence
import argparse as _argparse

_T = _TypeVar('_T')

class Arguments:
    class Template:
        """
        Example blueprint::

            def __init__(self):
                #Value will be stored in property name, argument name specifiers are what is typed on the cli
                self.ToggleFlagName = Arguments.ArgumentToggle('--ToggleFlag-Name', help='...')
                self.PositionalArguments = Arguments.ArgumentList()
                self.StringList = Arguments.ArgumentList('--string-list')
                self.Number = Arguments.Argument('-n', '--number', type=int, help="...", required=True)
                self.String = Arguments.Argument('-s', '--string', default="hello", help="...")
        """


    def __init__(self, **kwargs):
        self.default = None
        self.type:_Type = None
        self.name:tuple[str] = None
        self.help:str = None
        self.required:bool = None
        self.choices:_Iterable = None
        self.nArgs = None
        self.useBooleanToggle = False
        self.template: self.Template = None
        self.__dict__.update(kwargs)

    @classmethod
    def SubParser(cls, template: _Type[_T]|Template, name:str=None, help:str=None) -> _T:
        """
        Creates a sub group for the cli interface, the resulting arguments in the sub groups gets their own namespaces

        :param template: the subTemplate to implement
        :param name: the positional argument name to navigate to this group, if not specified defaults to reflected property name

        Example::

            class Group1Template(Arguments.Template):
                Number = Arguments.Argument('-n', '--number', type=int, help="...")

            class NestedArgumentTemplate(Arguments.Template):
                Group1 = Arguments.Group(Group1Template)
            
            #CLI usage: "... Group1 --Number 10"
        """
        if(name):
            name = [name]
        return cls(**locals())
    
    @classmethod
    def Argument(cls, *name:str, default=None, type:_Type[_T]|_Callable[[str], _T]=str, choices:_Iterable=None, required:bool=None, help:str=None) -> _T:
        """
        Create a new argument

        :param name: The names or flags for the argument. If no flag name is supplied then it becomes a positional argument.
        :param default: The default value of the argument.
        :param type: The type of the argument (str,int,bool) or a callback that recieves str as input.
        :param choices: Specifies which values are allowed for this argument
        :param required: Whether the argument is required.
        :param help: The help description for the argument.
        """
                
        return cls(**locals())

    @classmethod
    def ArgumentList(cls, *name:str, default=None, type:_Type[_T]|_Callable[[str], _T]=str, nArgs:int|_Literal['?','*','+','...']='+',choices:_Iterable=None, required:bool=None, help:str=None) -> list[_T]:
        """
        Create a new argument that accepts a list of values.

        :param name: The names or flags for the argument. If no flag name is supplied then it becomes a positional argument.
        :param default: The default value of the argument.
        :param type: The type of the argument (str,int,bool) or a callback that recieves str as input.
        :param nArgs: number of args to accept, special symbols(?: 0 or 1, *: 0 or more, +: atleast 1, '...': all rest of the arguments even if they are prefixed)
        :param choices: Specifies which values are allowed for this argument
        :param required: Whether the argument is required.
        :param help: The help description for the argument.
        """
        return cls(**locals())

    @classmethod
    def ArgumentToggle(cls, *name:str, help:str=None) -> bool:
        """
        Create a new boolean toggle flag without value, defaults to false when flag is not found, true otherwise
        
        :param name: The names or flags for the argument.
        :param help: The help description for the argument.
        """
        if(not name):
            raise ValueError("A Toggle flag must have a name identifier")
        return cls(**locals(), useBooleanToggle=True)

class _Nestedspace(_argparse.Namespace):
    def __setattr__(self, name:str, value):
        if '.' in name:
            group,name = name.split('.',1)
            ns = getattr(self, group, _Nestedspace())
            setattr(ns, name, value)
            self.__dict__[group] = ns
        else:
            self.__dict__[name] = value

class CLIParser(_Generic[_T]):
    def __init__(self, topTemplate:_Type[_T], description:str=None, add_help=True):
        topTemplate:Arguments.Template = topTemplate()
        self._SubGroupNamespaces = []
        self.nativeParser = _argparse.ArgumentParser(description=description, add_help=add_help)
        self._Map_Parser(self.nativeParser, topTemplate)

    def _Map_Parser(self, parser:_argparse.ArgumentParser, template:_Type[_T], namespace:list[str]=None):
        subparsers = None
        for key,argument in template.__dict__.items():
            if not(isinstance(argument, Arguments)):
                continue

            KeyNS = (*namespace, key) if namespace else (key,)

            #argparse requires some params to not be inputted at all if they are None
            args = []
            kwargs = {}

            if(argument.help is not None):
                kwargs['help'] = argument.help

            if(argument.template is not None): #subparser argument type
                if(subparsers is None):
                    subparsers = parser.add_subparsers()
                subparserCommand = argument.name[0] if argument.name else key
                subParser = subparsers.add_parser(subparserCommand, **kwargs)
                self._SubGroupNamespaces.append(KeyNS)
                self._Map_Parser(subParser, argument.template(), namespace=KeyNS)
                continue

            if(argument.name):
                args.extend(argument.name)
            
            kwargs['dest'] = '.'.join(KeyNS)
            if(argument.useBooleanToggle):
                parser.add_argument(*args, action="store_true", **kwargs)
                continue
            
            if(argument.nArgs is not None):
                kwargs['nargs'] = argument.nArgs
            if(argument.type is not None):
                kwargs['type'] = argument.type
            if(argument.default is not None):
                kwargs['default'] = argument.default
            if(argument.required is not None):
                kwargs['required'] = argument.required
            if(argument.choices is not None):
                kwargs['choices'] = argument.choices

            parser.add_argument(*args, **kwargs)
    
    def Parse(self, arguments:_Sequence[str]=None, ignoreUnkownArguments=True) -> _T:
        argNS = _Nestedspace()

        if(ignoreUnkownArguments):
            self.nativeParser.parse_known_args(args=arguments, namespace=argNS)
        else:
            self.nativeParser.parse_args(args=arguments, namespace=argNS)
        

        #defaulting null variables for subparsers to mimic the default flow of when an arg is not supplied it is None
        for keyNS in self._SubGroupNamespaces:
            current_level = argNS.__dict__
            for nsPart in keyNS:
                if nsPart not in current_level:
                    current_level[nsPart] = None
                    break
                elif current_level[nsPart] is None:
                    break
                current_level = current_level[nsPart].__dict__

        return argNS
