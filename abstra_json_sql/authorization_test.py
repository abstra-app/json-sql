from unittest import TestCase

from .authorization import Permissions


class TestPermissions(TestCase):
    def test_select(self):
        p = Permissions(default=False)
        p.grant("SELECT", "users", "age > 18")

        self.assertFalse(p.allowed("select * from users"))
        self.assertTrue(p.allowed("select * from users where age > 18"))

        p.revoke("SELECT", "users", "age < 21")
        self.assertFalse(p.allowed("select * from users where age < 21"))

    def test_select_complex(self):
        p = Permissions(default=False)
        p.grant("SELECT", "orders", "status = 'completed' AND total > 100")

        self.assertFalse(p.allowed("select * from orders where status = 'pending'"))
        self.assertFalse(p.allowed("select * from orders where total <= 100"))
        self.assertTrue(
            p.allowed("select * from orders where status = 'completed' AND total > 100")
        )

        p.revoke("SELECT", "orders", "customer_id = 42")
        self.assertFalse(
            p.allowed(
                "select * from orders where customer_id = 42 AND status = 'completed' AND total > 100"
            )
        )

    def test_insert(self):
        p = Permissions(default=False)
        p.grant("INSERT", "users", "name = 'Alice'")

        self.assertFalse(p.allowed("insert into users (name, age) values ('Bob', 25)"))
        self.assertTrue(p.allowed("insert into users (name, age) values ('Alice', 30)"))

        p.revoke("INSERT", "users", "age = 18")
        self.assertFalse(
            p.allowed("insert into users (name, age) values ('Alice', 18)")
        )
        self.assertTrue(p.allowed("insert into users (name, age) values ('Alice', 20)"))

    def test_update(self):
        p = Permissions(default=False)
        p.grant("UPDATE", "users", "age < 65")

        self.assertFalse(p.allowed("update users set age = age + 1 where age >= 65"))
        self.assertTrue(p.allowed("update users set age = age + 1 where age < 65"))

        p.revoke("UPDATE", "users", "status = 'inactive'")
        self.assertFalse(
            p.allowed("update users set age = age + 1 where status = 'inactive'")
        )
        self.assertFalse(
            p.allowed("update users set age = age + 1 where status = 'active'")
        )

        p.grant("UPDATE", "users", "status = 'active'")
        self.assertTrue(
            p.allowed("update users set age = age + 1 where status = 'active'")
        )

    def test_delete(self):
        p = Permissions(default=False)
        p.grant("DELETE", "users", "status = 'inactive'")

        self.assertFalse(p.allowed("delete from users where status = 'active'"))
        self.assertTrue(p.allowed("delete from users where status = 'inactive'"))

        p.revoke("DELETE", "users", "age < 18")
        self.assertFalse(
            p.allowed("delete from users where status = 'inactive' and age < 18")
        )
        self.assertTrue(
            p.allowed("delete from users where status = 'inactive' and age >= 18")
        )
