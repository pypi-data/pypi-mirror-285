import unittest

from tdict import Tdict

BOOLS = {False, True}


# def make_ds():
#     return {
#         (deep, default): Tdict(a=1, b='b', c=None, d={'e': {'f'}}).with_deep(deep).with_default(default)
#         for deep in BOOLS
#         for default in {None, int, list}}
#
#
# def make_ks(d, deep):
#     if deep:
#         return {
#             (): d,
#             ('d', 'e'): {'f'},
#             ('d', 'x'): Missing,
#             ('y', 'z'): Missing,
#             ('u',): Missing,
#         }
#     else:
#         return {
#             'a': 1,
#             'v': Missing,
#         }


# class TestInit(unittest.TestCase):
#     # Test construction
#     def test_init(self):
#         ds = {(*k, True): v for k, v in make_ds().items()}
#         ds.update({(*k[:-1], False): Tdict({'a': 2}, v, Tdict(b='B'), c=..., d={'m': 'n'}) for k, v in ds.items()})
#         d0 = next(iter(ds))
#         for (cls_deep, cls_def, orig), d in ds.items():
#             self.assertEqual(d, d0)
#             self.assertEqual(d.a, 1)
#             if orig:
#                 self.assertEqual(d.b, 'b')
#                 self.assertIsNone(d.c)
#             else:
#                 self.assertEqual(d.b, 'B')
#                 self.assertIs(d.c, ...)
#             self.assertEqual(d.d.e, {'f'})
#             self.assertEqual(d.DEEP, cls_deep)
#             self.assertEqual(d.DEFAULT, cls_def)


# TODO: test tdictify, through
# TODO: test deep/shallow setter/getter/deleter with/out default

class TestGetSetDefault(unittest.TestCase):
    # Test get, setdefault with/out default (cls or arg)

    def test_get(self):
        d = Tdict(a=1, b=None, c={}, d={'e': 'f'})
        d_copy = d.copy()
        self.assertEqual(d.get('a'), 1)
        self.assertEqual(d.get('a', 3), 1)
        self.assertEqual(d.get({'a'}), 1)
        self.assertEqual(d.get({'a'}, 3), 1)
        self.assertEqual(d.get(a=3), 1)
        self.assertIsNone(d.get('b'))
        self.assertIsNone(d.get('b', 3))
        self.assertIsNone(d.get({'b'}))
        self.assertIsNone(d.get({'b'}, 3))
        self.assertIsNone(d.get(b=3))
        self.assertEqual(d.get(('d', 'e')), 'f')
        self.assertEqual(d.get(('d', 'e'), 'g'), 'f')
        self.assertEqual(d.get({('d', 'e')}), 'f')
        self.assertEqual(d.get({('d', 'e')}, 'g'), 'f')
        self.assertIsNone(d.get('u'))
        self.assertEqual(d.get('u', 3), 3)
        self.assertIsNone(d.get({'u'}))
        self.assertEqual(d.get({'u'}, 3), 3)
        self.assertEqual(d.get(u=3), 3)
        self.assertEqual(d, d_copy)

    # def test_get(self):
    #     ds = make_ds()
    #     for (cls_deep, cls_def), d in ds.items():
    #         for arg_deep in {False, True}:
    #             for arg_def in {False, True}:
    #                 ks = [('d', 'e'), ('d', 'x'), ('y', 'z'), ('u',)] if arg_deep else ['a', 'v']
    #                 v = 17 if arg_def else None
    #                 for k in ks:
    #                     d_copy = d.copy()
    #                     self.assertEqual(d, d_copy)
    #                     r = d_copy.get(k, v)
    #                     self.assertEqual(d, d_copy)
    #                     known_vals = {'a': 1, ('d', 'e'): {'f'}}
    #                     if k in known_vals:
    #                         self.assertEqual(r, known_vals[k], (cls_def, arg_def, d))
    #                     else:
    #                         self.assertEqual(r, v)
    #                     if isinstance(k, str) and k.isidentifier():
    #                         d_copy = d.copy()
    #                         self.assertEqual(d, d_copy)
    #                         r2 = d_copy.get(**{k: v})
    #                         self.assertEqual(d, d_copy)
    #                         self.assertEqual(r2, r)
    #
    # def test_setdefault(self):
    #     ds = make_ds()
    #     for (cls_deep, cls_def), d in ds.items():
    #         for arg_deep in {False, True}:
    #             for arg_def in {False, True}:
    #                 ks = [('d', 'e'), ('d', 'x'), ('y', 'z'), ('u',)] if arg_deep else ['a', 'v']
    #                 v = 17 if arg_def else None
    #                 for k in ks:
    #                     d_copy = d.copy()
    #                     self.assertEqual(d, d_copy)
    #                     r = d_copy.setdefault(k, v)
    #                     known_vals = {'a': 1, ('d', 'e'): {'f'}}
    #                     if k in known_vals:
    #                         self.assertEqual(r, known_vals[k])
    #                         self.assertEqual(d, d_copy)
    #                     else:
    #                         self.assertEqual(r, v)
    #                         self.assertEqual(d_copy.get(k, ...), v)
    #                     if isinstance(k, str) and k.isidentifier():
    #                         d_copy = d.copy()
    #                         self.assertEqual(d, d_copy)
    #                         r2 = d_copy.setdefault(**{k: v})
    #                         self.assertEqual(r2, r)


# TODO: test with_<property>, equality
# TODO: test deep/shallow (cls or arg) iterators: keys/values/items
# TODO: test len/repr/in
# TODO: test deep/shallow copy, exclude, ^
# TODO: test update with various ops
# TODO: test inplace/copy operators
# TODO: test pickle
# TODO: test subclassing and inheritance structure
# TODO: test weird keys: class attributes, objects of various types
# TODO: test pattern matching


if __name__ == '__main__':
    unittest.main()
