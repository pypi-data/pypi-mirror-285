import unittest

from goja_py import execute


class TestExecute(unittest.IsolatedAsyncioTestCase):
    def test_maybe_two(self):
        self.assertEqual(2, execute('1 + 1;'))

    def test_reference_error(self):
        with self.assertRaises(RuntimeError) as ctx:
            execute('error += 1')
        self.assertIn('is not defined', repr(ctx.exception))

    def test_json_stringify(self):
        self.assertEqual({'test': True}, execute('JSON.stringify({"test": true})'))

    def test_async_wrapper(self):
        code = """
        ((A,B) => {
        globalThis = {console: globalThis.console};
        try {
            let main = async (message) => { console.log('test'); B=A+5; return B; }
            (async () => await main('result'))();
            return JSON.stringify({A,B});
        }
        catch (error) {
            return JSON.stringify({ error: `${error.name}: ${error.message}` });
        }
        })(5,null);
        """
        self.assertEqual({'A': 5, 'B': None}, execute(code))

    def test_global_this(self):
        self.assertEqual(True, execute('error = true; globalThis["error"] = true;'))
        self.assertEqual({}, execute('JSON.stringify(globalThis)'))
