import os, tempfile, unittest, json
from unittest.mock import patch
os.environ['NETSTORE_DATA'] = tempfile.mkdtemp(prefix='netstore-unit-')
import app

class AppTests(unittest.TestCase):
    def draft(self):
        return {'name':'Rolka scroll do pilota LG MR23GN', 'price':'18', 'stock':1000, 'category':'123', 'local_id':'local',
                'shipping_location':{'countryCode':'PL','province':'MAZOWIECKIE','postCode':'00-001','city':'Miasto testowe'}, 'sections':[{'title':'Opis <test>', 'text':'Jedna rolka <script>alert(1)</script>'}], 'product_parameters':[], 'offer_parameters':[]}
    def template(self):
        return {'delivery':{'shippingRates':{'id':'rate'},'handlingTime':'P7D'}, 'afterSalesServices':{'returnPolicy':{'id':'return'}},
                'productSet':[{'product':{'id':'WRONG-OLD-ROLLER'}}], 'images':['OLD']}
    def test_only_seller_settings_and_explicit_draft(self):
        p=app.build_payload(self.draft(),self.template(),['https://a.allegroimg.com/new'])
        self.assertEqual(p['publication']['status'],'INACTIVE'); self.assertEqual(p['delivery']['handlingTime'],'P1D')
        self.assertEqual(p['stock']['available'],1000); self.assertEqual(p['sellingMode']['price']['amount'],'18.00')
        self.assertNotIn('WRONG-OLD-ROLLER',json.dumps(p)); self.assertNotIn('OLD',json.dumps(p))
        self.assertEqual(p['afterSalesServices']['returnPolicy']['id'],'return')
    def test_location_overrides_template_and_allows_offer_exception(self):
        d=self.draft(); template=self.template()
        template['location']={'city':'Warszawa','province':'MAZOWIECKIE','postCode':'00-001','countryCode':'PL'}
        self.assertEqual(app.build_payload(d,template,['photo'])['location'],d['shipping_location'])
        d['shipping_location']={'city':'Katowice','province':'SLASKIE','postCode':'40-001','countryCode':'PL'}
        self.assertEqual(app.build_payload(d,template,['photo'])['location'],d['shipping_location'])
        d['shipping_location']['postCode']=''
        with self.assertRaises(ValueError): app.build_payload(d,template,['photo'])
    def test_local_shipping_default_and_missing_location(self):
        d=self.draft(); location=d.pop('shipping_location')
        with patch.object(app,'read',return_value={}), self.assertRaises(ValueError):
            app.build_payload(d,self.template(),['photo'])
        with patch.object(app,'save') as save:
            result=object.__new__(app.Handler).action('/shipping-default',{'shipping_location':location})
            save.assert_called_once_with('shipping-default',location)
            self.assertEqual(result['location'],location)
        with patch.object(app,'read',return_value=location):
            self.assertEqual(app.build_payload(d,self.template(),['photo'])['location'],location)
    def test_linked_folder_cannot_create_duplicate(self):
        d=self.draft();d['folder']='products/test'
        def read(name,default=None):
            return {'products/test':'123456'} if name.startswith('queue-links-') else default
        with patch.object(app,'read',side_effect=read), patch.object(app,'api') as api:
            with self.assertRaisesRegex(ValueError,'powiązany'):
                object.__new__(app.Handler).action('/draft',d)
            api.assert_not_called()
    def test_category_search_encodes_name(self):
        with patch.object(app,'api',return_value={'matchingCategories':[]}) as api:
            object.__new__(app.Handler).action('/categories-search',{'name':'rolka & pilot'})
            self.assertEqual(api.call_args.args[0],'/sale/matching-categories?name=rolka+%26+pilot')
    def test_escape_description(self):
        p=app.build_payload(self.draft(),self.template(),['photo'])
        text=p['description']['sections'][0]['items'][1]['content']
        self.assertNotIn('<script>',text); self.assertIn('&lt;script&gt;',text)
    def test_validation(self):
        for price in ['NaN','Infinity','-2','0','1.234']:
            d=self.draft();d['price']=price
            with self.assertRaises(ValueError):app.validate(d)
        with self.assertRaises(ValueError):app.build_payload(self.draft(),{},['photo'])
    def test_reference(self):
        self.assertEqual(app.offer_id('https://allegro.pl/oferta/rolka-18866219051'),'18866219051')
        with self.assertRaises(ValueError):app.offer_id('../config')
    def test_publish_requires_confirmation(self):
        handler=object.__new__(app.Handler)
        with self.assertRaises(ValueError):handler.action('/publish',{})
    def test_ambiguous_creation_is_not_retried(self):
        app.save('offer-production',{'pending':True,'local_id':'local'})
        handler=object.__new__(app.Handler)
        with patch.object(app,'api') as api:
            with self.assertRaisesRegex(ValueError,'nieznany wynik'):handler.action('/draft',self.draft())
            api.assert_not_called()
        app.save('offer-production',{})
    def test_refresh_and_image_host(self):
        app.save('tokens-production',{'access_token':'test','expires_at':99999999999})
        with patch.object(app,'request',return_value={'location':'photo'}) as req:
            app.api('/sale/images','POST',b'bytes','image/png')
            self.assertEqual(req.call_args.args[0],'https://upload.allegro.pl/sale/images')
    def test_secret_never_returned(self):
        handler=object.__new__(app.Handler)
        handler.action('/configure',{'client_id':'id','client_secret':'SECRET','environment':'sandbox'})
        self.assertEqual(app.read('config')['client_secret'],'SECRET')
        handler.action('/configure',{'client_id':'id','client_secret':'','environment':'production'})
        self.assertEqual(app.read('config')['client_secret'],'SECRET')
if __name__=='__main__':unittest.main()
