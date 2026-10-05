from pathlib import Path
from html import escape
import json
from collections import Counter
import sys

OUT = Path(__file__).resolve().parent
INDEX = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / '.cache/ethereum-execution-spec-tests/cached_downloads/ethereum/execution-specs/tests%40v21.0.0/fixtures/fixtures/.meta/index.json'
WIRE = 'wirex-consume/'
REORG = 'reorg-suite/'

if INDEX.exists():
    index = json.loads(INDEX.read_text())
    amsterdam = [t for t in index['test_cases'] if t['fork'] == 'Amsterdam']
    counts = Counter(t['format'] for t in amsterdam)
    x_cases = [t for t in amsterdam if t['format'] == 'blockchain_test_engine_x']
    groups = {t['pre_hash'] for t in x_cases}
    legacy_groups = {t['pre_hash'] for t in x_cases if '/ported_static/' in t['id']}
    data = {
        'release': 'v21.0.0', 'fork_filter': 'Amsterdam',
        'index_created_at': index['created_at'], 'index_root_hash': index['root_hash'],
        'index_path': 'v21.0.0/fixtures/.meta/index.json', 'counts': dict(counts),
        'engine_x_pre_hash_groups': len(groups),
        'groups_containing_ported_static': len(legacy_groups),
        'engine_x_cases_per_group': len(x_cases) / len(groups),
        'sync_all_forks': dict(Counter(t['fork'] for t in index['test_cases']
                                       if t['format'] == 'blockchain_test_sync')),
        'counting_method': 'Count test_cases entries with fork exactly Amsterdam, grouped by format. Formats overlap. Count distinct pre_hash values for EngineX.',
    }
    (OUT / 'fixture-counts.json').write_text(json.dumps(data, indent=2) + '\n')
else:
    data = json.loads((OUT / 'fixture-counts.json').read_text())
    counts = Counter(data['counts'])

def text(x, y, value, cls='label', anchor='middle'):
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{escape(value)}</text>'

def box(x, y, w, h, title, sub='', tone=''):
    cy = y + h / 2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" class="node {tone}"/>'
            + text(x+w/2, cy-5 if sub else cy+7, title, 'node-title')
            + (text(x+w/2, cy+24, sub, 'node-sub') if sub else ''))

def edge(path, tone='', dashed=False):
    marker = 'mint' if tone == 'mint' else 'violet' if tone == 'violet' else 'amber' if tone == 'amber' else 'gray'
    return f'<path d="{path}" class="edge {tone} {"dashed" if dashed else ""}" marker-end="url(#{marker}-arrow)"/>'

def svg(name, content, height=350, width=1040):
    return f'<figure class="diagram"><svg role="img" aria-label="{escape(name)}" viewBox="0 0 {width} {height}">{content}</svg></figure>'

def source(path, line, base=WIRE):
    label = ('reorg-suite/' if base == REORG else 'wirex-consume/') + path
    return f'<li><code>{escape(label)}:{line}</code></li>'

def notes(body, sources=''):
    return '<details class="notes"><summary>Discussion notes &amp; sources</summary><div class="notes-body">'+body+('<ul class="sources">'+sources+'</ul>' if sources else '')+'</div></details>'

def section(id, number, title, intro, body, extra='', cmd=''):
    command = f'<code class="command">{escape(cmd)}</code>' if cmd else ''
    return f'<section class="slide" id="{id}" data-title="{escape(title)}"><div class="inner"><div class="section-top"><span class="section-number">{number} / 10</span>{command}</div><h2>{title}</h2><p class="lead">{intro}</p>{body}{extra}</div></section>'

# Overview: each route names the actual client entry point.
hero_diagram = svg('Consume delivers fixture data to an isolated client. Execute sends transactions into a network.',
    text(50,35,'CONSUME','svg-kicker','start')
    + box(30,62,180,85,'Fixtures','filled offline','violet')
    + edge('M210 104 H270','violet')
    + box(282,62,300,85,'Client under test','Engine / import / devp2p','violet')
    + text(50,219,'EXECUTE','svg-kicker','start')
    + box(30,246,180,85,'Python tests','live transactions','mint')
    + edge('M210 288 H270','mint')
    + box(282,246,300,85,'Network','EL peers + consensus','mint')
    + text(306,395,'Controlled fixtures. Native network interactions.','label'),420,620)
cover = f'''<section class="slide cover" id="overview" data-title="Overview"><div class="inner"><div class="section-top"><span class="section-number">01 / 10</span><span class="edition">execution-specs</span><span class="crops-badge" title="Censorship resistance, Open source, Privacy, Security">CROPS</span></div><div class="hero"><div><h1>Execution client<br><span>test routes</span></h1><p class="hero-lead">A discussion map of <strong>consume</strong> and <strong>execute</strong>.</p><p class="hero-sub">Which interface? Which environment?<br>How much client reuse?</p><div class="hero-links"><a href="#routes" class="primary-link">Explore consume <span aria-hidden="true">↗</span></a><a href="#remote" class="text-link">Jump to execute</a></div></div><div>{hero_diagram}</div></div><div class="cover-footer"><span>Censorship resistance / Open source / Privacy / Security</span><span>WireX &amp; reorg include unmerged work</span><span>Scroll freely · arrow keys to navigate</span></div></div></section>'''

# Engine and startup import, shown as equal-sized routes.
c = text(28,32,'ENGINE','svg-kicker','start') + text(28,174,'RLP','svg-kicker','start')
c += box(20,52,185,80,'Engine fixture','payloads + checks','violet')
c += edge('M205 92 H280','violet')
c += box(292,52,220,80,'Simulator','newPayload + forkchoice','violet')
c += edge('M512 92 H617','violet')
c += text(565,73,'Engine API','edge-label')
c += box(630,52,230,80,'Client under test','payload validation','violet')
c += edge('M860 92 H908') + text(953,100,'✓','check')
c += text(427,156,'fixture chain','node-sub')
c += text(514,156,'G','chain-label') + edge('M538 148 H575','violet')
c += text(601,156,'T₁','chain-label') + edge('M626 148 H661','violet')
c += text(690,156,'…','chain-label') + edge('M714 148 H749','violet')
c += text(777,156,'Tₙ','chain-label')
c += box(20,194,185,80,'Blockchain fixture','RLP-encoded blocks','amber')
c += edge('M205 234 H280','amber')
c += box(292,194,220,80,'Hive startup','genesis + /blocks/*.rlp','amber')
c += edge('M512 234 H617','amber') + text(565,215,'Offline import','edge-label')
c += box(630,194,230,80,'Client under test','client import adapter','amber')
c += edge('M860 234 H908') + text(953,242,'✓','check')
routes = section('routes','02','Engine API and startup import',
    'A broad test corpus reaches the client through different block-ingestion paths.',
    svg('Engine fixture chains start at genesis G and deliver T1 through Tn using Engine API calls. RLP fixtures enter through files imported when the client starts.',c,292)
    + '<div class="fact-row"><p><strong class="violet-text">Engine / EngineX</strong><br>Standard Engine API. Post-Merge.</p><p><strong class="amber-text">RLP</strong><br>Out-of-protocol import. Also covers PoW.</p><p><strong>Assertions</strong><br>Engine responses / RLP final head.</p></div>',
    notes('<p>Engine and RLP complement each other because they enter different client code paths. Engine checks payload validity/rejection responses and API errors. The client validates the payload state root internally. RLP writes the genesis and ordered block files into Hive, then checks the final canonical block hash over JSON-RPC. The client chooses how its startup adapter reaches the import pipeline.</p><p>These are broadly generated formats for applicable state and blockchain cases. Format restrictions, source markers and simulator skips mean that “every case” is not literal.</p>',
          source('docs/running_tests/running.md',91)
          + source('packages/testing/src/execution_testing/cli/pytest_commands/plugins/consume/simulators/simulator_logic/test_via_rlp.py',1)
          + source('docs/running_tests/test_formats/blockchain_test_engine_x.md',1)),
    'consume engine / enginex / rlp')

