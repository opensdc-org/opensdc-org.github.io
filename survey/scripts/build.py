# -*- coding: utf-8 -*-
"""Build the static survey page. Python 3.9+; standard library only."""
import json,html,pathlib,collections,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
esc=lambda x:html.escape(str(x),quote=True)
ASOF='2026-11-16'  # 文献核验截止日期；修改时同步更新 content/scope.html 与 README.md
papers=json.loads((ROOT/'data/papers.json').read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'data/software.json').read_text(encoding='utf-8')); software=catalog['items']; swgroups=catalog['groups']
datasets=json.loads((ROOT/'data/datasets.json').read_text(encoding='utf-8'))
sw={s['id']:s for s in software}; ds={d['id']:d for d in datasets}
if len(sw)!=len(software) or len(ds)!=len(datasets): raise ValueError('Duplicate software or dataset id')
BENCH='https://opensdc-org.github.io/benchmark/'; BENCHREPO='https://github.com/opensdc-org/OpenSDC-Bench'
required=['id','title','venue','year','url','problem','method','results','scenario','evidence','status','tags']
for p in papers:
 for key in required:
  if key not in p: raise ValueError(f"Missing {key}: {p.get('id')}")
 if p['status'] not in ['main','appendix']: raise ValueError(f"Invalid status: {p['id']}")
 if not isinstance(p['year'],int): raise ValueError(f"Invalid year: {p['id']}")
 if not p['url'].startswith(('https://','http://')): raise ValueError(f"Invalid URL: {p['id']}")
 for key,table in (('code',sw),('data',ds)):
  for x in p.get(key,[]):
   if x not in table: raise ValueError(f"Unknown {key} id {x}: {p['id']}")
venues=['SC','PPoPP','ICS','HPDC','SOSP','OSDI','EuroSys','FAST','USENIX ATC','NSDI','ISCA','HPCA','MICRO','ASPLOS','SIGCOMM','DAC']
CORE=venues[:14]  # 主要检索范围；其余场所的主清单条目必须写 select_reason
aliases={'AI/HPC融合':'AI融合','AI/HPC':'AI融合','GPU加速':'GPU','无损压缩':'无损','有损压缩':'有损','内存缓存':'内存压缩','内存':'内存压缩','I/O':'I/O与检查点','检查点':'I/O与检查点','质量性能权衡':'性能权衡','质量权衡':'性能权衡','精度与性能权衡':'性能权衡','学习式压缩':'学习压缩','科学数据压缩':'科学数据','渐进访问':'渐进检索','原位处理':'原位','可移植':'可移植性','软硬协同':'硬件协同'}
def evlevel(e):
 if '正文' in e or '全文' in e:return '正文'
 if '摘要' in e or '报告' in e or 'artifact' in e:return '摘要'
 return '题录'
for p in papers:
 if p['venue']=='ATC':p['venue']='USENIX ATC'
 if p['venue'] not in venues:venues.append(p['venue'])
 p['status']=p.get('status','main');p.setdefault('caveat','');p.setdefault('tags',[])
 if p['status']=='main' and p['venue'] not in CORE and not p.get('select_reason'): raise ValueError(f"Missing select_reason for supplementary venue: {p['id']}")
 p['selection']='专题补充' if p.get('select_reason') else '主要检索范围'
 p['evlevel']=evlevel(p['evidence'])
 p.setdefault('code',[]);p.setdefault('data',[])
 p['reprotext']=' '.join([sw[c]['name'] for c in p['code']]+[ds[d]['name'] for d in p['data']])
 p['repro']=[k for k,v in (('code',p['code']),('data',p['data']),('bench',any(sw[c].get('bench') for c in p['code']))) if v]
 p['tags']=list(dict.fromkeys(aliases.get(t,t) for t in p['tags']))
