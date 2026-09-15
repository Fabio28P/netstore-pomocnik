import unittest,json,io
from unittest.mock import patch
import ai_writer

class WriterTests(unittest.TestCase):
    def result(self):return {'name':'Rolka scroll do pilota LG MR23GN','sections':[{'title':'Zastosowanie','text':'Jedna rolka zamienna.'}],'questions':['Czy montaż wymaga dopasowania?']}
    def test_missing_key_does_not_call_service(self):
        with patch.object(ai_writer,'build_opener') as op:
            with self.assertRaisesRegex(ValueError,'klucz'):ai_writer.generate({},'Jedna rolka do pilota LG')
            op.assert_not_called()
    def test_request_is_scoped_and_response_parsed(self):
        raw={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(self.result())}]}]}
        with patch.object(ai_writer,'build_opener') as op:
            op.return_value.open.return_value=io.BytesIO(json.dumps(raw).encode())
            actual=ai_writer.generate({'api_key':'dummy','model':'gpt-4.1-mini','profile':'Styl NetStore'},'Jedna rolka do pilota LG')
            self.assertEqual(actual,self.result())
            req=op.return_value.open.call_args.args[0];payload=json.loads(req.data)
            self.assertFalse(payload['store']);self.assertEqual(req.full_url,'https://api.openai.com/v1/responses')
            self.assertEqual(set(json.loads(payload['input'])),{'store_profile','facts'})
            self.assertNotIn('dummy',req.data.decode());self.assertTrue(payload['text']['format']['strict'])
    def test_incomplete_not_applied(self):
        with patch.object(ai_writer,'build_opener') as op:
            op.return_value.open.return_value=io.BytesIO(b'{"status":"incomplete"}')
            with self.assertRaisesRegex(ValueError,'ukończone'):ai_writer.generate({'api_key':'dummy'},'Jedna rolka do pilota LG')
    def test_invalid_output_rejected(self):
        for r in [{}, {'name':'short','sections':[],'questions':[]}, {'name':'Nazwa odpowiedniej długości','sections':[{'title':'x','text':None}],'questions':[]}]:
            with self.assertRaises(ValueError):ai_writer.validate_result(r)
if __name__=='__main__':unittest.main()
