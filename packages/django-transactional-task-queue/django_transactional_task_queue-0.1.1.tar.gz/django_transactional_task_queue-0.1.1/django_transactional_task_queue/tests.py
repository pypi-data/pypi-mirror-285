from unittest import TestCase

from django_transactional_task_queue.celery import shared_task
from django_transactional_task_queue.models import Task


@shared_task
def foo(a, b, c):
    print("EXECUTING FUNCTION", a, b, c)


class PersonTestCase(TestCase):
    def test_dummy(self):
        foo(1, 2, 3)
        foo.delay(1, 2, 3)
        foo.delay(1, b=2, c=3)

    def test_exec(self):
        Task(
            task="django_transactional_task_queue.tests.foo", args=[1, 2, 3], kwargs={}
        ).execute()
        Task(
            task="django_transactional_task_queue.tests.foo",
            args=[1],
            kwargs={"b": 2, "c": 3},
        ).execute()
