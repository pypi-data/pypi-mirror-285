from typing import Any


class ModelHooksMixin:
    def pre_init(self, *, is_new_object: bool, kwargs: dict[str, Any]) -> None:
        """
        This hook is called just before the model is initialized and the built-in validations are executed.
        This hook is useful for setting default values for the model fields or for validating the keyword arguments.

        :param is_new_object: indicates if the model is being initialized as a new record or existing one.
        :type is_new_object: bool
        :param kwargs: dictionary of keyword arguments passed to the model constructor.
        :type kwargs: dict[str, Any]

        :return: does not return anything.
        :rtype: None
        """
        pass

    def post_init(self, *, is_new_object: bool, kwargs: dict[str, Any]) -> None:
        """
        This hook is called just after the model is initialized and the built-in validations are executed.
        This hook also is useful for setting default values for the model fields or for extra validating the keyword
        arguments.

        :param is_new_object: indicates if the model is being initialized as a new record or existing one.
        :type is_new_object: bool
        :param kwargs: dictionary of keyword arguments passed to the model constructor.
        :type kwargs: dict[str, Any]

        :return: does not return anything.
        :rtype: None
        """
        pass

    def pre_create(self) -> None:
        """
        This hook is called just before the new record of model is saved to the database.
        It doesn't accept any arguments.
        This hook is useful for setting default values for the model fields or for validating the model before
        saving it to the database.
        At this stage object is not saved to the database yet.

        :return: does not return anything.
        :rtype: None
        """
        pass

    def post_create(self) -> None:
        """
        This hook is called just after the new record of model is saved to the database.
        It doesn't accept any arguments.
        This hook is useful for adding extra logic after the model is saved to the database.
        For example, you can send a notification to the user that the new record is created.
        At this stage object is already saved to the database, and can be referenced by other records.

        :return: does not return anything.
        :rtype: None
        """

    def pre_update(self) -> None:
        """
        This hook is called just before the existing record of model is updated in the database.
        It doesn't accept any arguments.
        This hook is useful for validating the model before updating it in the database.
        At this stage object is not updated in the database yet, so previous_version may return None.

        :return: does not return anything.
        :rtype: None
        """
        pass

    def post_update(self) -> None:
        """
        This hook is called just after the existing record of model is updated in the database.
        It doesn't accept any arguments.
        This hook is useful for adding extra logic after the model is updated in the database.
        For example, you can send a notification to the user that the record is updated.
        At this stage object is already updated in the database, and calling previous_version will return the
        version of the object before the update.

        :return: does not return anything.
        :rtype: None
        """
        pass

    def pre_delete(self) -> None:
        """
        This hook is called just before the existing record of model is deleted from the database.
        It doesn't accept any arguments.
        This hook is useful for validating the model before deleting it from the database.
        At this stage object is not deleted from the database yet.

        :return: does not return anything.
        :rtype: None
        """
        pass

    def post_delete(self) -> None:
        """
        This hook is called just after the existing record of model is deleted from the database.
        It doesn't accept any arguments.
        This hook is useful for adding extra logic after the model is deleted from the database.
        For example, you can send a notification to the user that the record is deleted.

        :return: does not return anything.
        :rtype: None
        """
        pass
