from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class
# from sqlalchemy_easy_softdelete.hook import IgnoredTable
import datetime

class SoftDeleteMixin(generate_soft_delete_mixin_class(
    # This table will be ignored by the hook
    # even if the table has the soft-delete column
    # ignored_tables=[IgnoredTable(table_schema="public", name="cars"),]
)):
    # type hint for autocomplete IDE support
    deleted_at: datetime 