"""AGENTEE-487 R before/after probe (run inside a tree via ae-ci-exec): H1 no-phase isolated always zone; H2 duplicate evidence."""
import inspect, sys, unittest
sys.path[:0] = ['.', 'src', 'tests']
from agent_ee import add_planes as planes
from tests.test_add_planes import PlaneFixture
class P(PlaneFixture, unittest.TestCase):
    def test_h1_no_phase(self):
        self.plan['zones'] = [dict(self.plan['zones'][0], island_removal='always',
                                   outline={'polygon_mm': [[35,11],[49,11],[49,30],[35,30]]})]
        self.save()
        r = planes.generate(self.source, self.board, self.plan_path, self.root/'h1')
        print('H1_NO_PHASE_ALWAYS_ISOLATED', r['execution'], 'deferred', r.get('deferred_connectivity'))
    def test_h2_duplicate(self):
        uid = '10000000-0000-0000-0000-000000000001'
        errs = [dict(type='isolated_copper', severity='warning', items=[dict(uuid=uid, pos=dict(x=1, y=1))])] * 2
        zones = [dict(uuid=uid, fill_polygons=2)]
        params = inspect.signature(planes.wholly_unconnected).parameters
        try:
            if 'phase' in params:
                out = planes.wholly_unconnected(errs, zones, {uid}, {uid: dict(polygons=2, islands=[True, True])}, planes.PRE_ROUTING)
            else:
                out = planes.wholly_unconnected(errs, zones, {uid})
            print('H2_DUPLICATE_FINDINGS', 'deferred' if out else 'not-deferred', sorted(out))
        except ValueError as exc:
            print('H2_DUPLICATE_FINDINGS', 'FAIL-CLOSED', exc)
unittest.main(argv=['x'], verbosity=0)
