"""Audit completed contact outputs and write a new four-way comparison report."""
import csv,json
from decimal import Decimal
from contacts_received import validate, BATCH, verify_report, require, digest

def read_contacts(folder):
    sel=validate(folder)
    out=folder/'top1_contacts'
    if folder.parent.name!='05_baseline': verify_report(out/'validation.json')
    meta=json.loads((out/'ifp/metadata.json').read_text())
    if folder.parent.name=='05_baseline': verify_report(folder.parent/'preparation_validation.json')
    with (out/'contact_residues.csv').open() as f: rows=list(csv.DictReader(f))
    contacts={int(r['original_number']):{'residue':r['residue'],'types':sorted(r['interaction_types'].split(';'))} for r in rows}
    with (out/'ifp/ifp_presence.csv').open() as f: table=list(csv.reader(f))
    require(len(table)==5,'Expected one IFP data row')
    parsed={}
    for i,value in enumerate(table[4][1:],1):
        if value.lower()=='true': parsed.setdefault(table[1][i],set()).add(table[2][i])
    require(parsed=={r['residue']:set(r['interaction_types'].split(';')) for r in rows},'IFP/contact table disagreement')
    return {'score':sel['vina_score_kcal_mol'],'model':sel['selected_original_mode'],'count':len(contacts),'entry_count':sum(len(c['types']) for c in contacts.values()),'contacts':contacts,'source':str(out)}

def delta(wt,mut):
    a={(n,t) for n,c in wt['contacts'].items() for t in c['types']}
    b={(n,t) for n,c in mut['contacts'].items() for t in c['types']}
    def label(pair,src):
        n,t=pair; return f'{src["contacts"][n]["residue"]}:{t}'
    return {'gained':[label(x,mut) for x in sorted(b-a)],'lost':[label(x,wt) for x in sorted(a-b)],
            'gained_residues':[mut['contacts'][n]['residue'] for n in sorted(mut['contacts'].keys()-wt['contacts'].keys())],
            'lost_residues':[wt['contacts'][n]['residue'] for n in sorted(wt['contacts'].keys()-mut['contacts'].keys())],
            'identity_changes':[{'number':n,'wt':wt['contacts'][n]['residue'],'mutant':mut['contacts'][n]['residue']} for n in sorted(wt['contacts'].keys()&mut['contacts'].keys()) if wt['contacts'][n]['residue']!=mut['contacts'][n]['residue']]}

def main():
    out=BATCH/'run-01/contact-comparison'; require(not out.exists(),f'Refusing overwrite: {out}')
    m=json.loads((BATCH/'manifests/received-af3.json').read_text())
    scores=json.loads((BATCH/'run-01/score-audit/scores.json').read_text()); scoremap={r['variant']:r for r in scores['records']}
    baseline={lig:read_contacts(BATCH/'run-01/05_baseline'/lig) for lig in ['ascr3','ascr18']}
    records=[]; hashes={}
    for j in m['jobs']:
        for lig in ['ascr3','ascr18']:
            for name in ['selection.json','contact_residues.csv','ifp/ifp_presence.csv','ifp/metadata.json']:
                p=BATCH/'run-01'/j['alias']/lig/'top1_contacts'/name; hashes[str(p)]=digest(p)
        if j['id']=='baseline': continue
        r={'variant':j['id'],'alias':j['alias'],'scores':scoremap[j['id']]}
        for lig in ['ascr3','ascr18']:
            c=read_contacts(BATCH/'run-01'/j['alias']/lig)
            require(Decimal(str(c['score']))==Decimal(r['scores'][lig]['score']),'Score mismatch')
            r[lig]={'wt':baseline[lig],'mutant':c,'changes':delta(baseline[lig],c)}
        records.append(r)
    records.sort(key=lambda r:Decimal(r['scores']['D']),reverse=True)
    out.mkdir()
    (out/'four-way.json').write_text(json.dumps({'records':records,'baseline':baseline,'comparison_key':'original residue number and interaction type; residue identity changes separately recorded','files':hashes},indent=2)+'\n')
    lines=['# 批次05：最低分pose四格接触比较','',
      '58个受体×两种配体，共116个最低分pose。核验来源哈希、最低分MODEL、ProLIF 2.1.0参数与IFP/残基表一致性。',
      '','D＝ΔS18−ΔS3，单位kcal/mol。每个突变体与本轮WT比较；新增/丢失按原残基编号＋接触类型统计，突变导致的残基名称变化另记。',
      '','接触残基数按一个残基有任意类型接触计一次；残基–类型条目单独计数。6 Å为邻域筛选范围。接触数量变化不等同于能量贡献。',
      '','本轮为model_0、seed=1919的一次筛选；候选解释需结合pose可视化与追加seed复核。V368L/P/K局部结构可视化尚待用户确认。',
      '','| 突变 | ΔS3 | ΔS18 | D | #3残基数 WT→突变 | #18残基数 WT→突变 |','|---|---:|---:|---:|---|---|']
    for r in records:
        s=r['scores']; lines.append(f'| {r["variant"]} | {s["deltaS3"]} | {s["deltaS18"]} | {s["D"]} | 8→{r["ascr3"]["mutant"]["count"]} | 11→{r["ascr18"]["mutant"]["count"]} |')
    for r in records:
        lines+=['',f'## {r["variant"]}','', '| 体系 | 最低分 | MODEL | 接触残基数 | 残基–类型条目 |','|---|---:|---:|---:|---:|']
        for lig in ['ascr3','ascr18']:
            for role in ['wt','mutant']:
                c=r[lig][role]; lines.append(f'| {role} {lig} | {c["score"]} | {c["model"]} | {c["count"]} | {c["entry_count"]} |')
        for lig in ['ascr3','ascr18']:
            changes=r[lig]['changes']; lines+=['',f'{lig} 新增：'+('；'.join(changes['gained']) or '无')+'。',f'{lig} 丢失：'+('；'.join(changes['lost']) or '无')+'。']
            if changes['identity_changes']: lines.append('同编号接触残基名称变化：'+str(changes['identity_changes']))
    (out/'four-way.md').write_text('\n'.join(lines)+'\n')
    print('CONTACT AUDIT PASS: 116 lowest-pose analyses; 57 four-way comparisons')
    for r in records[:4]+list(reversed(records[-4:])):
        print(r['variant'],r['scores']['D'])
        for lig in ['ascr3','ascr18']: print(lig,json.dumps(r[lig]['changes']))
    print(out/'four-way.md')
if __name__=='__main__': main()
