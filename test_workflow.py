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

if __name__=='__main__':unittest.main()