ids=[p['id'] for p in papers]; assert len(ids)==len(set(ids)),'duplicate IDs'
papers.sort(key=lambda p:(venues.index(p['venue']),-p['year'],p['title']))
main=[p for p in papers if p['status']=='main']; app=[p for p in papers if p['status']!='main']; byid={p['id']:p for p in papers}
counts=collections.Counter(p['venue'] for p in main)
def refs(ids):
 return '；'.join(f'<a class="paper-ref" href="#{esc(i)}">{esc(byid[i]["title"].split(":")[0])} · {esc(byid[i]["venue"])} {byid[i]["year"]}</a>' for i in ids if i in byid)
def trend(title,body,ids,question):
 return f'<article class="trend"><h3>{title}</h3><p>{body}</p><p class="refs">证据：{refs(ids)}</p><p class="question"><b>值得继续研究：</b>{question}</p></article>'
trends=''.join(trend(t['title'],t['body'],t['papers'],t['question']) for t in json.loads((ROOT/'content/trends.json').read_text(encoding='utf-8')))

def repro(p):
 code=''.join(f'<a class="chip" href="./compressors.html#sw-{esc(c)}">{esc(sw[c]["name"])}</a>' for c in p['code'])
 if not code: code=f'<span class="muted">{esc(p.get("code_note") or "未检索到公开代码")}</span>'
 elif p.get('code_note'): code+=f'<span class="muted">{esc(p["code_note"])}</span>'
 data=''.join(f'<a class="chip" href="./datasets.html#ds-{esc(d)}">{esc(ds[d]["name"])}</a>' for d in p['data'])
 basis='据论文'+p.get('data_basis','正文')+'中出现的数据集名称标注'
 data=f'<span class="field-label" title="{esc(basis)}">数据集</span>{data}' if data else ''
 bench=f'<a class="chip bench" href="{BENCH}" target="_blank" rel="noopener noreferrer">OpenSDC-Bench 有评测结果 ↗</a>' if 'bench' in p['repro'] else ''
 return f'<p class="repro"><span class="field-label">代码</span>{code}{data}{bench}</p>'
def card(p):
 src=[{'url':p['url'],'label':'官方 / 稳定入口'}]+p.get('sources',[]); seen=set(); links=[]
 for s in src:
  if s['url'] in seen:continue
  seen.add(s['url']);links.append(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s.get("label","来源"))} ↗</a>')
 reason=f'<p class="callout note"><b>收录理由：</b>{esc(p["select_reason"])}</p>' if p.get('select_reason') else ''
 tags=''.join(f'<span class="tag">{esc(t)}</span>' for t in p['tags'])
 return f'''<article class="paper" id="{esc(p['id'])}" data-venue="{esc(p['venue'])}" data-year="{p['year']}" data-status="{p['status']}">
<div class="meta"><span class="badge year">{p['year']}</span><span class="badge">{esc(p['venue'])}</span><span class="badge">核验：{esc(p['evidence'])}</span>{tags}</div>
{reason}<h3><a href="{esc(p['url'])}" target="_blank" rel="noopener noreferrer">{esc(p['title'])} ↗</a></h3>
<p><span class="field-label">主要问题</span>{esc(p['problem'])}</p>
<p class="results"><span class="field-label">关键结果 · 论文报告</span>{esc(p['results'])}</p>
<details><summary>展开核心方法与适用场景</summary><div class="details-grid"><p><span class="field-label">核心方法 / 系统设计</span>{esc(p['method'])}</p><p><span class="field-label">适用数据 / 场景</span>{esc(p['scenario'])}</p></div></details><p class="caveat">{esc(p['caveat'])}</p>{repro(p)}<div class="sources">{''.join(links)}</div></article>'''
nav=''.join(f'<a href="#venue-{esc(v.replace(" ","-"))}">{esc(v)} <small>{counts[v]}</small></a>' for v in venues if counts[v])
groups=''.join(f'<section class="venue-group" id="venue-{esc(v.replace(" ","-"))}"><div class="venue-head"><h2>{esc(v)}</h2><span>{counts[v]} 篇主清单论文</span></div>'+''.join(card(p) for p in main if p['venue']==v)+'</section>' for v in venues if counts[v])
rows=''.join('<tr><td><a href="#venue-'+esc(v.replace(' ','-'))+'">'+esc(v)+'</a></td>'+''.join('<td>'+str(sum(p['venue']==v and p['year']==y for p in main))+'</td>' for y in range(2019,2027))+f'<td><b>{counts[v]}</b></td></tr>' for v in venues if counts[v])
coverage=f'<div class="tablewrap"><table><thead><tr><th>发表场所</th>'+''.join(f'<th>{y}</th>' for y in range(2019,2027))+'<th>合计</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
scope=(ROOT/'content/scope.html').read_text(encoding='utf-8')
if ASOF not in scope: raise ValueError(f'content/scope.html does not mention the verification date {ASOF}')
tagcount=collections.Counter(t for p in papers for t in p['tags'])
tagopts=''.join(f'<option value="{esc(t)}">{esc(t)}（{n}）</option>' for t,n in sorted(tagcount.items(),key=lambda x:(-x[1],x[0])) if n>=2)
paper_json=json.dumps(papers,ensure_ascii=False).replace('</', r'<\/')