# X architecture: independent branches, never imply fixture chains continue each other.
c = text(28,32,'STANDARD','svg-kicker','start') + text(578,32,'X ARCHITECTURE','svg-kicker','start')
for i,y in enumerate([55,130,205]):
    c += box(25,y,148,62,'Start client',tone='amber') + edge(f'M173 {y+31} H207','amber')
    c += box(220,y,115,62,f'Test {i+1}',tone='amber') + edge(f'M335 {y+31} H369')
    c += box(382,y,115,62,'Stop',tone='neutral')
c += '<path d="M539 45 V278" class="divider"/>'
c += box(571,119,177,85,'Start once','shared genesis G','mint')
for i,y in enumerate([55,130,205]):
    c += edge(f'M748 161 H782 V{y+31} H817','mint')
    c += box(830,y,165,62,f'G → Test {i+1}',tone='mint')
c += text(784,284,'Independent chains rooted at the same genesis','node-sub')
x = section('reuse','03','Shared genesis, fewer client starts',
    'Compatible fork, genesis settings and accounts share a genesis, so one boot runs many tests.',
    svg('Standard simulators start and stop a client for each test. X architecture runs independent fixture chains against one shared genesis client.',c,300)
    + '<div class="metrics"><div><strong>26,357</strong><span>Amsterdam EngineX fixtures</span></div><div><strong class="mint-text">996</strong><span>distinct pre-allocation groups</span></div><div><strong>26.5×</strong><span>fewer planned base starts per client</span></div></div>'
    + '<p class="callout">Legacy cleanup can cut more startups. <strong>512 / 996</strong> groups contain ported static tests.</p>',
    notes('<p><strong>How grouping works:</strong> the filler groups compatible fork, chain ID, genesis environment and fixed-account footprints. Reserved/shared addresses must agree. It then merges private allocations and refills tests against that shared pre-state. Each fixture references its group using <code>pre_hash</code>. The group shares a genesis. The consumer’s group key combines <code>pre_hash</code> and client implementation.</p><p><strong>EngineX</strong> resets forkchoice to genesis for each fixture. <strong>WireX</strong> reuses the client without that reset, orders valid paths first and isolates every target of multi-target fixtures. Reuse does not make one test the continuation of another.</p><p>The 26.5× figure is 26,357 ÷ 996, a planned base-start count comparison, not a measured runtime speedup. WireX can need extra isolated or replacement clients. Legacy fixed-address allocations contribute 507 exclusive ported-static groups, but not all are removable.</p>',
          source('docs/running_tests/test_formats/blockchain_test_engine_x.md',1)
          + source('docs/running_tests/consume/wirex.md',32)
          + source('packages/testing/src/execution_testing/cli/pytest_commands/plugins/consume/simulators/helpers/test_tracker.py',45)),
    'consume enginex / wirex')

# WireX: a thin Engine control plane above a strong transport route.
c = text(27,32,'MOCK PEER, REAL CLIENT SYNC','svg-kicker','start')
c += box(28,110,190,90,'WireX runner','fixture expectations','violet')
c += box(305,110,245,90,'Mock devp2p peer','deterministic chain','mint')
c += box(740,110,263,90,'Client under test','full-sync ingestion','mint')
c += edge('M218 155 H292','violet') + text(257,137,'chain','edge-label')
c += edge('M550 155 H727','mint') + text(645,132,'devp2p','edge-label mint-text')
c += text(645,181,'headers + bodies','node-sub')
c += edge('M123 110 V65 H870 V97','violet',True)
c += text(505,52,'Engine API announces sync target S','edge-label')
c += text(514,262,'G', 'chain-label') + edge('M538 254 H575','mint')
c += text(601,262,'T₁','chain-label') + edge('M626 254 H661','mint')
c += text(690,262,'…','chain-label') + edge('M714 254 H749','mint')
c += text(777,262,'Tₙ','chain-label') + edge('M803 254 H839','violet',True)
c += text(870,262,'S','chain-label')
c += text(427,291,'fixture blocks over devp2p','node-sub') + text(923,291,'sync target','node-sub')
wirex = section('wirex','05','WireX: the production peer path',
    'The mock serves missing ancestry over devp2p. The Engine API tells the client where to sync.',
    svg('WireX configures a deterministic mock peer, announces a target using Engine API, and checks that the client receives fixture ancestry over devp2p.',c,310)
    + '<div class="fact-row"><p><strong class="mint-text">In-protocol ingestion</strong><br>RLPx / eth, headers and block bodies.</p><p><strong>Broad input corpus</strong><br>Uses the existing EngineX fixture format.</p><p><strong class="violet-text">Planned RLP replacement</strong><br>Initially post-Merge. Shared client startup.</p></div>',
    notes('<p><strong>Unmerged work.</strong> The intent is to replace post-Merge <code>consume rlp</code> with the client’s actual devp2p block-ingestion path and reduce startup overhead. It is not a complete historical-sync conformance suite.</p><p><code>S</code> illustrates an extra framework sync target above authored blocks <code>T₁…Tₙ</code>. Resolved targets can also use authored-chain fallbacks. The consumer checks validity/rejection and, where topology guarantees transport, records which required headers and nonempty bodies the mock served by block hash.</p><p>Some malformed, undecodable or otherwise unrepresentable chains are skipped. A multi-target fixture uses isolated clients per target. The 26,357 Amsterdam EngineX entries are the available input corpus, not a promise that every entry or path runs in WireX.</p>',
          source('docs/running_tests/consume/wirex.md',1)
          + source('docs/running_tests/running.md',186)
          + source('packages/testing/src/execution_testing/fixtures/blockchain.py',1034)),
    'consume wirex · WIP')

