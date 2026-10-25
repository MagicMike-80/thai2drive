import os, sys, asyncio, json, uuid, copy
from pathlib import Path
from types import SimpleNamespace
os.environ.update(MONGO_URL='mongodb://127.0.0.1:1', DB_NAME='free30_offline', JWT_SECRET='free30-local-only-not-a-real-credential')
repo=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(repo/'backend'))
import server
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

async def main():
    direct=AsyncIOMotorClient('mongodb://127.0.0.1:27095/?directConnection=true',serverSelectionTimeoutMS=10000)
    try:
        await direct.admin.command('replSetInitiate',{'_id':'free30rs','members':[{'_id':0,'host':'127.0.0.1:27095'}]})
    except OperationFailure as e:
        if e.code != 23: raise
    client=AsyncIOMotorClient('mongodb://127.0.0.1:27095/?replicaSet=free30rs',serverSelectionTimeoutMS=30000)
    db=client['free30_synthetic_'+uuid.uuid4().hex[:10]]
    server.db=db
    await db.users.insert_many([{'id':f'u{i}', 'is_premium':False,'trial_used':False} for i in range(65)])
    # Historical failed reservations must not make real seats disappear.
    await db.campaign_counters.insert_one({'_id':'free30-2026-10','sequence':500})
    async def claim(i,language='no'):
        r=await server.register_campaign_user(SimpleNamespace(language=language),{'sub':f'u{i}'})
        return r.status_code,json.loads(r.body)
    results=await asyncio.gather(*(claim(i%60,('no','th','en')[i%3]) for i in range(80)))
    granted=await db.campaign_users.count_documents({'campaign_id':'free30-2026-10'})
    assert granted==50,granted
    assert await db.users.count_documents({'trial_used':True})==50
    assert sum(status==200 for status,_ in results)==50
    docs=await db.campaign_users.find({}).to_list(100)
    assert len({d['user_id'] for d in docs})==50
    assert sorted(d['campaign_index'] for d in docs)==list(range(1,51))
    status=json.loads((await server.get_campaign_status()).body)
    assert status['registered']==50 and status['remaining']==0 and not status['is_active']
    old=await db.users.find_one({'id':docs[0]['user_id']})
    repeat=await claim(int(old['id'][1:]))
    assert repeat[0]==400 and await db.users.find_one({'id':old['id']})==old
    # New isolated database for preservation and forced rollback.
    db2=client[db.name+'_rollback'];server.db=db2
    await db2.users.insert_many([
        {'id':'u0','is_premium':True,'premium_expires_at':'2099-01-01T00:00:00+00:00'},
        {'id':'u1','trial_used':True,'trial_expires_at':'2099-01-01T00:00:00+00:00'},
        {'id':'u2','is_premium':False,'trial_used':False,'premium_expires_at':'2020-01-01T00:00:00+00:00'},
        {'id':'u3','is_premium':False,'trial_used':False}])
    before=await db2.users.find({}).to_list(10)
    for i in range(2): assert (await claim(i))[0]==400
    assert (await claim(2))[0]==409
    assert await db2.campaign_users.count_documents({})==0
    assert await db2.users.find({}).to_list(10)==before
    assert (await claim(3,'th'))[0]==200
    assert json.loads((await server.get_campaign_status()).body)['registered']==1
    report={'real_local_mongo':True,'database':db.name,'requests':80,'successful_claims':50,'unique_claims':50,'capacity_50_51':True,'duplicate_no_extension':True,'existing_paid_and_trial_unchanged':True,'conditional_failure_transaction_rollback':True,'legacy_sequence_500_does_not_consume_seats':True,'languages':['no','th','en']}
    out=repo/'test_reports/free30-20261025';out.mkdir(parents=True,exist_ok=True)
    (out/'mongo-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))
    client.close();direct.close()

asyncio.run(main())