opts=lambda a:''.join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in a)
page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="2019–2026 HPC、系统与体系结构顶会数据压缩论文，按会议组织、逐条来源核验与趋势分析。"><title>数据压缩研究图谱 · 2019–2026</title><link rel="stylesheet" href="./assets/styles.css"></head><body id="top"><div class="layout"><aside aria-label="目录"><div class="brand">COMPRESSION<br>RESEARCH ATLAS</div><a href="#scope">范围与收录标准</a><a href="#coverage">覆盖情况</a><a href="#catalog">论文筛选</a><a href="#trends">发展趋势 · 10条</a><a href="#appendix">待核验 / 边缘相关</a><h3>复现资源</h3><a href="./compressors.html">压缩器与代码目录 <small>{len(software)}</small></a><a href="./datasets.html">数据集目录 <small>{len(datasets)}</small></a><h3>按发表场所跳转</h3>{nav}<p class="note">检索截至<br>{ASOF}<br><br>OpenSDC 文献整理<br>来源与核验范围见各条目</p></aside><main><header><nav class="site-links" aria-label="OpenSDC 导航"><a href="https://opensdc-org.github.io/zh.html">← 返回 OpenSDC</a><a href="./compressors.html">压缩器与代码目录</a><a href="./datasets.html">数据集目录</a><a href="https://opensdc-org.github.io/benchmark/">评测与榜单 →</a></nav><div class="eyebrow">LITERATURE REVIEW · 2019—2026</div><h1>数据压缩研究图谱</h1><p class="subtitle">HPC / 系统 / 体系结构顶会与精选重要工作<br>从科学数据减量到内存、通信与加速器协同设计</p><div class="stats"><div class="stat"><strong>{len(main)}</strong><span>主清单论文</span></div><div class="stat"><strong>{len(counts)}</strong><span>会议 / 期刊系列</span></div><div class="stat"><strong>{len(app)}</strong><span>附录条目</span></div><div class="stat"><strong>{sum(1 for p in papers if p['code'])}</strong><span>篇有公开代码</span></div><div class="stat"><strong>2019–26</strong><span>检索年份</span></div></div><p class="mobile-nav"><a href="#catalog">论文目录</a> · <a href="#trends">趋势总结</a> · <a href="#appendix">附录</a> · <a href="./compressors.html">代码目录</a> · <a href="./datasets.html">数据集目录</a></p></header>
<section class="scope" id="scope"><h2>检索范围与收录标准</h2>{scope}</section>
<section id="coverage"><div class="eyebrow">COVERAGE</div><h2>按发表场所与年份查看覆盖情况</h2><p class="note">单元格为当前主清单篇数，包含已标注状态的2026录用记录；附录不计入。数字描述检索结果，不用于判断学科发表量变化。</p>{coverage}</section>
<section id="catalog"><div class="eyebrow">PAPER CATALOG</div><h2>按发表场所组织的论文清单</h2><p>每条包含问题、方法、关键结果、场景、核验来源，以及已核实的代码仓库和公开数据集。默认展开问题与结果；可按需展开方法，或一次展开全部。主题下拉列表只列出现两次及以上的标签，其余标签可用检索框查找。</p><div class="filters"><div class="controls"><label>检索题目、方法、结果或主题<input id="search" type="search" placeholder="例如：GPU、误差、通信、KV、SZ、checkpoint"></label><label>发表场所<select id="venue"><option value="">全部发表场所</option>{opts([v for v in venues if counts[v]])}</select></label><label>年份<select id="year"><option value="">全部年份</option>{opts(range(2026,2018,-1))}</select></label><label>主题标签<select id="tag"><option value="">全部主题</option>{tagopts}</select></label><label>核验深度<select id="evidence"><option value="">全部核验深度</option><option value="正文">核对过正文 / 全文</option><option value="摘要">摘要或官方报告</option><option value="题录">仅题录 / 议程</option></select></label><label>清单范围<select id="listmode"><option value="all">主清单与附录</option><option value="main">只看主清单</option><option value="appendix">只看附录</option></select></label><label>收录范围<select id="selection"><option value="">全部收录范围</option><option value="主要检索范围">主要检索范围</option><option value="专题补充">专题补充</option></select></label><label>复现资源<select id="repro"><option value="">不限</option><option value="code">有公开代码</option><option value="data">标注了公开数据集</option><option value="bench">OpenSDC-Bench 有评测结果</option></select></label></div><div class="toolbar"><button id="reset">重置筛选</button><button id="expand">展开当前条目</button><button id="collapse">收起方法详情</button><button id="print">打印 / 另存PDF</button><span class="resultcount" id="resultcount" aria-live="polite"></span></div></div><noscript>浏览器未启用JavaScript：完整论文内容仍可阅读，筛选功能不可用。</noscript><p class="empty" id="empty" hidden>没有匹配条目，请调整筛选或点击重置。</p></section>
<div id="papers">{groups}</div>
<section id="trends"><div class="eyebrow">SYNTHESIS</div><h2>近几年数据压缩的发展趋势</h2><p class="callout">以下按研究主题梳理相关进展，各节附对应论文。仅有摘要或录用记录的工作，其实验与部署情况以条目中的核验说明为准。</p>{trends}<h3>科学压缩的几条算法主线</h3><p>预测型路线从局部回归/插值发展到SZ3模块化组合、QoZ/HPEZ质量驱动自调优；变换型路线包括SPERR的小波与嵌入编码、MGARD的多层误差控制；张量路线由TTHRESH代表，利用全局低秩相关性并在中低码率改善率失真。无损路线如ndzip/LC则保留每个浮点位，适合不能容忍数值改动的任务。它们解决不同约束，不宜用单一“最佳压缩器”概括。</p><p class="refs">证据：{refs(['tbd23-sz3','sc22-qoz','sigmod24-hpez','ipdps23-sperr','tc22-mgardplus','tvcg20-tthresh','dcc21-ndzip','sc21-ndzip','asplos25-float'])}</p><h3>阅读实验结果时应保持的口径</h3><ul><li><b>压缩比：</b>通常是原始字节/压缩后字节；“提高N%”与“为原来的N倍”不同。模型权重、元数据与训练成本是否计入须看原文。</li><li><b>吞吐与加速：</b>GB/s可能按原始输入计算；压缩器、通信原语、I/O或端到端应用的收益不能互相代替。最大值不是平均值。</li><li><b>质量：</b>绝对/相对误差界、PSNR、任务准确率和数值稳定性分别回答不同问题；“无精度损失”不能自动视作逐位无损。</li><li><b>可比性：</b>硬件型号、节点数、数据形状、误差设置、数据可压缩性和基线实现共同决定结果。比较时需同时考虑这些条件。</li></ul></section>
<section id="appendix" class="appendix"><div class="eyebrow">APPENDIX</div><h2>待核验 / 边缘相关</h2><p>下列条目不计入主清单论文数。这里既包括压缩核心性或证据尚待确认的候选，也保留少量已确认的范围排除案例；具体原因逐条列出。附录不按发表场所等级划分；各条目列明核验状态或主题边界。</p>{''.join(card(p) for p in app)}</section>
<section id="search-notes"><h2>检索方法与覆盖边界</h2><p>检索组合包括会议名称/年份与 compression、data reduction、scientific、lossy、error-bounded、decompression、compressed memory/cache、gradient/KV、deduplication、progressive、GPU 等词。使用会议目录与官方程序发现候选，结合作者发表列表追踪同一工作不同标题/预印本，最终以ACM/IEEE/USENIX、会议官方页、作者公开原稿或机构仓储核对。</p><p>排除相同工作的重复预印本与代码版本；没有看到实验数字时保留“未报告/未核实”，不从基线论文、相关新闻或名称推断结果。2019作为回溯起点，主要密集覆盖2020–2026。扩展会议为主题补充；SIGMOD/VLDB/ICDE等数据库顶会、纯图像/视频编码顶会以及扩展期刊未作为完整检索池，不能以本页判断这些领域的全貌。</p><p class="note">条目所依据的摘要、正文与官方记录已分别标注。尚缺精确误差设置、硬件配置或表格基线的条目已在证据与备注中保留边界。外部链接可能随时间迁移，DOI与USENIX入口优先保留。</p></section>
<footer>整理语言：中文 · 文献题名保留英文 · 截至{ASOF} · 文献题录与研究趋势<br>OpenSDC · 专题文献整理 · 实验结果按论文报告记录，未进行独立复现。</footer></main></div><a href="#top" class="toplink">回到顶部 ↑</a><script type="application/json" id="paper-data">{paper_json}</script><script src="./assets/app.js" defer></script></body></html>'''
out=ROOT/'index.html'
out.write_text(page,encoding='utf-8')

# ---------------------------------------------------------------- catalogue pages: compressors.html, datasets.html
EXT=' target="_blank" rel="noopener noreferrer"'
STD=('Apache','MIT','BSD','GPL','LGPL','MPL')
def plinks(ids):
 ps=sorted((byid[i] for i in ids),key=lambda p:(-p['year'],p['venue'],p['title']))
 return ''.join(f'<a href="./index.html#{esc(p["id"])}">{esc(p["title"])} · {esc(p["venue"])} {p["year"]}</a>' for p in ps)
def shell(title,desc,sidebar,body):
 head=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(desc)}"><title>{esc(title)} · 数据压缩研究图谱</title><link rel="stylesheet" href="./assets/styles.css"></head><body id="top"><div class="layout">'
 side=f'<aside aria-label="目录"><div class="brand">COMPRESSION<br>RESEARCH ATLAS</div><a href="./index.html">论文图谱 <small>{len(papers)}</small></a><a href="./compressors.html">压缩器与代码目录 <small>{len(software)}</small></a><a href="./datasets.html">数据集目录 <small>{len(datasets)}</small></a>{sidebar}<p class="note">核查截至<br>{ASOF}<br><br>OpenSDC 文献整理</p></aside>'
 nav=f'<nav class="site-links" aria-label="OpenSDC 导航"><a href="https://opensdc-org.github.io/zh.html">← 返回 OpenSDC</a><a href="./index.html">论文图谱</a><a href="./compressors.html">压缩器与代码目录</a><a href="./datasets.html">数据集目录</a><a href="{BENCH}">评测与榜单 →</a></nav>'
 foot=f'<footer>OpenSDC · 专题文献整理 · 仓库与数据集信息核查于 {ASOF}，以各仓库和数据提供方当前的说明为准。</footer></main></div><a href="#top" class="toplink">回到顶部 ↑</a><script src="./assets/catalog.js" defer></script></body></html>'
 return head+side+'<main><header>'+nav+body+foot
def controls(extra,hint):
 return f'<div class="filters"><div class="controls"><label>检索名称、说明或论文<input id="q" type="search" placeholder="{esc(hint)}"></label>{extra}</div><div class="toolbar"><button id="reset">重置筛选</button><span class="resultcount" id="count" aria-live="polite"></span></div></div><p class="empty" id="empty" hidden>没有匹配条目，请调整筛选或点击重置。</p>'
def kv(rows): return '<dl class="kv">'+''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k,v in rows if v)+'</dl>'
def stats(rows): return '<div class="stats">'+''.join(f'<div class="stat"><strong>{n}</strong><span>{esc(t)}</span></div>' for n,t in rows)+'</div>'
def grouped(names,items,render,unit):
 body=''.join(f'<section class="group" id="g-{i}"><div class="group-head"><h2>{esc(g)}</h2><span>{sum(1 for x in items if x["group"]==g)} {unit}</span></div>'+''.join(render(x) for x in items if x['group']==g)+'</section>' for i,g in enumerate(names))
 side='<h3>按类别跳转</h3>'+''.join(f'<a href="#g-{i}">{esc(g)} <small>{sum(1 for x in items if x["group"]==g)}</small></a>' for i,g in enumerate(names))
 return body,side
papers_of_sw=collections.defaultdict(list); papers_of_ds=collections.defaultdict(list)
for p in papers:
 for c in p['code']: papers_of_sw[c].append(p['id'])
 for d in p['data']: papers_of_ds[d].append(p['id'])

def sw_item(s):
 repo=s['repo']; short=repo.replace('https://github.com/','').replace('https://','')
 badges=''.join(f'<span class="badge">{esc(x)}</span>' for x in s['platform'])+f'<span class="badge">{esc(s["license"])}</span>'
 if s.get('host'): badges+=f'<span class="tag">{esc(s["host"])} 托管</span>'
 if s.get('archived'): badges+='<span class="badge">仓库已归档</span>'
 if s.get('bench'): badges+=f'<a class="chip bench" href="{BENCH}"{EXT}>OpenSDC-Bench 有评测结果 ↗</a>'
 ps=papers_of_sw[s['id']]
 release=f'（最新发布 {esc(s["release"])}）' if s.get('release') else ''
 rows=[('仓库',f'<a href="{esc(repo)}"{EXT}>{esc(short)} ↗</a>'),
  ('语言 / 构建',esc(' · '.join(x for x in (s.get('lang'),s.get('build')) if x))),
  ('最近提交',esc(s.get('pushed',''))+release if s.get('pushed') else ''),
  ('误差模式',esc(s.get('modes',''))),
  ('示例命令',f'<code>{esc(s["example"])}</code>' if s.get('example') else ''),
  ('对应论文',f'<span class="paperlist">{plinks(ps)}</span>' if ps else esc(s.get('paper_note','—'))),
  ('核验依据',esc(s.get('basis',''))),('备注',esc(s.get('note','')))]
 lic='std' if s['license'].startswith(STD) else 'other'; bench='1' if s.get('bench') else ''
 return f'<article class="item" id="sw-{esc(s["id"])}" data-group="{esc(s["group"])}" data-platform="{esc("|".join(s["platform"]))}" data-lic="{lic}" data-bench="{bench}"><div class="meta">{badges}</div><h3><a href="{esc(repo)}"{EXT}>{esc(s["name"])} ↗</a></h3><p>{esc(s["summary"])}</p>{kv(rows)}</article>'
platforms=sorted({x for s in software for x in s['platform']})
sw_groups,sw_side=grouped(swgroups,software,sw_item,'个仓库')
sw_filters=f'<label>类别<select data-filter="group"><option value="">全部类别</option>{opts(swgroups)}</select></label><label>平台<select data-filter="platform"><option value="">全部平台</option>{opts(platforms)}</select></label><label>许可证<select data-filter="lic"><option value="">不限</option><option value="std">标准开源许可证</option><option value="other">非标准或未声明</option></select></label><label class="check"><input type="checkbox" data-filter="bench">只看 OpenSDC-Bench 已有评测结果的</label>'
sw_stats=stats([(len(software),'代码仓库'),(sum(1 for p in papers if p['code']),'篇论文有公开代码'),(sum(1 for s in software if s['license'].startswith(STD)),'个采用标准开源许可证'),(sum(1 for s in software if s.get('bench')),'个已有 OpenSDC-Bench 结果')])
sw_howto=f'<section class="scope" id="howto"><h2>从下载到评估</h2><ol class="steps"><li><span class="n">01 · 取代码</span><b>先看许可证</b>条目列出仓库、许可证、主要语言和构建方式。标为“仓库未声明许可证”或“非标准模板”的代码，使用或再分发前需要先读 LICENSE 或联系作者。</li><li><span class="n">02 · 取数据</span><b>对上数据集和字段</b><a href="./datasets.html">数据集目录</a>列出各数据集的布局、大小和下载入口，以及哪些论文用过它。</li><li><span class="n">03 · 运行</span><b>以仓库文档为准</b>条目里的示例命令摘自各仓库 README，只用来说明调用方式。需要用同一套代码调用多个压缩器时，可以用 <a href="#sw-libpressio">LibPressio</a>。</li><li><span class="n">04 · 评估</span><b>用同一套口径</b><a href="{BENCHREPO}"{EXT}>OpenSDC-Bench ↗</a> 提供统一的误差界定义、计时方式和质量指标，<a href="{BENCH}"{EXT}>榜单 ↗</a> 已包含 SZ3、ZFP、SPERR、PFPL 和 Falcons。单独分析可用 <a href="#sw-qcat">QCAT</a> 或 <a href="#sw-z-checker">Z-checker</a>。</li></ol><p class="callout"><b>核验方式：</b>仓库逐个通过 GitHub 接口确认存在，并核对 README 是否引用对应论文，依据写在各条目里。论文卡片上的“未检索到公开代码”只表示按题名和系统名没有找到，不代表作者没有公开。许可证、语言和最近提交时间取自核查当日的仓库信息。</p></section>'
sw_body=f'<div class="eyebrow">CODE CATALOG · 核查于 {ASOF}</div><h1>压缩器与代码目录</h1><p class="subtitle">论文图谱里能找到公开代码的工作，以及常用基线和评测工具。<br>每个条目给出仓库、许可证、构建方式和对应论文。</p>{sw_stats}</header>{sw_howto}<section id="list"><div class="eyebrow">REPOSITORIES</div><h2>按类别浏览</h2>{controls(sw_filters,"例如：SZ3、GPU、粒子、KV")}</section>{sw_groups}'
(ROOT/'compressors.html').write_text(shell('压缩器与代码目录','数据压缩论文对应的开源压缩器、artifact 与评测工具：仓库、许可证、构建方式和对应论文。',sw_side,sw_body),encoding='utf-8')

def ds_item(d):
 ps=papers_of_ds[d['id']]
 links=' · '.join(f'<a href="{esc(l["url"])}"{EXT}>{esc(l["label"])} ↗</a>' for l in d.get('links',[])) or '未找到公开下载入口'
 badges=f'<span class="badge">{esc(d["domain"])}</span>'
 if d.get('bench'): badges+=f'<a class="chip bench" href="{BENCHREPO}/blob/main/datasets/README.md"{EXT}>OpenSDC-Bench 使用 ↗</a>'
 used=f'<details><summary>{len(ps)} 篇</summary><span class="paperlist">{plinks(ps)}</span></details>' if ps else '本清单中暂未标注'
 rows=[('布局',esc(d.get('layout',''))),('大小',esc(d.get('size',''))),('提供方',esc(d.get('provider',''))),('下载',links),('使用条件',esc(d.get('terms',''))),('评测子集',esc(d.get('bench',''))),('用过的论文',used)]
 bench='1' if d.get('bench') else ''
 return f'<article class="item" id="ds-{esc(d["id"])}" data-group="{esc(d["group"])}" data-bench="{bench}"><div class="meta">{badges}</div><h3>{esc(d["name"])}</h3>{kv(rows)}</article>'
dsgroups=list(dict.fromkeys(d['group'] for d in datasets))
dsorted=sorted(datasets,key=lambda d:-len(papers_of_ds[d['id']]))
ds_groups,ds_side=grouped(dsgroups,dsorted,ds_item,'个数据集')
ds_filters=f'<label>类别<select data-filter="group"><option value="">全部类别</option>{opts(dsgroups)}</select></label><label class="check"><input type="checkbox" data-filter="bench">只看 OpenSDC-Bench 使用的</label>'
ds_stats=stats([(len(datasets),'数据集与基准'),(sum(1 for d in datasets if d['group'].startswith('SDRBench')),'来自 SDRBench'),(sum(1 for p in papers if p['data']),'篇论文已标注数据集'),(sum(1 for d in datasets if d.get('bench')),'个用于 OpenSDC-Bench')])
ds_howto=f'<section class="scope" id="howto"><h2>获取与使用</h2><p><b>SDRBench：</b><a href="https://sdrbench.github.io/datasets.html"{EXT}>SDRBench 目录 ↗</a> 给出各数据集的归档下载链接，以及 SZ、ZFP、LibPressio 的命令示例。多数数据集另有 Hugging Face 镜像，可以用 <a href="./compressors.html#sw-sdrbench-py">sdrbench</a> Python 包按字段读取为 numpy 数组。</p><p><b>数组布局：</b>SDRBench 的数据是小端二进制裸数组。目录里的维度按最慢变化维在前（C 顺序）书写，例如 100×500×500；SZ、ZFP 的命令行参数则按最快变化维在前，传参时需要倒过来。</p><p><b>OpenSDC-Bench 子集：</b>榜单使用 NYX、CESM-ATM、Hurricane ISABEL、Miranda 和 SCALE-LETKF 的指定字段，字段、类型和形状见 <a href="{BENCHREPO}/blob/main/datasets/README.md"{EXT}>数据集说明 ↗</a> 和 <a href="{BENCHREPO}/blob/main/datasets/sdrbench-fields.json"{EXT}>字段清单 ↗</a>。</p><p class="callout"><b>标注方式：</b>论文与数据集的对应关系取自论文正文（少数取自摘要）里出现的数据集名称，只表示该论文用过这个数据集，不代表用了全部字段、同一版本或同一误差设置。没有拿到正文的论文暂未标注。</p></section>'
ds_body=f'<div class="eyebrow">DATASET CATALOG · 核查于 {ASOF}</div><h1>数据集目录</h1><p class="subtitle">压缩论文常用的科学数据集和基准负载：<br>布局、大小、下载入口，以及哪些论文用过。</p>{ds_stats}</header>{ds_howto}<section id="list"><div class="eyebrow">DATASETS</div><h2>按类别浏览</h2>{controls(ds_filters,"例如：NYX、宇宙学、SPEC、日志")}</section>{ds_groups}'
(ROOT/'datasets.html').write_text(shell('数据集目录','数据压缩论文常用的科学数据集与基准负载：布局、大小、下载入口和使用它的论文。',ds_side,ds_body),encoding='utf-8')
print(json.dumps({'main':len(main),'appendix':len(app),'venues':len(counts),'software':len(software),'datasets':len(datasets),'papers_with_code':sum(1 for p in papers if p['code']),'papers_with_data':sum(1 for p in papers if p['data']),'output':str(out)},ensure_ascii=False))