# Real-client source and target, different roles even when implementation matches.
c = text(28,32,'TWO REAL CLIENT ROLES','svg-kicker','start')
c += box(25,133,220,86,'Sync fixture','chain + sync target','violet')
c += box(382,133,237,86,'Source EL','populated via Engine','amber')
c += box(784,133,237,86,'Target EL','downloads ancestry','mint')
c += edge('M245 176 H369','violet') + text(307,151,'Engine API','edge-label')
c += edge('M619 176 H771','mint') + text(701,151,'devp2p','edge-label mint-text')
c += box(396,36,210,55,'Simulator',tone='violet')
c += edge('M606 64 H902 V120','violet',True) + text(782,49,'Engine API: target S + forkchoice','edge-label')
c += text(514,243,'G','chain-label') + edge('M538 235 H575','mint')
c += text(601,243,'T₁','chain-label') + edge('M626 235 H661','mint')
c += text(690,243,'…','chain-label') + edge('M714 235 H749','mint')
c += text(777,243,'Tₙ','chain-label') + edge('M803 235 H839','violet',True)
c += text(870,243,'S','chain-label')
c += text(697,268,'Same genesis, independently selected client implementations','node-sub')
sync = section('sync','06','Sync: client-to-client integration',
    'A real source serves a real target. WireX replaces the source with a deterministic mock.',
    svg('A sync fixture populates a source EL through Engine API. The simulator tells a second EL about a target head. The target downloads ancestry from the source over devp2p.',c,288)
    + '<div class="sync-summary"><div class="large-number">9<span>Amsterdam fixtures</span></div><div><strong>Dedicated format, selected tests</strong><p><code>blockchain_test_sync</code> comes from <code>verify_sync</code> marks.</p><p>RLP block-size limit: boundaries, transaction types, logs, withdrawals.</p></div></div>'
    + '<p class="callout">Compatible devp2p bugs in both clients can pass unnoticed. Mixed-client pairs make this strong integration coverage.</p>',
    notes('<p><a href="https://github.com/ethereum/execution-spec-tests/pull/2007" target="_blank" rel="noreferrer">PR #2007</a> introduced consume sync in August 2025, with EIP-7934 RLP-size-limit tests. The v21 index has 18 sync entries: 9 Osaka and 9 Amsterdam.</p><p>Amsterdam’s nine cases comprise two valid boundary cases (limit−1 and limit), five transaction types (0–4), one logs case and one withdrawals case. This is selective sync coverage, not a special fixture for the whole corpus.</p><p>The simulator connects the clients, submits the extra empty tip <code>S</code> to the target with <code>newPayload</code> and <code>forkchoiceUpdated</code>, waits for convergence and checks expected state. Shared compatible transport bugs can be masked, while state and payload checks still catch many failures.</p><p>The overview docs list “Simulator: None”, but the implementation defines the Hive suite <code>eels/consume-sync</code>.</p>',
          source('packages/testing/src/execution_testing/cli/pytest_commands/plugins/consume/simulators/sync/conftest.py',314)
          + source('packages/testing/src/execution_testing/cli/pytest_commands/plugins/consume/simulators/simulator_logic/test_via_sync.py',243)
          + source('tests/osaka/eip7934_block_rlp_limit/test_max_block_rlp_size.py',644)),
    'consume sync')

# A deliberately illustrative DAG with interactive canonical head.
c = text(28,31,'SCRIPTED BRANCH SWITCHES','svg-kicker','start')
c += box(35,109,134,70,'Genesis',tone='neutral') + edge('M169 144 H223')
c += box(236,109,164,70,'Fork point',tone='neutral')
c += '<g class="branch branch-a active" data-branch="a">' + edge('M400 144 H454 V76 H508','violet')
c += box(521,42,157,68,'A₁',tone='violet') + edge('M678 76 H754','violet')
c += box(767,42,157,68,'A₂ / head',tone='violet') + '</g>'
c += '<g class="branch branch-b" data-branch="b">' + edge('M400 144 H454 V218 H508','mint')
c += box(521,184,157,68,'B₁',tone='mint') + edge('M678 218 H754','mint')
c += box(767,184,157,68,'B₂ / head',tone='mint') + '</g>'
c += text(662,148,'Engine API: forkchoiceUpdated','edge-label')
c += text(310,278,'A → B → A','chain-label')
c += text(710,278,'assert after each transition','node-sub')
reorg = section('reorg','07','Reorg: state across branch changes',
    'A block DAG and a script control delivery, forkchoice and assertions at each step.',
    svg('An illustrative block DAG branches at a shared fork point. Engine forkchoice changes which branch is canonical, and assertions check each transition.',c,292)
    + '<div class="reorg-controls"><div class="segmented" role="group" aria-label="Choose canonical branch"><button class="selected" data-head="a" aria-pressed="true">Head A</button><button data-head="b" aria-pressed="false">Head B</button></div><span id="head-status" role="status">A is canonical</span><span class="diagram-caption">Illustrative DAG</span></div>'
    + '<div class="fact-row"><p><strong>Dedicated reorg fixture</strong><br><code>blockchain_test_engine_reorg</code></p><p><strong>Engine + JSON-RPC</strong><br>Head, state, receipts, logs, txpool.</p><p><strong class="violet-text">Fresh client per fixture</strong><br>Dedicated suite. Unmerged work.</p></div>',
    notes('<p>The new <code>ReorgTest</code> emits a DAG plus scripted Engine/JSON-RPC steps. Fixtures can describe head, safe and finalized explicitly. The consumer follows allowed response branches and checks observable state during the script.</p><p>The authored suite covers branch switches and rewinds, invalid branches, out-of-order delivery, deep reorgs, fork transitions, rollback, receipts/logs and transaction reinjection. One case adds a real peer to deliver a chain by devp2p sync. Peer clients currently use the same implementation as the main client.</p><p>Format support starts at Paris. The authored suite starts at Cancun and includes later fork transitions. This format is not in v21. The diagram is an illustrative topology, not a rendering of one fixture.</p>',
          source('docs/running_tests/test_formats/blockchain_test_engine_reorg.md',1,REORG)
          + source('packages/testing/src/execution_testing/cli/pytest_commands/plugins/consume/simulators/simulator_logic/test_via_reorg.py',646,REORG)
          + source('tests/reorg/test_sync_delivery.py',31,REORG)),
    'consume reorg · WIP')

rows = [
    ('Engine','routes','Engine API','blockchain_test_engine','Per fixture',f"{counts['blockchain_test_engine']:,}"),
    ('EngineX','reuse','Engine API','blockchain_test_engine_x','Per group',f"{counts['blockchain_test_engine_x']:,}"),
    ('RLP','routes','Startup files','blockchain_test','Per fixture',f"{counts['blockchain_test']:,}"),
    ('WireX <small>WIP</small>','wirex','devp2p + Engine target','blockchain_test_engine_x','Per group*',f"{counts['blockchain_test_engine_x']:,}†"),
    ('Sync','sync','devp2p + Engine target','blockchain_test_sync','Client pair',f"{counts['blockchain_test_sync']:,}"),
    ('Reorg <small>WIP</small>','reorg','Engine + JSON-RPC','blockchain_test_engine_reorg','Per fixture','—'),
]
table = '<div class="table-wrap"><table><thead><tr><th>Route</th><th>Client entry</th><th>Fixture format</th><th>Lifecycle</th><th class="numeric">Amsterdam</th></tr></thead><tbody>'
for name,id,interface,fmt,lifecycle,count in rows:
    table += f'<tr><td><a href="#{id}">{name}</a></td><td>{interface}</td><td><code>{fmt}</code></td><td>{lifecycle}</td><td class="numeric">{count}</td></tr>'
