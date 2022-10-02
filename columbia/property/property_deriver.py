from typing import List, Tuple
from columbia.memo.expr_group import Group, GroupExpr
from plan.plan import PhyiscalType
from plan.properties import Property, PropertySet, make_replica


class PropertyDeriver:
    def __init__(self, plan: GroupExpr, require_prop: PropertySet) -> None:
        self.gexpr = plan
        self.require_prop = require_prop

    def derive(self) -> List[Tuple[PropertySet, ...]]:
        assert not self.gexpr.is_logical()
        match self.gexpr.type():
            case PhyiscalType.NLJoin:
                return self.derive_join()
            case PhyiscalType.Scan:
                return [()]
            case _:
                assert False, f"Unsupported Physical Plan Type{self.gexpr.type}"

    def compatible(self, prop: Property, expr: Group):
        return True

    def derive_join(self) -> List[Tuple[PropertySet, ...]]:
        # 1. Singleton Join
        res: List[Tuple[PropertySet, ...]] = []
        res.append((PropertySet(), PropertySet()))

        # 2. Broadcast Join
        res.append((PropertySet(), make_replica()))

        # 3. Shuffle Join has no supported yet
        return res
