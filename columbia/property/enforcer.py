from plan.plan import EnforceType, PlanContent
from plan.properties import Property, PropertyType
from columbia.memo.expr_group import Group, GroupExpr
from plan.properties import PropertySet


class Enforcer:
    """
    Enfocer will from bottom to up pop the enfoce expr until the requsted_prop is satisfied
    """

    def __init__(
        self, requsted_prop: PropertySet, output_prop: PropertySet, child_group: Group
    ) -> None:
        self.requsted_prop = requsted_prop
        self.output_prop = output_prop
        self.child_group = child_group
        # TODO: we only support the followinf rule:
        #   order a -> group by a
        #   order a,b,c -> order by a,b
        # TODO: Support functional dependencies
        self.enforce_properties = PropertySet()
        for prop in self.requsted_prop:
            if not self.output_prop.compat(prop):
                self.enforce_properties.add_property(prop)

    def enforce(self, prop: Property, child_group: Group):
        match prop.type:
            case PropertyType.Sort:
                return GroupExpr(
                    (child_group,), PlanContent(EnforceType.Sort, prop.expressions)
                )
            case PropertyType.Group:
                return GroupExpr(
                    (child_group,), PlanContent(EnforceType.Hash, prop.expressions)
                )

    def __iter__(self):
        return self

    def __next__(self):
        if self.enforce_properties.empty():
            raise StopIteration
        prop = self.enforce_properties.pop_property()
        self.output_prop.add_property(prop)
        return self.enforce(prop, self.child_group), self.output_prop

    def output_property(self):
        return self.output_prop

    def cost(self):
        return 0.9