table += '</tbody></table></div>'
scope = section('scope','08','Amsterdam: corpus and routes',
    'v21.0.0 fixture entries, filtered to fork = Amsterdam. The formats overlap.',
    table + '<div class="table-footnotes"><p>† WireX reuses EngineX inputs, with path-specific skips. * Multi-target fixtures need isolated clients.</p><p>Reorg is absent from this release. Counts describe fixture entries, not unique test ideas.</p></div>'
    + '<div class="scope-secondary"><span><strong>16,896</strong> state fixtures</span><span><strong>92</strong> transaction fixtures</span><span>Index generated 23 September 2026</span></div>',
    notes('<p>These are counts of entries in <code>test_cases</code> with <code>fork == "Amsterdam"</code>, grouped by <code>format</code>. One authored case can produce several formats. WireX’s row refers to the same EngineX entries, so rows must not be added together as independent test coverage.</p><p>The index contains 354,203 entries across all included forks and formats. Amsterdam has 96,025 entries across its six released formats. Fork-transition entries are excluded by the exact-fork filter.</p><p><code>fixture-counts.json</code> stores the counts, index timestamp and root hash. <code>build.py</code> reproduces them from the supplied index.</p>',
          '<li><a href="https://github.com/ethereum/execution-specs/releases/tag/tests%40v21.0.0">v21.0.0 fixture release</a> · <code>.meta/index.json</code></li>'))

# Remote: native network prominent, EL and CL drawn as actual separate roles.
c = text(28,31,'STAGING / DEVNET / LIVE NETWORK','svg-kicker','start')
c += '<rect x="394" y="38" width="620" height="223" rx="6" class="network-boundary"/>'
c += box(25,130,220,100,'Python tests','fund · deploy · transact','mint')
c += edge('M245 180 H421','mint') + text(338,155,'JSON-RPC','edge-label mint-text')
c += box(434,140,158,80,'EL₁','RPC entry','mint')
c += box(624,140,158,80,'EL₂','peer','mint')
c += box(815,140,158,80,'EL₃','peer','mint')
c += edge('M592 180 H611','mint') + edge('M782 180 H802','mint')
for cx in [513,703,894]:
    c += box(cx-58,54,116,55,'CL',tone='violet')
    c += edge(f'M{cx} 109 V127','violet')
c += text(704,247,'EL propagation + consensus-driven inclusion','node-sub')
c += edge('M513 220 V285 H135 V243','gray',True)
c += text(331,272,'RPC state assertions','edge-label')
remote = section('remote','09','Execute remote: tests in the network',
    'The test submits transactions. A native EL / CL network includes them and advances the chain.',
    svg('Execute remote turns Python tests into funding, deployment and test transactions. JSON-RPC submits to an EL node in a real network, with EL peers and CL interaction. RPC reads assert the resulting state.',c,308)
    + '<div class="fact-row"><p><strong class="mint-text">Test source, no fixture JSON</strong><br>Pre-state becomes real setup transactions.</p><p><strong>Native interactions</strong><br>Mempool, block production, EL and CL.</p><p><strong>Test-state assertions</strong><br>Expected account and contract state.</p></div>',
    notes('<p>Consume gives a client controlled fixture input in Hive. Execute remote brings eligible Python tests into an existing staging or live network through its normal transaction interface. It must adapt funding, deployments, addresses and fees to that environment.</p><p>The default remote mode relies on an existing beacon node to advance the chain. An optional <code>--engine-endpoint</code> configuration instead drives an EL manually. The diagram shows the default live-network mode.</p><p>Network and consensus interfaces participate implicitly in execution. The tool asserts test state, not complete network health or an exhaustive assertion on every interface. The docs explicitly say it does not detect overall network instability or forks. Fork transitions and some genesis-dependent tests are unsupported.</p>',
          source('docs/running_tests/execute/index.md',16)
          + source('docs/running_tests/execute/remote.md',29)
          + source('docs/running_tests/execute/remote.md',70)),
    'execute remote')

# Blobs retrieval, inclusion downstream, Hive small aside.
c = text(28,31,'BLOB POOL RETRIEVAL','svg-kicker','start')
c += box(28,90,218,94,'Python blob tests','transaction + sidecar','mint')
c += edge('M246 137 H419','mint') + text(335,112,'JSON-RPC submit','edge-label')
c += box(432,90,224,94,'EL blob pool','pending blob data','mint')
c += edge('M656 137 H797','violet') + text(730,78,'engine_getBlobsV*','edge-label')
c += box(810,90,199,94,'Blobs + proofs','check contents','violet')
c += edge('M544 184 V236 H832','gray',True)
c += text(646,222,'then wait for inclusion','edge-label') + text(884,244,'block','node-title')
blobs = section('execute-hive','10','Execute blobs and the Hive harness',
    'Blob tests submit network-wrapped transactions, then verify blob retrieval through the Engine API.',
    svg('Blob tests send transactions and sidecars over JSON-RPC into the EL blob pool. The test calls engine_getBlobs to check blobs and proofs, then waits for inclusion.',c,263)
    + '<div class="execute-asides"><div><h3 class="mint-text">eels/execute-blobs</h3><p>Hive simulator using <code>execute hive<br>-m blob_transaction_test</code>.</p><p>Available / missing blobs, proofs and newer retrieval variants.</p></div><div><h3>execute hive</h3><p>Controlled single EL. The harness supplies the consensus role.</p><p>Useful for execute plumbing and regression checks, alongside client checks.</p></div></div>',
    notes('<p><code>execute-blobs</code> is the Hive simulator name, not a standalone <code>execute blobs</code> CLI subcommand. It executes Python <code>BlobsTest</code> cases through <code>execute hive -m blob_transaction_test</code>. There is no filled JSON fixture format or count for it in the v21 index.</p><p>The test requests blobs/proofs with <code>engine_getBlobsV*</code> after sending the transaction and before waiting for inclusion. Without Engine RPC, submission still runs but retrieval checks are skipped.</p><p>Execute Hive creates a controlled, funded single-client session and uses Engine API calls to build/import payloads and set forkchoice. It is useful for checking the execute harness and regressions. The docs also classify it as client system testing, so it can catch client bugs too.</p>',
          source('docs/running_tests/execute/hive.md',47)
          + source('packages/testing/src/execution_testing/execution/blob_transaction.py',393)
          + '<li><code>hive/simulators/ethereum/eels/execute-blobs/Dockerfile:23</code></li>'),
    'execute remote / hive · eels/execute-blobs')


