import unittest
from unittest.mock import patch
import app
import test_app
class QuickTests(unittest.TestCase):
    def test_sixteen_images_are_preserved(self):
        d=test_app.AppTests().draft();images=['image'+str(i) for i in range(16)]
        p=app.build_payload(d,test_app.AppTests().template(),images)
        actual=[x['url'] for row in p['description']['sections'] for x in row['items'] if x['type']=='IMAGE']
        self.assertCountEqual(actual,images)
        with self.assertRaises(ValueError):app.build_payload(d,test_app.AppTests().template(),images+['extra'])
    def test_preset_does_not_copy_product_identity_or_private_location(self):
        d=test_app.AppTests().draft();d.update(product_id='OLD',producer_id='producer',safety='old warning',shipping_location={'city':'private'})
        with patch.object(app,'read',side_effect=lambda name,default=None:default),patch.object(app,'save') as save:
            app.Handler.action(object.__new__(app.Handler),'/presets-save',{'name':'Test','draft':d})
            fields=save.call_args.args[1]['Test']
            for key in ['product_id','local_id','images','sections','product_parameters','shipping_location','price','safety']:self.assertNotIn(key,fields)
            self.assertEqual(fields['producer_id'],'producer')
    def test_preflight_returns_missing_fields_without_upload(self):
        with patch.object(app,'read',side_effect=lambda name,default=None:default),patch.object(app,'api') as api:
            r=app.Handler.action(object.__new__(app.Handler),'/preflight',{})
            self.assertGreater(len(r['issues']),3);api.assert_not_called()
