from typing import List, Tuple
from columbia.memo.expr_group import GroupExpr
from plan.plan import PhyiscalType
from plan.properties import PropertySet


class PropertyDeriver:
    """
    This deriver receive a reuqire prop and a expression
    It derive all the possible prop that should be pushdown to children
    """

    def __init__(self, plan: GroupExpr, require_prop: PropertySet) -> None:
        self.gexpr = plan
        self.require_prop = require_prop

    def derive(self) -> List[Tuple[PropertySet, Tuple[PropertySet, ...]]]:
        """
        We can derive the possible children properties in following strategies
            1. pass all possible properties
            2. don't pass properties
            3. pass all combination of possible properties
        Right now we use strategy 1
        """
        assert (
            not self.gexpr.is_logical()
        ), "only physical operator can be derived properties"
        match self.gexpr.type():
            case PhyiscalType.NLJoin:
                return self.derive_nl_join()
            case PhyiscalType.Scan:
                return [(PropertySet(), ())]
            case _:
                assert False, f"Unsupported Physical Plan Type{self.gexpr.type}"

    def derive_nl_join(self) -> List[Tuple[PropertySet, Tuple[PropertySet, ...]]]:
        res: List[Tuple[PropertySet, Tuple[PropertySet, ...]]] = []
        # Pushdown nothing
        res.append((PropertySet(), (PropertySet(), PropertySet())))
        # Pushdown the property of outter table
        outter_prop = PropertySet()
        for prop in self.require_prop:
            if prop.tables.issubset(self.gexpr.children[0].tables):
                outter_prop.add_property(prop)
        if not outter_prop.empty():
            res.append((outter_prop, (outter_prop, PropertySet())))
        return res