# Measured, matched Hive run pairs. Keep this separate from v21 corpus counts.
bench = json.loads((OUT / 'timings.json').read_text())
def duration(seconds):
    rounded = round(seconds)
    hours, remainder = divmod(rounded, 3600)
    minutes, seconds = divmod(remainder, 60)
    return (f'{hours}h ' if hours else '') + f'{minutes}m {seconds:02d}s'
chart = '<figure class="benchmark-chart" aria-label="Measured Engine and EngineX suite wall-clock times for three clients"><div class="benchmark-labels"><span>Client</span><span>Suite wall-clock time</span><span>Speedup</span></div>'
benchmark_sources = ''
for client in bench['clients']:
    engine = client['engine_seconds']
    enginex = client['enginex_seconds']
    ratio = engine / enginex
    chart += f'<div class="benchmark-row"><h3>{client["name"]}</h3><div class="bar-pair"><div class="bar-line"><span>Engine</span><div class="bar-track"><i class="engine-bar" style="width:100%"></i></div><strong>{duration(engine)}</strong></div><div class="bar-line"><span>EngineX</span><div class="bar-track"><i class="enginex-bar" style="width:{enginex/engine*100:.3f}%"></i></div><strong>{duration(enginex)}</strong></div></div><div class="speedup">{ratio:.1f}×</div></div>'
    engine_url = 'https://hive.ethpandaops.io/generic/results/' + client['engine_run'] + '.json'
    enginex_url = 'https://hive.ethpandaops.io/generic/results/' + client['enginex_run'] + '.json'
    benchmark_sources += f'<li>{client["name"]} <code>{client["version"]}</code> · <a href="{engine_url}" target="_blank" rel="noreferrer">Engine result</a> · <a href="{enginex_url}" target="_blank" rel="noreferrer">EngineX result</a></li>'
chart += '</figure>'
timings = section('timings','04','Engine vs EngineX: measured time',
    'Paris–Osaka + transitions. v20.0.1. 54,438 cases. Four workers. July 2026.',
    chart + '<p class="benchmark-caption">Each pair uses the same client image. Bars normalize to that client’s Engine time.</p><p class="callout">Shared genesis turns hours of client starts into minutes of test execution.</p>',
    notes('<p>Measured daily Hive suite wall-clock spans from July 16–17, 2026, recovered from the saved July 19 dashboard analysis. These are historical runs, not a new benchmark or today’s latest dashboard result.</p><p>Each pair matches host, fixture release, test count, worker count, check-time limit and client image. Timing includes extraction and simulator/client startup, and excludes Docker image builds. The suite covers Paris through Osaka and transitions, including 23 BPO transition cases, but excludes standalone BPO fork suites.</p><p>Nimbus is excluded because cascade failures distort its duration. Erigon and Besu are excluded because their paired images differ, with Besu also using an older fixture release. This is observed suite acceleration, not a controlled repeated benchmark. Exact seconds, versions and public result IDs are preserved in <code>timings.json</code>.</p>', benchmark_sources),
    'eels/consume-engine / eels/consume-enginex')

