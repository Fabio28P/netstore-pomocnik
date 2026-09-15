import os,tempfile
os.environ['NETSTORE_DATA']=tempfile.mkdtemp(prefix='netstore-v13-')
import unittest,json,io
from unittest.mock import patch
import app,ai_writer

class V13Tests(unittest.TestCase):
 def test_all_four_images_used_once(self):
  sections=[{'title':'Test','text':'Treść','image_index':idx} for idx in [2,-1,0,2,99]]
  result=app.description(sections,['a','b','c','d'])
  images=[item['url'] for row in result['sections'] for item in row['items'] if item['type']=='IMAGE']
  self.assertEqual(sorted(images),['a','b','c','d']);self.assertEqual(images[0],'c')
 def test_plan_invalid_and_duplicate_indices_repaired(self):
  result={'sections':[{'image_index':2},{'image_index':2},{'image_index':500},{'image_index':-1},{'image_index':0}]}
  r=ai_writer.assign_images(result,4)
  actual=[s['image_index'] for s in r['sections'] if s['image_index']>=0]
  self.assertEqual(sorted(actual),[0,1,2,3])
 def test_markdown_headings_cleaned(self):
  r=ai_writer.validate_result({'name':'Rolka zamienna do pilota','sections':[{'title':'### **Zalety**','text':'### Montaż\nTreść','image_index':0}],'questions':[]})
  self.assertEqual(r['sections'][0]['title'],'Zalety');self.assertNotIn('###',r['sections'][0]['text'])
 def test_gemini_receives_opted_images_and_style(self):
  output={'name':'Rolka zamienna do pilota','sections':[{'title':'Kupujesz','text':'Jedna rolka','image_index':0}],'questions':[]}
  with patch.object(ai_writer,'build_opener') as op:
   op.return_value.open.return_value=io.BytesIO(json.dumps({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(output)}]}}]}).encode())
   ai_writer.generate({'provider':'gemini','api_key':'secret'},'Jedna czarna rolka do pilota.', ['data:image/jpeg;base64,YWJj'])
   payload=json.loads(op.return_value.open.call_args.args[0].data)
   self.assertEqual(payload['contents'][0]['parts'][1]['inlineData']['data'],'YWJj')
   self.assertIn('280–420',payload['systemInstruction']['parts'][0]['text'])
   self.assertIn('przykład B',payload['systemInstruction']['parts'][0]['text'])
 def test_no_arbitrary_remote_image_urls(self):
  with self.assertRaises(ValueError):ai_writer.check_images(['https://example.com/image.png'])
if __name__=='__main__':unittest.main()
