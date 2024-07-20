"""
RPC utility functions for the bec_lib package.
"""


class user_access:

    def __init__(self, meth):
        """
        Decorator to mark <device_class> methods to be accessible from the bec client

        Args:
            meth: method to be marked as accessible

        Examples:
            >>> @user_access
            >>> def my_method(self, *args, **kwargs):
            >>>     return fcn(self, *args, **kwargs)

        """
        self.meth = meth

    def __set_name__(self, owner, name):
        """Write registered method into the owner class USER_ACCESS list for the bec_ipython_client"""
        if not hasattr(owner, "USER_ACCESS"):
            owner.USER_ACCESS = []
        if name not in owner.USER_ACCESS:
            owner.USER_ACCESS.append(name)

        setattr(owner, name, self.meth)