style = r'''
:root{color-scheme:dark;--bg:#0b0e14;--panel:#10151e;--line:#29313e;--text:#edf1f7;--muted:#a5afbf;--dim:#687588;--violet:#b7a6fb;--mint:#9ae5c7;--amber:#efbc84;--nav:64px;font-family:Inter,"Segoe UI",Arial,sans-serif;font-synthesis:none}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:0}body{margin:0;background:var(--bg);color:var(--text);line-height:1.45}a{color:inherit;text-decoration:none}button{font:inherit;color:inherit;cursor:pointer}button:focus-visible,a:focus-visible,summary:focus-visible{outline:2px solid var(--mint);outline-offset:5px}button:hover,a:hover{color:var(--mint)}code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;font-size:.83em}p{margin:0}header{height:var(--nav);position:fixed;inset:0 0 auto;z-index:20;display:flex;align-items:center;gap:24px;padding:0 4vw;background:rgba(11,14,20,.94);border-bottom:1px solid var(--line);backdrop-filter:blur(15px)}.brand{font-size:14px;font-weight:700;letter-spacing:.04em;white-space:nowrap}.brand span{color:var(--muted);font-weight:400}nav{display:flex;align-items:center;gap:21px;flex:1}nav a{font-size:13px;color:var(--muted);padding:22px 0;white-space:nowrap;position:relative}nav a.active{color:var(--text)}nav a.active:after{content:"";height:2px;background:var(--mint);position:absolute;bottom:0;inset-inline:0}.header-tools{display:flex;gap:8px;align-items:center}.header-tools button{border:1px solid var(--line);background:transparent;border-radius:7px;width:31px;height:30px;font-size:15px}.page-count{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;min-width:36px}.progress{position:fixed;z-index:25;top:0;left:0;height:2px;background:var(--mint);width:0;transition:width .15s}.slide{min-height:100svh;display:flex;align-items:center;padding:calc(var(--nav) + 26px) 5vw 35px;border-bottom:1px solid #202733;scroll-margin-top:0}.inner{width:100%;max-width:1120px;margin:auto}.section-top{display:flex;align-items:center;gap:20px;min-height:21px;margin-bottom:14px}.section-number{font-family:Consolas,monospace;color:var(--dim);font-size:12px;letter-spacing:.08em}.command{color:var(--muted);font-size:13px}.edition{color:var(--muted);font-size:14px}h1,h2,h3{line-height:1.12;letter-spacing:-.035em;font-weight:550;margin:0}h2{font-size:clamp(32px,3.3vw,47px);margin-bottom:12px}h3{font-size:22px;letter-spacing:-.02em}.lead{font-size:clamp(18px,1.65vw,22px);color:var(--muted);margin-bottom:24px;max-width:1040px}.hero{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center;margin-top:37px}h1{font-size:clamp(52px,5.5vw,78px);letter-spacing:-.055em;line-height:1.08}h1 span{color:var(--violet)}.hero-lead{font-size:24px;color:var(--muted);margin-top:27px}.hero-lead strong{color:var(--text);font-weight:500}.hero-sub{font-size:19px;color:var(--muted);margin-top:20px}.hero-links{display:flex;align-items:center;gap:26px;margin-top:35px;font-size:15px}.primary-link{padding:12px 17px;border:1px solid #665a94;border-radius:8px;background:#1d1930}.primary-link span{margin-left:14px;color:var(--violet)}.text-link{color:var(--muted)}.cover-footer{margin-top:55px;border-top:1px solid var(--line);padding-top:18px;display:flex;justify-content:space-between;gap:20px;color:var(--dim);font-size:12px}.diagram{margin:0;width:100%;border:1px solid var(--line);border-radius:18px;padding:12px;background:radial-gradient(ellipse at 90% 0%,#19213380,transparent 65%),var(--panel)}.cover .diagram{background:transparent;border:none;padding:0}.diagram svg{width:100%;height:auto;display:block;overflow:visible}.node{fill:#151c28;stroke:#3b475a;stroke-width:1.25}.node.violet{fill:#1d1a2e;stroke:#7968b0}.node.mint{fill:#132922;stroke:#568e77}.node.amber{fill:#2a221c;stroke:#9b7956}.node.neutral{fill:#141b25;stroke:#465368}.edge{stroke:#718199;fill:none;stroke-width:2}.edge.mint{stroke:var(--mint);stroke-width:2.6}.edge.violet{stroke:var(--violet)}.edge.amber{stroke:var(--amber)}.edge.dashed{stroke-dasharray:6 5;stroke-width:1.6}.node-title{fill:var(--text);font-size:22px;font-weight:550;letter-spacing:-.025em}.node-sub{fill:var(--muted);font-size:17px}.label{fill:var(--muted);font-size:20px}.edge-label{fill:var(--muted);font-size:17px}.svg-kicker{fill:var(--dim);font-size:13px;font-weight:600;letter-spacing:.14em}.chain-label{fill:var(--text);font-size:23px;font-family:Consolas,monospace}.check{fill:var(--mint);font-size:30px}.divider{stroke:#2f3744;stroke-width:1}.network-boundary{fill:#101c2080;stroke:#344c46;stroke-dasharray:5 6;stroke-width:1}.violet-text{color:var(--violet);fill:var(--violet)}.mint-text{color:var(--mint);fill:var(--mint)}.amber-text{color:var(--amber);fill:var(--amber)}.fact-row{display:grid;grid-template-columns:repeat(3,1fr);gap:30px;margin-top:21px;font-size:17px;color:var(--muted)}.fact-row strong{display:inline-block;font-weight:550;margin-bottom:4px;color:var(--text)}.fact-row strong.violet-text{color:var(--violet)}.fact-row strong.mint-text{color:var(--mint)}.fact-row strong.amber-text{color:var(--amber)}.metrics{display:flex;gap:65px;margin-top:20px}.metrics>div{display:flex;align-items:baseline;gap:12px}.metrics strong{font-size:35px;font-weight:500;letter-spacing:-.04em}.metrics span{font-size:14px;color:var(--muted);max-width:160px}.callout{border-left:2px solid var(--violet);padding:2px 0 2px 15px;font-size:16px;color:var(--muted);margin-top:20px}.callout strong{color:var(--text);font-weight:550}.notes{margin-top:20px;color:var(--muted);font-size:13px}.notes summary{display:inline-flex;align-items:center;gap:8px;cursor:pointer;list-style:none;padding:3px 0}.notes summary:before{content:"+";font-size:16px;color:var(--violet)}.notes[open] summary:before{content:"−"}.notes-body{border-top:1px solid var(--line);margin-top:12px;padding-top:17px;font-size:17px;line-height:1.6;max-width:1000px}.notes-body p+p{margin-top:12px}.notes-body a{color:var(--violet);text-decoration:underline}.sources{list-style:none;padding:0;margin-top:19px}.sources li{margin-top:7px;overflow-wrap:anywhere;font-size:14px;color:var(--dim)}.sync-summary{display:flex;align-items:center;gap:43px;margin-top:21px}.large-number{font-size:58px;line-height:1;color:var(--mint);font-weight:450;display:flex;align-items:center;gap:16px}.large-number span{font-size:15px;line-height:1.4;color:var(--muted);max-width:100px}.sync-summary strong{font-size:18px;font-weight:550}.sync-summary p{font-size:16px;color:var(--muted);margin-top:4px}.reorg-controls{display:flex;align-items:center;gap:20px;margin-top:14px;color:var(--muted);font-size:15px}.segmented{display:flex;border:1px solid var(--line);border-radius:8px;padding:3px;gap:3px}.segmented button{border:0;background:transparent;border-radius:5px;font-size:14px;padding:7px 17px;color:var(--muted)}.segmented button.selected{background:#302744;color:var(--violet)}.segmented button[data-head=b].selected{background:#18352a;color:var(--mint)}.diagram-caption{margin-left:auto;color:var(--dim);font-size:12px}.branch{opacity:.5;transition:opacity .3s}.branch.active{opacity:1}.table-wrap{border-block:1px solid var(--line)}table{width:100%;border-collapse:collapse;font-size:17px}th{text-align:left;color:var(--dim);font-size:12px;font-weight:500;padding:12px 10px}td{padding:15px 10px;border-top:1px solid #222a37;color:var(--muted)}td:first-child{color:var(--text);font-weight:550;width:12%}td code{font-size:13px;white-space:nowrap}td small{font-size:9px;color:var(--violet);vertical-align:middle;letter-spacing:.05em;margin-left:4px}.numeric{text-align:right;font-variant-numeric:tabular-nums}.numeric:not(th){font-size:23px;color:var(--text)}tbody tr:hover{background:#141a25}.table-footnotes{margin-top:15px;color:var(--muted);font-size:14px}.table-footnotes p+p{margin-top:5px}.scope-secondary{margin-top:24px;display:flex;gap:40px;font-size:14px;color:var(--dim)}.scope-secondary strong{font-weight:500;color:var(--muted)}.execute-asides{display:grid;grid-template-columns:1fr 1fr;gap:45px;margin-top:23px}.execute-asides>div+div{border-left:1px solid var(--line);padding-left:38px}.execute-asides h3{margin-bottom:9px}.execute-asides p{font-size:17px;color:var(--muted)}.execute-asides p+p{margin-top:8px}.execute-asides code{color:var(--text);font-size:14px}dialog{background:var(--panel);color:var(--text);border:1px solid #4d596b;border-radius:14px;max-width:430px;padding:27px}dialog::backdrop{background:#0009;backdrop-filter:blur(5px)}dialog h3{margin-bottom:18px}dialog dl{display:grid;grid-template-columns:95px 1fr;gap:12px;font-size:15px}dialog dt{font-family:Consolas,monospace;color:var(--mint)}dialog dd{margin:0;color:var(--muted)}dialog button{margin-top:18px;background:#202a38;border:1px solid var(--line);border-radius:6px;padding:8px 18px}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
@media(min-width:1600px){.inner{max-width:1240px}.slide{padding-top:100px}.diagram{padding:16px}.lead{font-size:23px}}
@media(max-width:1120px){header{gap:16px;padding-inline:3vw}nav{gap:15px}nav a{font-size:12px}.brand span{display:none}.metrics{gap:35px}.metrics>div{gap:9px}.metrics span{font-size:13px}.metrics strong{font-size:31px}.fact-row{font-size:15px}td{font-size:15px}td code{font-size:12px}.hero{gap:20px}.hero-sub{font-size:17px}}
@media(max-width:800px){:root{--nav:58px}header{gap:10px}.brand{font-size:12px}nav{overflow-x:auto;gap:15px}nav a{font-size:11px}.header-tools .page-count,.header-tools button[data-action=prev],.header-tools button[data-action=next]{display:none}.slide{min-height:100svh;padding:85px 5vw 34px}.hero{grid-template-columns:1fr;margin-top:20px}.hero .diagram{max-width:530px;margin:26px auto 0}h1{font-size:52px}.hero-lead{font-size:20px;margin-top:19px}.hero-links{margin-top:24px}.cover-footer{margin-top:20px;flex-wrap:wrap;font-size:11px}.diagram{padding:8px;border-radius:12px;overflow-x:auto}.slide:not(.cover) .diagram svg{min-width:900px}.fact-row{gap:16px;font-size:14px}.metrics{gap:18px}.metrics>div{display:block}.metrics strong{font-size:29px}.metrics span{display:block;max-width:160px;margin-top:4px}.sync-summary{gap:20px}.large-number{font-size:48px}.large-number span{max-width:80px;font-size:12px}.sync-summary p{font-size:14px}.sync-summary strong{font-size:16px}.callout{font-size:14px}.table-wrap{overflow-x:auto}table{min-width:900px}.scope-secondary{gap:18px;flex-wrap:wrap}.execute-asides{gap:20px}.execute-asides>div+div{padding-left:20px}.execute-asides p{font-size:15px}.execute-asides code{font-size:12px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}

@media(max-height:820px) and (min-width:801px){.slide{padding-top:80px;padding-bottom:10px}.section-top{margin-bottom:8px}h2{font-size:40px;margin-bottom:10px}.lead{font-size:20px;margin-bottom:16px}.diagram{padding:10px}.fact-row{margin-top:16px;font-size:16px}.metrics{margin-top:16px}.metrics strong{font-size:32px}.callout{margin-top:12px;font-size:15px}.notes{margin-top:12px}.sync-summary{margin-top:16px}.sync-summary p{font-size:15px}.reorg-controls{margin-top:10px}.execute-asides{margin-top:18px}.execute-asides p{font-size:16px}td{padding-block:10px;font-size:16px}th{padding-block:10px}.numeric:not(th){font-size:22px}.table-footnotes{margin-top:10px}.scope-secondary{margin-top:18px}}
@media print{header,.progress,.notes,.hero-links,.reorg-controls,dialog{display:none!important}body{background:var(--bg);print-color-adjust:exact;-webkit-print-color-adjust:exact}.slide{min-height:0;height:190mm;page-break-after:always;padding:10mm 9mm;border:0}.inner{max-width:none}.hero{margin:0}h1{font-size:50px}h2{font-size:32px}.lead{font-size:16px}.diagram{padding:8px}.fact-row,.execute-asides p{font-size:13px}.callout{font-size:12px}.metrics strong{font-size:25px}.metrics span{font-size:11px}.metrics{gap:35px}.cover-footer{margin-top:20px}.table-footnotes{font-size:11px}td{padding:10px;font-size:13px}.scope-secondary{font-size:11px}.numeric:not(th){font-size:18px}@page{size:A4 landscape;margin:0}}
'''

