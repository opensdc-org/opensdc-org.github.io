"""Build the static survey page. Python 3.9+; standard library only."""
import json,html,pathlib,collections,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
esc=lambda x:html.escape(str(x),quote=True)
papers=json.loads((ROOT/'data/papers.json').read_text(encoding='utf-8'))
required=['id','title','venue','year','url','problem','method','results','scenario','evidence','status','tags']
for p in papers:
 for key in required:
  if key not in p: raise ValueError(f"Missing {key}: {p.get('id')}")
 if p['status'] not in ['main','appendix']: raise ValueError(f"Invalid status: {p['id']}")
 if not isinstance(p['year'],int): raise ValueError(f"Invalid year: {p['id']}")
 if not p['url'].startswith(('https://','http://')): raise ValueError(f"Invalid URL: {p['id']}")
venues=['SC','PPoPP','ICS','HPDC','SOSP','OSDI','EuroSys','FAST','USENIX ATC','NSDI','ISCA','HPCA','MICRO','ASPLOS','SIGCOMM','DAC']
for p in papers:
 if p['venue']=='ATC':p['venue']='USENIX ATC'
 if p['venue'] not in venues:venues.append(p['venue'])
 p['status']=p.get('status','main');p.setdefault('caveat','');p.setdefault('tags',[])
 p['selection']='专题补充' if p.get('select_reason') else '主要检索范围'
 aliases={'AI/HPC融合':'AI融合','GPU加速':'GPU','无损压缩':'无损','有损压缩':'有损','内存缓存':'内存压缩','I/O':'I/O与检查点','质量性能权衡':'性能权衡','学习式压缩':'学习压缩'}
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
<details><summary>展开核心方法与适用场景</summary><div class="details-grid"><p><span class="field-label">核心方法 / 系统设计</span>{esc(p['method'])}</p><p><span class="field-label">适用数据 / 场景</span>{esc(p['scenario'])}</p></div></details><p class="caveat">{esc(p['caveat'])}</p><div class="sources">{''.join(links)}</div></article>'''
nav=''.join(f'<a href="#venue-{esc(v.replace(" ","-"))}">{esc(v)} <small>{counts[v]}</small></a>' for v in venues if counts[v])
groups=''.join(f'<section class="venue-group" id="venue-{esc(v.replace(" ","-"))}"><div class="venue-head"><h2>{esc(v)}</h2><span>{counts[v]} 篇主清单论文</span></div>'+''.join(card(p) for p in main if p['venue']==v)+'</section>' for v in venues if counts[v])
rows=''.join('<tr><td><a href="#venue-'+esc(v.replace(' ','-'))+'">'+esc(v)+'</a></td>'+''.join('<td>'+str(sum(p['venue']==v and p['year']==y for p in main))+'</td>' for y in range(2019,2027))+f'<td><b>{counts[v]}</b></td></tr>' for v in venues if counts[v])
coverage=f'<div class="tablewrap"><table><thead><tr><th>发表场所</th>'+''.join(f'<th>{y}</th>' for y in range(2019,2027))+'<th>合计</th></tr></thead><tbody>'+rows+'</tbody></table></div>'
scope=(ROOT/'content/scope.html').read_text(encoding='utf-8')

opts=lambda a:''.join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in a)
page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="2019–2026 HPC、系统与体系结构顶会数据压缩论文，按会议组织、逐条来源核验与趋势分析。"><title>数据压缩研究图谱 · 2019–2026</title><link rel="stylesheet" href="./assets/styles.css"></head><body id="top"><div class="layout"><aside aria-label="目录"><div class="brand">COMPRESSION<br>RESEARCH ATLAS</div><a href="#scope">范围与收录标准</a><a href="#coverage">覆盖情况</a><a href="#catalog">论文筛选</a><a href="#trends">发展趋势 · 10条</a><a href="#appendix">待核验 / 边缘相关</a><h3>按发表场所跳转</h3>{nav}<p class="note">检索截至<br>2026-11-13<br><br>OpenSDC 文献整理<br>来源与核验范围见各条目</p></aside><main><header><nav class="site-links" aria-label="OpenSDC 导航"><a href="https://opensdc-org.github.io/zh.html">← 返回 OpenSDC</a><a href="https://opensdc-org.github.io/benchmark/">评测与榜单 →</a></nav><div class="eyebrow">LITERATURE REVIEW · 2019—2026</div><h1>数据压缩研究图谱</h1><p class="subtitle">HPC / 系统 / 体系结构顶会与精选重要工作<br>从科学数据减量到内存、通信与加速器协同设计</p><div class="stats"><div class="stat"><strong>{len(main)}</strong><span>主清单论文</span></div><div class="stat"><strong>{len(counts)}</strong><span>会议 / 期刊系列</span></div><div class="stat"><strong>{len(app)}</strong><span>附录条目</span></div><div class="stat"><strong>2019–26</strong><span>检索年份</span></div></div><p class="mobile-nav"><a href="#catalog">论文目录</a> · <a href="#trends">趋势总结</a> · <a href="#appendix">附录</a></p></header>
<section class="scope" id="scope"><h2>检索范围与收录标准</h2>{scope}</section>
<section id="coverage"><div class="eyebrow">COVERAGE</div><h2>按发表场所与年份查看覆盖情况</h2><p class="note">单元格为当前主清单篇数，包含已标注状态的2026录用记录；附录不计入。数字描述检索结果，不用于判断学科发表量变化。</p>{coverage}</section>
<section id="catalog"><div class="eyebrow">PAPER CATALOG</div><h2>按发表场所组织的论文清单</h2><p>每条包含问题、方法、关键结果、场景与核验来源。默认展开问题与结果；可按需展开方法，或一次展开全部。</p><div class="filters"><div class="controls"><label>检索题目、方法、结果或主题<input id="search" type="search" placeholder="例如：GPU、误差、通信、KV、SZ、checkpoint"></label><label>发表场所<select id="venue"><option value="">全部发表场所</option>{opts([v for v in venues if counts[v]])}</select></label><label>年份<select id="year"><option value="">全部年份</option>{opts(range(2026,2018,-1))}</select></label><label>主题标签<select id="tag"><option value="">全部主题</option>{opts(sorted(set(t for p in papers for t in p['tags'])))}</select></label><label>证据文本包含<select id="evidence"><option value="">全部证据层级</option><option value="正文">正文</option><option value="全文">全文</option><option value="摘要">摘要</option><option value="记录">记录</option></select></label><label>清单范围<select id="listmode"><option value="all">主清单与附录</option><option value="main">只看主清单</option><option value="appendix">只看附录</option></select></label><label>收录范围<select id="selection"><option value="">全部收录范围</option><option value="主要检索范围">主要检索范围</option><option value="专题补充">专题补充</option></select></label></div><div class="toolbar"><button id="reset">重置筛选</button><button id="expand">展开当前条目</button><button id="collapse">收起方法详情</button><button id="print">打印 / 另存PDF</button><span class="resultcount" id="resultcount" aria-live="polite"></span></div></div><noscript>浏览器未启用JavaScript：完整论文内容仍可阅读，筛选功能不可用。</noscript><p class="empty" id="empty" hidden>没有匹配条目，请调整筛选或点击重置。</p></section>
<div id="papers">{groups}</div>
<section id="trends"><div class="eyebrow">SYNTHESIS</div><h2>近几年数据压缩的发展趋势</h2><p class="callout">以下按研究主题梳理相关进展，各节附对应论文。仅有摘要或录用记录的工作，其实验与部署情况以条目中的核验说明为准。</p>{trends}<h3>科学压缩的几条算法主线</h3><p>预测型路线从局部回归/插值发展到SZ3模块化组合、QoZ/HPEZ质量驱动自调优；变换型路线包括SPERR的小波与嵌入编码、MGARD的多层误差控制；张量路线由TTHRESH代表，利用全局低秩相关性并在中低码率改善率失真。无损路线如ndzip/LC则保留每个浮点位，适合不能容忍数值改动的任务。它们解决不同约束，不宜用单一“最佳压缩器”概括。</p><p class="refs">证据：{refs(['tbd23-sz3','sc22-qoz','sigmod24-hpez','ipdps23-sperr','tc22-mgardplus','tvcg20-tthresh','dcc21-ndzip','sc21-ndzip','asplos25-float'])}</p><h3>阅读实验结果时应保持的口径</h3><ul><li><b>压缩比：</b>通常是原始字节/压缩后字节；“提高N%”与“为原来的N倍”不同。模型权重、元数据与训练成本是否计入须看原文。</li><li><b>吞吐与加速：</b>GB/s可能按原始输入计算；压缩器、通信原语、I/O或端到端应用的收益不能互相代替。最大值不是平均值。</li><li><b>质量：</b>绝对/相对误差界、PSNR、任务准确率和数值稳定性分别回答不同问题；“无精度损失”不能自动视作逐位无损。</li><li><b>可比性：</b>硬件型号、节点数、数据形状、误差设置、数据可压缩性和基线实现共同决定结果。比较时需同时考虑这些条件。</li></ul></section>
<section id="appendix" class="appendix"><div class="eyebrow">APPENDIX</div><h2>待核验 / 边缘相关</h2><p>下列条目不计入主清单论文数。这里既包括压缩核心性或证据尚待确认的候选，也保留少量已确认的范围排除案例；具体原因逐条列出。附录不按发表场所等级划分；各条目列明核验状态或主题边界。</p>{''.join(card(p) for p in app)}</section>
<section id="search-notes"><h2>检索方法与覆盖边界</h2><p>检索组合包括会议名称/年份与 compression、data reduction、scientific、lossy、error-bounded、decompression、compressed memory/cache、gradient/KV、deduplication、progressive、GPU 等词。使用会议目录与官方程序发现候选，结合作者发表列表追踪同一工作不同标题/预印本，最终以ACM/IEEE/USENIX、会议官方页、作者公开原稿或机构仓储核对。</p><p>排除相同工作的重复预印本与代码版本；没有看到实验数字时保留“未报告/未核实”，不从基线论文、相关新闻或名称推断结果。2019作为回溯起点，主要密集覆盖2020–2026。扩展会议为主题补充；SIGMOD/VLDB/ICDE等数据库顶会、纯图像/视频编码顶会以及扩展期刊未作为完整检索池，不能以本页判断这些领域的全貌。</p><p class="note">条目所依据的摘要、正文与官方记录已分别标注。尚缺精确误差设置、硬件配置或表格基线的条目已在证据与备注中保留边界。外部链接可能随时间迁移，DOI与USENIX入口优先保留。</p></section>
<footer>整理语言：中文 · 文献题名保留英文 · 截至2026-11-13 · 文献题录与研究趋势<br>OpenSDC · 专题文献整理 · 实验结果按论文报告记录，未进行独立复现。</footer></main></div><a href="#top" class="toplink">回到顶部 ↑</a><script type="application/json" id="paper-data">{json.dumps(papers,ensure_ascii=False).replace('</', r'<\/')}</script><script src="./assets/app.js" defer></script></body></html>'''
out=ROOT/'index.html'
out.write_text(page,encoding='utf-8')
print(json.dumps({'main':len(main),'appendix':len(app),'venues':len(counts),'output':str(out)},ensure_ascii=False))
