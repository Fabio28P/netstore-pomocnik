import os,tempfile
os.environ["NETSTORE_DATA"]=tempfile.mkdtemp(prefix="netstore-v12-")
import json,io,unittest
from unittest.mock import patch
import parameters,ai_writer,app
from urllib.error import HTTPError

class V12Tests(unittest.TestCase):
 def test_product_parameters_required_and_routed(self):
  defs=parameters.merge([{'id':'1','name':'Kod producenta','type':'string','required':False}], [{'id':'1','name':'Kod producenta','type':'string','required':True}])
  with self.assertRaisesRegex(ValueError,'Kod producenta'):parameters.normalize({},defs)
  d={'offer_parameters':[{'id':'1','values':['NET-MR23']}],'product_parameters':[]}
  parameters.normalize(d,defs);self.assertEqual(d['product_parameters'][0]['values'],['NET-MR23']);self.assertEqual(d['offer_parameters'],[])
 def test_existing_product_does_not_need_new_product_fields(self):
  d={'product_id':'existing'};parameters.normalize(d,[{'id':'1','name':'Model','requiredForProduct':True,'options':{'describesProduct':True}}])
 def test_html_escaped_and_bold_lists(self):
  rendered=app.rich_text('**Jedna rolka**\n- <script>\n- Czarna')
  self.assertIn('<b>Jedna rolka</b>',rendered);self.assertIn('<ul>',rendered);self.assertNotIn('<script>',rendered)
 def test_keys_do_not_cross_providers(self):
  h=object.__new__(app.Handler)
  app.save('ai-config',{'provider':'openai','api_key':'openai-secret'})
  h.action('/ai-config',{'provider':'gemini','api_key':'','model':'gemini-2.5-flash-lite'})
  self.assertEqual(app.read('ai-config')['api_key'],'')
 def test_folder_restores_offer_and_pending(self):
  h=object.__new__(app.Handler)
  app.save('draft',{'local_id':'A','folder':'root/A','name':'A'})
  app.save('offer-production',{'local_id':'A','id':'123','pending':True})
  h.action('/switch-folder',{'folder':'root/B','draft':{'local_id':'B','name':'B'}})
  self.assertEqual(app.read('offer-production'),{})
  h.action('/switch-folder',{'folder':'root/A','draft':{'local_id':'wrong'}})
  self.assertEqual(app.read('draft')['local_id'],'A');self.assertTrue(app.read('offer-production')['pending'])
  app.save('offer-production',{})
 def test_gemini_success(self):
  result={'name':'Rolka zamienna do pilota LG','sections':[{'title':'Kupujesz','text':'**Jedna rolka**'}],'questions':[]}
  response={'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(result)}]}}]}
  with patch.object(ai_writer,'build_opener') as op:
   op.return_value.open.return_value=io.BytesIO(json.dumps(response).encode())
   self.assertEqual(ai_writer.generate({'provider':'gemini','api_key':'dummy'},'Jedna rolka do pilota LG.'),result)
   req=op.return_value.open.call_args.args[0];self.assertNotIn('dummy',req.full_url);self.assertNotIn('images',req.data.decode())
 def test_rate_limit_no_fallback(self):
  with patch.object(ai_writer,'build_opener') as op:
   op.return_value.open.side_effect=HTTPError('url',429,'limit',{},None)
   with self.assertRaisesRegex(ValueError,'limit'):ai_writer.generate({'provider':'gemini','api_key':'dummy'},'Jedna rolka do pilota LG.')
   self.assertEqual(op.return_value.open.call_count,1)
if __name__=='__main__':unittest.main()