style += r'''
/* Restrained CROPS / cypherpunk direction. No external fonts or assets. */
:root{--bg:#080b0a;--panel:#0d1210;--line:#2b352f;--text:#f0f4ed;--muted:#acb8ae;--dim:#77857b;--mint:#b4f65e;--violet:#b4bfd6;--amber:#e6b06e}
body{background-image:linear-gradient(#b4f65e03 1px,transparent 1px),linear-gradient(90deg,#b4f65e03 1px,transparent 1px);background-size:48px 48px}
header{background:rgba(8,11,10,.96)}.brand,nav,.edition,.command,.crops-badge,.cover-footer,.svg-kicker,.metrics span{font-family:Consolas,"Liberation Mono",monospace}
nav{gap:16px}nav a{font-size:12px}.header-tools button{border-radius:3px}.slide{border-bottom-color:#26302a}h1 span{color:var(--mint)}
.crops-badge{font-size:10px;letter-spacing:.15em;color:var(--mint);border:1px solid #566e3c;padding:3px 7px;line-height:1.2}
.primary-link{border-radius:3px;border-color:#617f3d;background:#142010}.primary-link span{color:var(--mint)}
.diagram{border-radius:5px;background:var(--panel)}.node{fill:#101813;stroke:#44594a}.node.violet{fill:#141920;stroke:#687891}.node.mint{fill:#162111;stroke:#729b44}.node.amber{fill:#211b13;stroke:#9b7956}.node.neutral{fill:#111713;stroke:#455b4a}
.network-boundary{fill:#111b0e80;stroke:#526a3f}.divider{stroke:#344036}.segmented{border-radius:3px}.segmented button{border-radius:2px}.segmented button.selected{background:#26303e}.segmented button[data-head=b].selected{background:#223a16}
.callout{border-left-color:var(--mint)}.notes summary:before{color:var(--mint)}.notes-body a{color:var(--mint)}dialog{border-radius:5px;background:var(--panel)}
@media(max-width:1120px){nav{gap:12px}nav a{font-size:11px}}
@media(max-width:800px){nav{gap:12px}.diagram{border-radius:4px}.cover-footer{font-size:10px}}
'''

style += r'''
.benchmark-chart{margin:0;padding:19px 24px;border:1px solid var(--line);background:var(--panel);border-radius:5px}
.benchmark-labels,.benchmark-row{display:grid;grid-template-columns:135px 1fr 95px;gap:20px;align-items:center}.benchmark-labels{font-family:Consolas,monospace;color:var(--dim);font-size:12px;padding-bottom:10px}.benchmark-labels span:last-child{text-align:right}.benchmark-row{padding:19px 0;border-top:1px solid var(--line)}.benchmark-row h3{font-size:23px}.bar-pair{display:grid;gap:13px}.bar-line{display:grid;grid-template-columns:66px 1fr 138px;gap:14px;align-items:center;font-size:13px;color:var(--muted)}.bar-line>span{font-family:Consolas,monospace}.bar-line strong{font-size:18px;font-weight:500;text-align:right;font-variant-numeric:tabular-nums;color:var(--text)}.bar-track{height:12px;background:#1a241c}.bar-track i{display:block;height:100%}.engine-bar{background:#687789}.enginex-bar{background:var(--mint)}.speedup{font-size:34px;font-weight:500;letter-spacing:-.045em;color:var(--mint);text-align:right}.benchmark-caption{color:var(--muted);font-size:14px;margin-top:15px}
@media(max-width:800px){.benchmark-chart{overflow-x:auto}.benchmark-row,.benchmark-labels{min-width:850px}.benchmark-row{padding-block:15px}}
@media print{.benchmark-chart{padding:12px}.benchmark-row{padding-block:12px}}
'''

