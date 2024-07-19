from __future__ import annotations

from abc import ABC

from lark import Lark, Transformer

from mathesis.forms import (
    Atom,
    Conditional,
    Conjunction,
    Disjunction,
    Negation,
    Particular,
    Universal,
)

_latex_symbols = {
    "⊥": r"\bot",
    "⊤": r"\top",
}


class ToFml(Transformer):
    def atom(self, v):
        if len(v) == 1:
            return Atom(*v, latex=_latex_symbols.get(v[0], None))
        else:
            return Atom(v)

    def negation(self, v):
        return Negation(*v)

    def universal(self, v):
        return Universal(*v)

    def particular(self, v):
        return Particular(*v)

    def conjunction(self, v):
        return Conjunction(*v)

    def disjunction(self, v):
        return Disjunction(*v)

    def conditional(self, v):
        return Conditional(*v)


class Grammar(ABC):
    """Abstract class for grammars."""

    grammar_rules: str

    def __repr__(self):
        return self.grammar_rules

    # @abstractmethod
    # def parse(self, text_or_list: str | list):
    #     raise NotImplementedError()

    def __init__(self):
        self.grammar = Lark(self.grammar_rules, start="fml")

    def parse(self, text_or_list: str | list):
        """Parse a string or a list of strings into formula object(s).

        Args:
            text_or_list (str | list): A string or a list of strings representing formula(s).
        """

        # print(fml_strings)
        if isinstance(text_or_list, list):
            fml_strings = text_or_list
            fmls = []
            for fml_string in fml_strings:
                tree = self.grammar.parse(fml_string)
                fml = ToFml().transform(tree)
                fmls.append(fml)
            return fmls
        else:
            fml_string = text_or_list
            tree = self.grammar.parse(fml_string)
            fml = ToFml().transform(tree)
            return fml


class BasicPropositionalGrammar(Grammar):
    """Basic grammar for the propositional language."""

    grammar_rules = r"""
?fml: conjunction
    | disjunction
    | conditional
    | negation
    | atom
    | _subfml

ATOM : /\w+/ | "⊤" | "⊥"

atom : ATOM
negation : "¬" _subfml
conjunction : (conjunction | _subfml) "∧" _subfml
disjunction : (disjunction | _subfml) "∨" _subfml
conditional : _subfml "{conditional_symbol}" _subfml
necc : "□" _subfml
poss : "◇" _subfml

_unary : negation | necc | poss
_subfml : "(" fml ")" | _unary | atom

%import common.WS
%ignore WS
""".lstrip()

    def __init__(self, symbols={"conditional": "→"}):
        self.grammar_rules = self.grammar_rules.format(
            conditional_symbol=symbols["conditional"]
        )
        super().__init__()


class BasicGrammar(BasicPropositionalGrammar):
    """Basic grammar for the first-order language."""

    grammar_rules = r"""
?fml: conjunction
    | disjunction
    | conditional
    | negation
    | universal
    | particular
    | atom
    | _subfml

PREDICATE: /\w+/ | "⊤" | "⊥"
TERM: /\w+/

atom : PREDICATE ("(" TERM ("," TERM)* ")")?
negation : "¬" _subfml
conjunction : (conjunction | _subfml) "∧" _subfml
disjunction : (disjunction | _subfml) "∨" _subfml
conditional : _subfml "{conditional_symbol}" _subfml
necc : "□" _subfml
poss : "◇" _subfml
universal : "∀" TERM _subfml
particular : "∃" TERM _subfml

_unary : negation | necc | poss | universal | particular
_subfml : "(" fml ")" | _unary | atom

%import common.WS
%ignore WS
""".lstrip()
