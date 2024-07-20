from viggocore.common import manager, exception
from viggocore.common.subsystem import operation
from viggocore.common.subsystem.pagination import Pagination
from viggocore.subsystem.capability_functionality.resource \
    import CapabilityFunctionality
from viggocore.subsystem.policy_functionality.resource \
    import PolicyFunctionality
from viggocore.subsystem.functionality.resource \
    import Functionality
from sqlalchemy import or_


class GetAvailableFunctionalitys(operation.List):

    def pre(self, **kwargs):
        self.role_id = kwargs.get('role_id', None)
        if self.role_id is None:
            raise exception.BadRequest('role_id is required')
        self.application_id = kwargs.get('application_id', None)
        if self.application_id is None:
            raise exception.BadRequest('application_id is required')
        return super().pre(**kwargs)

    def do(self, session, **kwargs):
        query = session.query(Functionality). \
            join(CapabilityFunctionality,
                 CapabilityFunctionality.functionality_id == Functionality.id,
                 isouter=True). \
            join(PolicyFunctionality,
                 PolicyFunctionality.capability_functionality_id ==  # noqa
                 CapabilityFunctionality.id, isouter=True). \
            filter(
                or_(CapabilityFunctionality.application_id != self.application_id,  # noqa
                    CapabilityFunctionality.application_id == None))  # noqa
        query = query.filter(
            or_(PolicyFunctionality.role_id != self.role_id,
                PolicyFunctionality.role_id == None))  # noqa
        query = self.manager.apply_filters(query, Functionality, **kwargs)
        query = query.distinct()

        dict_compare = {'capability_functionality.': CapabilityFunctionality,
                        'policy_functionality.': PolicyFunctionality}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Functionality, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Functionality)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class GetSelectedFunctionalitys(operation.List):

    def pre(self, **kwargs):
        self.role_id = kwargs.get('role_id', None)
        if self.role_id is None:
            raise exception.BadRequest('role_id is required')
        self.application_id = kwargs.get('application_id', None)
        if self.application_id is None:
            raise exception.BadRequest('application_id is required')
        return super().pre(**kwargs)

    def do(self, session, **kwargs):
        query = session.query(Functionality). \
            join(CapabilityFunctionality,
                 CapabilityFunctionality.functionality_id == Functionality.id,
                 isouter=True). \
            join(PolicyFunctionality,
                 PolicyFunctionality.capability_functionality_id ==  # noqa
                 CapabilityFunctionality.id, isouter=True). \
            filter(
                PolicyFunctionality.role_id == self.role_id). \
            filter(
                CapabilityFunctionality.application_id == self.application_id)
        query = self.manager.apply_filters(query, Functionality, **kwargs)
        query = query.distinct()

        dict_compare = {'capability_functionality.': CapabilityFunctionality,
                        'policy_functionality.': PolicyFunctionality}
        query = self.manager.apply_filters_includes(
            query, dict_compare, **kwargs)
        query = query.distinct()

        total_rows = None
        if self.manager.with_pagination(**kwargs):
            total_rows = query.count()

        pagination = Pagination.get_pagination(Functionality, **kwargs)
        if pagination.order_by is not None:
            pagination.adjust_order_by(Functionality)
        query = self.driver.apply_pagination(query, pagination)
        result = query.all()

        return (result, total_rows)


class Delete(operation.Delete):

    def pre(self, session, id, **kwargs):
        super().pre(session, id=id)
        policies = self.manager.api.policy_functionalities().list(
            capability_functionality_id=id)
        if policies:
            message = 'You can\'t remove this capability because' + \
                ' there are policies associated'
            raise exception.BadRequest(message)
        return True


class Manager(manager.CommonManager):

    def __init__(self, driver):
        super(Manager, self).__init__(driver)
        self.get_available_functionalities = GetAvailableFunctionalitys(self)
        self.get_selected_functionalities = GetSelectedFunctionalitys(self)
        self.delete = Delete(self)