script = r'''
(() => {
  const sections = [...document.querySelectorAll('.slide')];
  const links = [...document.querySelectorAll('nav a')];
  const counter = document.querySelector('.page-count');
  const progress = document.querySelector('.progress');
  const help = document.querySelector('#help');
  let current = 0;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function refresh() {
    const target = innerHeight * .36;
    current = sections.reduce((best,s,i) => Math.abs(s.getBoundingClientRect().top - 64) < Math.abs(sections[best].getBoundingClientRect().top - 64) ? i : best, 0);
    const containing = sections.findIndex(s => { const r = s.getBoundingClientRect(); return r.top <= target && r.bottom > target; });
    if (containing >= 0) current = containing;
    links.forEach(a => { const active = a.hash === '#'+sections[current].id; a.classList.toggle('active',active); if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current'); });
    counter.textContent = String(current+1).padStart(2,'0')+' / 10';
    progress.style.width = ((current+1)/sections.length*100)+'%';
  }
  function go(index) { sections[Math.max(0,Math.min(sections.length-1,index))].scrollIntoView({behavior:reduced?'instant':'smooth',block:'start'}); }
  let queued = false;
  addEventListener('scroll',() => { if(!queued){queued=true;requestAnimationFrame(()=>{refresh();queued=false;});} },{passive:true});
  addEventListener('resize',refresh);
  document.querySelectorAll('[data-action]').forEach(b => b.addEventListener('click',()=>{
    if(b.dataset.action==='prev')go(current-1);
    if(b.dataset.action==='next')go(current+1);
    if(b.dataset.action==='help')help.showModal();
  }));
  help.querySelector('button').addEventListener('click',()=>help.close());
  help.addEventListener('click',e=>{if(e.target===help)help.close();});
  addEventListener('keydown',e=>{
    if(help.open || /INPUT|TEXTAREA|SELECT/.test(e.target.tagName) || e.ctrlKey || e.metaKey || e.altKey)return;
    if(e.key==='ArrowRight' || e.key==='PageDown'){e.preventDefault();go(current+1);}
    if(e.key==='ArrowLeft' || e.key==='PageUp'){e.preventDefault();go(current-1);}
    if(e.key==='Home'){e.preventDefault();go(0);}
    if(e.key==='End'){e.preventDefault();go(sections.length-1);}
    if(e.key.toLowerCase()==='n'){const d=sections[current].querySelector('details');if(d)d.open=!d.open;}
    if(e.key==='?')help.showModal();
    if(e.key.toLowerCase()==='f'){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen().catch(()=>{});}
  });
  document.querySelectorAll('[data-head]').forEach(b=>b.addEventListener('click',()=>{
    const chosen=b.dataset.head;
    document.querySelectorAll('[data-head]').forEach(button=>{const selected=button.dataset.head===chosen;button.classList.toggle('selected',selected);button.setAttribute('aria-pressed',String(selected));});
    document.querySelectorAll('[data-branch]').forEach(branch=>branch.classList.toggle('active',branch.dataset.branch===chosen));
    document.querySelector('#head-status').textContent=chosen.toUpperCase()+' is canonical';
  }));
  refresh();
})();
'''

nav = [('overview','Overview'),('routes','Engine / RLP'),('reuse','Reuse'),('timings','Timings'),('wirex','WireX'),('sync','Sync'),('reorg','Reorg'),('scope','Corpus'),('remote','Remote'),('execute-hive','Blobs / Hive')]
markers = ''.join(f'<marker id="{name}-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker>' for name,color in [('gray','#7a877d'),('mint','#b4f65e'),('violet','#b4bfd6'),('amber','#e6b06e')])
html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="A visual discussion map of execution-specs consume and execute testing routes."><title>Execution client test routes</title><style>'''+style+'''</style></head><body><div class="progress" aria-hidden="true"></div><svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs>'''+markers+'''</defs></svg><header><a class="brand" href="#overview">EELS <span>/ test routes</span></a><nav aria-label="Topics">'''+''.join(f'<a href="#{id}">{label}</a>' for id,label in nav)+'''</nav><div class="header-tools"><span class="page-count">01 / 10</span><button data-action="prev" aria-label="Previous topic">‹</button><button data-action="next" aria-label="Next topic">›</button><button data-action="help" aria-label="Keyboard shortcuts">?</button></div></header><main>'''+''.join([cover,routes,x,timings,wirex,sync,reorg,scope,remote,blobs])+'''</main><dialog id="help" aria-labelledby="help-title"><h3 id="help-title">Presentation controls</h3><dl><dt>← / →</dt><dd>Previous / next topic</dd><dt>PgUp / PgDn</dt><dd>Previous / next topic</dd><dt>Home / End</dt><dd>First / last topic</dd><dt>N</dt><dd>Toggle current topic’s notes</dd><dt>F</dt><dd>Toggle fullscreen</dd><dt>?</dt><dd>Show these controls</dd></dl><button>Close</button></dialog><script>'''+script+'''</script></body></html>'''
(OUT / 'index.html').write_text(html)
(OUT / 'README.md').write_text('''# Execution client test routes

Open `index.html` directly in a browser. It is self-contained and works offline. No service, build step, external font or package installation is required.

Ten scrollable topics cover Engine/RLP routes, shared-genesis reuse, measured timings, WireX, sync, reorg, Amsterdam fixture counts, execute remote, and execute-blobs/Hive. Arrow keys or Page Up/Down move between topics. `N` toggles the current topic’s discussion notes. `F` toggles fullscreen. Click Head A / Head B on the reorg diagram to change the illustrative canonical branch.

The default layouts target a laptop viewport of 1280×720 or larger. Use browser fullscreen for presentation. A print stylesheet is included for landscape output.

## Sources

Primary docs: `docs/running_tests/running.md` in the supplied `wirex-consume` worktree and linked consume/execute docs. Implementation was checked in that worktree.

Reorg: the supplied `reorg-suite` worktree, including its format docs, consumer and dedicated tests. WireX and reorg are explicitly marked as unmerged work.

Sync history: https://github.com/ethereum/execution-spec-tests/pull/2007

Counts: the supplied v21.0.0 `.meta/index.json`. Count entries whose fork is exactly `Amsterdam`, grouped by format. Formats overlap. WireX uses the EngineX input corpus, with eligibility limitations. Reorg is not included in the release index. Execute runs source tests and has no corresponding count in that fixture index.

`fixture-counts.json` records the index timestamp, root hash, counts and grouping statistics. `build.py` rebuilds the HTML and counts using Python’s standard library. It uses the original cached index when available, or the bundled count snapshot otherwise. Pass an index path to refresh the counts:

```sh
python3 build.py
python3 build.py /path/to/.meta/index.json
```

The 26.5× comparison describes planned base client starts for EngineX, not measured runtime. More grouping reduction remains in legacy allocations. Optional discussion notes in the HTML include implementation qualifications and source references.

Measured timing provenance, exact durations, client images and public Hive result IDs are in `timings.json`. The timing slide compares matched v20.0.1 Paris–Osaka runs from July 2026, rather than the Amsterdam v21 corpus.

Published with GitHub Pages at https://danceratopz.github.io/consume-execute-overview/.
''')
print(f'Created {OUT / "index.html"} ({len(html.encode()):,} bytes)')
