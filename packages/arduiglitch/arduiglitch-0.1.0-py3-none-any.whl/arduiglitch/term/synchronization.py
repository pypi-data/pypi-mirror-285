"""
This file is a copy/paste of the thread synchronization example from the
wrap module documentation: https://wrapt.readthedocs.io/en/latest/examples.html

---

Copyright (c) 2013-2023, Graham Dumpleton
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

from wrapt import FunctionWrapper
from threading import Lock, RLock


def synchronized(wrapped):
    """
    This function can be used in various ways to provide memory safety.

    It is a copy/paste of the thread synchronization example from the
    `wrap` module documentation: https://wrapt.readthedocs.io/en/latest/examples.html

    Some examples:

    With `my_resource` supporting adding attributes:

    .. code-block:: python

        with synchronized(my_resource):
            # Do something while `my_resource` is locked
        # Starting here, `my_resource` is unlocked and can be accessed by other
        # threads that also use `with synchronized(my_resource):`

    On a class method:

    .. code-block:: python

        @synchronized
        def some_function(self):
            # Do something while self is locked

    What actually happens behind the hood is that a `RLock` is added to the
    resource's attributes if it is the first time it is given to `synchronized`.
    This lock is then acquired and released automatically depending on if the
    function is used as a context manager or a decorator.
    """

    def _synchronized_lock(context):
        # Attempt to retrieve the lock for the specific context.

        lock = vars(context).get('_synchronized_lock', None)

        if lock is None:
            # There is no existing lock defined for the context we
            # are dealing with so we need to create one. This needs
            # to be done in a way to guarantee there is only one
            # created, even if multiple threads try and create it at
            # the same time. We can't always use the setdefault()
            # method on the __dict__ for the context. This is the
            # case where the context is a class, as __dict__ is
            # actually a dictproxy. What we therefore do is use a
            # meta lock on this wrapper itself, to control the
            # creation and assignment of the lock attribute against
            # the context.

            meta_lock = vars(synchronized).setdefault(
                '_synchronized_meta_lock', Lock())

            with meta_lock:
                # We need to check again for whether the lock we want
                # exists in case two threads were trying to create it
                # at the same time and were competing to create the
                # meta lock.

                lock = vars(context).get('_synchronized_lock', None)

                if lock is None:
                    lock = RLock()
                    setattr(context, '_synchronized_lock', lock)

        return lock

    def _synchronized_wrapper(wrapped, instance, args, kwargs):
        # Execute the wrapped function while the lock for the
        # desired context is held. If instance is None then the
        # wrapped function is used as the context.

        with _synchronized_lock(instance or wrapped):
            return wrapped(*args, **kwargs)

    class _FinalDecorator(FunctionWrapper):

        def __enter__(self):
            self._self_lock = _synchronized_lock(self.__wrapped__)
            self._self_lock.acquire()
            return self._self_lock

        def __exit__(self, *args):
            self._self_lock.release()

    return _FinalDecorator(wrapped=wrapped, wrapper=_synchronized_wrapper)
