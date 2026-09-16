import unittest
from unittest.mock import Mock
import workflow

class WorkflowTests(unittest.TestCase):
    def test_pagination(self):
        api=Mock(side_effect=[{'offers':[{'id':str(i)} for i in range(1000)]},{'offers':[{'id':'last'}]}])
        self.assertEqual(len(workflow.inventory(api)),1001)
        self.assertIn('offset=1000',api.call_args.args[0])
    def test_names_do_not_prove_identity_and_exact_external_does(self):
        offers=[{'id':'123456','name':'same name','external':{'id':'known'},'publication':{'status':'ACTIVE'}}]
        data={workflow.key('root/one'):{'draft':{'local_id':'known'}},workflow.key('root/two'):{'draft':{'name':'same name','local_id':'other'}}}
        result=workflow.scan(['root/one','root/two'],lambda _: {'offers':offers},lambda k,d=None:data.get(k,d),'production')
        self.assertEqual([r['status'] for r in result['rows']],['ACTIVE','unlinked'])
    def test_unknown_and_duplicate_states_are_not_new(self):
        data={workflow.key('x'):{'offers':{'production':{'id':'absent'}}},workflow.key('y'):{'draft':{'local_id':'same'}}}
        offers=[{'id':str(i),'external':{'id':'same'}} for i in range(2)]
        result=workflow.scan(['x','y'],lambda _: {'offers':offers},lambda k,d=None:data.get(k,d),'production')
        self.assertEqual([r['status'] for r in result['rows']],['unknown','ambiguous'])
    def test_current_draft_and_environment_isolation(self):
        data={'draft':{'folder':'x','local_id':'current'},'offer-production':{'id':'123456'},'queue-links-sandbox':{'x':'other'}}
        result=workflow.scan(['x'],lambda _: {'offers':[{'id':'123456','publication':{'status':'INACTIVE'}}]},lambda k,d=None:data.get(k,d),'production')
        self.assertEqual(result['rows'][0]['status'],'INACTIVE')
    def test_failed_scan_never_means_missing(self):
        with self.assertRaises(ValueError):workflow.scan(['x'],Mock(side_effect=ValueError('offline')),lambda k,d=None:d,'production')

class ImportRefreshTests(unittest.TestCase):
    def test_new_note_fills_old_empty_draft_without_changing_identity(self):
        old={'local_id':'stable','ai_facts':'','sections':[],'price':'18','images':['old']}
        fresh={'local_id':'new','ai_facts':'Nowe fakty z opis.txt','sections':[],'price':'','images':['new']}
        merged=workflow.merge_import(old,fresh)
        self.assertEqual(merged['ai_facts'],fresh['ai_facts'])
        self.assertEqual(merged['local_id'],'stable');self.assertEqual(merged['price'],'18')
        self.assertEqual(merged['images'],['old']);self.assertEqual(old['ai_facts'],'')
    def test_existing_edits_are_preserved_and_ready_description_fills_empty(self):
        old={'ai_facts':'Moja poprawka','sections':[]}
        fresh={'ai_facts':'Starszy plik','sections':[{'text':'Gotowy opis'}]}
        merged=workflow.merge_import(old,fresh)
        self.assertEqual(merged['ai_facts'],'Moja poprawka');self.assertEqual(merged['sections'],fresh['sections'])
    def test_new_choice_persists_independently_of_folder_title(self):
        data={'queue-choices-production':{'dowolny folder':True}}
        r=workflow.scan(['dowolny folder'],lambda _: {'offers':[]},lambda k,d=None:data.get(k,d),'production')
        self.assertTrue(r['rows'][0]['isNew'])
        data['queue-links-production']={'dowolny folder':'123456'}
        r=workflow.scan(['dowolny folder'],lambda _: {'offers':[{'id':'123456','name':'Całkiem inny tytuł','publication':{'status':'ACTIVE'}}]},lambda k,d=None:data.get(k,d),'production')
        self.assertFalse(r['rows'][0]['isNew']);self.assertEqual(r['rows'][0]['status'],'ACTIVE')

if __name__=='__main__':unittest.main()
