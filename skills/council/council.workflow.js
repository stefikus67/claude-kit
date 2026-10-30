export const meta = {
  name: 'council',
  description: 'Big-decision council: 3 independent opinions with different lenses, then 1 judge that cites them (4 agents)',
  whenToUse: 'Only for big, costly or hard-to-reverse decisions, after the user has said yes to running a council',
  phases: [
    { title: 'Opinions', detail: '3 independent advisors, one lens each, run in parallel' },
    { title: 'Judge', detail: '1 judge weighs the opinions and cites them' },
  ],
}

// args: {
//   question:  string   (required) the decision, framed neutrally
//   options:   string[] (optional) the options on the table
//   context:   string   (required) facts, numbers, constraints, what was tried; framed by the caller
//   files:     string[] (optional) absolute paths the advisors may read
//   stakes:    string   (optional) what a wrong call costs
//   allowWeb:  boolean  (optional, default false) let advisors use web search
//   lenses:    [{id, name, brief}] (optional) replace the default three lenses; keep it at 3
//   opinionModel, judgeModel: string (optional) model overrides; omit to inherit the session model
// }

if (!args || typeof args !== 'object' || !args.question || !args.context) {
  throw new Error('council: pass args {question, context} at minimum (options, files, stakes optional)')
}

const DEFAULT_LENSES = [
  {
    id: 'O1',
    name: 'Downside',
    brief:
      'Assume the leading option is chosen and fails within six months. Find the most likely way it fails, ' +
      'what that costs (money, hours, reputation, relationships), and whether the choice can be undone. ' +
      'Look for costs nobody has priced, such as the user\'s own time. If every option looks safe, look harder.',
  },
  {
    id: 'O2',
    name: 'Reframe',
    brief:
      'Ignore how the question is framed. Work out what the user is actually trying to achieve, then check whether ' +
      'the options on the table serve it. Look for a missing option, a cheaper test that would settle the question ' +
      'before committing, or a sign that this decision does not need to be made now.',
  },
  {
    id: 'O3',
    name: 'Execution',
    brief:
      'Judge each option only by whether it can actually be done with the constraints given: the first concrete ' +
      'step tomorrow, hours per week, money, tools, and who else must agree. Prefer the option that gets a real ' +
      'result soonest with the least that can go wrong in the doing.',
  },
]

const lenses = Array.isArray(args.lenses) && args.lenses.length ? args.lenses.slice(0, 3) : DEFAULT_LENSES
if (Array.isArray(args.lenses) && args.lenses.length > 3) log('council: more than 3 lenses passed; only the first 3 are used')

const OPINION_SCHEMA = {
  type: 'object',
  properties: {
    recommendation: { type: 'string', description: 'The option you back, or a new option, in one sentence' },
    confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
    reasons: {
      type: 'array',
      maxItems: 4,
      items: {
        type: 'object',
        properties: {
          point: { type: 'string' },
          evidence: { type: 'string', description: 'Fact from the context or a file (path), or "judgment" if none' },
        },
        required: ['point', 'evidence'],
      },
    },
    biggest_risk: { type: 'string', description: 'The single biggest risk in your own recommendation' },
    would_change_my_mind: { type: 'string', description: 'The fact that would flip your recommendation' },
    unknowns: { type: 'array', items: { type: 'string' }, description: 'Missing facts that matter, max 3' },
  },
  required: ['recommendation', 'confidence', 'reasons', 'biggest_risk', 'would_change_my_mind'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', description: 'The recommended option, one sentence, no hedging' },
    confidence: { type: 'string', enum: ['low', 'medium', 'high'] },
    because: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          point: { type: 'string' },
          cites: { type: 'array', items: { type: 'string' }, description: 'Opinion IDs, e.g. ["O1","O3"]' },
        },
        required: ['point', 'cites'],
      },
    },
    clashes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          issue: { type: 'string' },
          sides: { type: 'string', description: 'Who said what, with IDs' },
          resolved_by: { type: 'string', description: 'Why the verdict sides as it does, or "unresolved: needs <fact>"' },
        },
        required: ['issue', 'sides', 'resolved_by'],
      },
    },
    strongest_dissent: {
      type: 'object',
      properties: { from: { type: 'string' }, point: { type: 'string' } },
      required: ['from', 'point'],
    },
    first_step: { type: 'string', description: 'One concrete action, doable this week' },
    would_change_verdict: { type: 'string' },
    stepan_decides: {
      type: 'array',
      items: { type: 'string' },
      description: 'Value or taste calls the council cannot make for the user',
    },
  },
  required: ['verdict', 'confidence', 'because', 'clashes', 'strongest_dissent', 'first_step', 'would_change_verdict', 'stepan_decides'],
}

const framed = [
  '<question>', args.question, '</question>',
  args.options && args.options.length ? '<options>\n- ' + args.options.join('\n- ') + '\n</options>' : '',
  '<context>', args.context, '</context>',
  args.stakes ? '<stakes>' + args.stakes + '</stakes>' : '',
  args.files && args.files.length ? '<files_you_may_read>\n' + args.files.join('\n') + '\n</files_you_may_read>' : '',
].filter(Boolean).join('\n')

const toolRule = args.allowWeb
  ? 'You may read the listed files and use web search for facts that change the answer. Cite URLs.'
  : 'You may read the listed files. Do not search the web. Work from the context and files only.'

function opinionPrompt(lens) {
  return [
    'You are one of three independent advisors on a decision for the user. The others use different lenses;',
    'you will not see their answers. Do not try to be balanced: give the strongest honest case from your lens.',
    '',
    '<lens name="' + lens.name + '">', lens.brief, '</lens>',
    '',
    framed,
    '',
    toolRule,
    'Do not change, send, post or install anything. Read only.',
    'Ground each reason in the context or a file path. Write "judgment" as the evidence where you have none.',
    'Plain, direct English. No preamble.',
  ].join('\n')
}

phase('Opinions')
const raw = await parallel(
  lenses.map((lens) => () =>
    agent(opinionPrompt(lens), {
      label: lens.id + ' ' + lens.name,
      phase: 'Opinions',
      schema: OPINION_SCHEMA,
      ...(args.opinionModel ? { model: args.opinionModel } : {}),
    }).then((op) => (op ? { id: lens.id, lens: lens.name, ...op } : null))
  )
)
const opinions = raw.filter(Boolean)
if (opinions.length < 2) {
  log('council: only ' + opinions.length + ' opinion(s) came back; stopping before the judge')
  return { question: args.question, opinions, verdict: null, warnings: ['fewer than 2 opinions returned'] }
}
if (opinions.length < lenses.length) log('council: one opinion is missing; the judge works with ' + opinions.length)

phase('Judge')
const judgePrompt = [
  'You are the judge on a decision council for the user. Three advisors answered independently, each from one lens.',
  'Weigh their arguments on evidence, not on how many agree. You may overrule a majority if the evidence supports it.',
  'Every point in "because" must cite the opinion IDs it rests on (O1, O2, O3). Do not introduce new facts;',
  'if a missing fact decides the question, say so in clashes as "unresolved: needs <fact>" and lower confidence.',
  'Keep the strongest dissent, do not smooth it away. Value or taste calls go to stepan_decides.',
  '',
  framed,
  '',
  '<opinions>',
  ...opinions.map((o) => '<opinion id="' + o.id + '" lens="' + o.lens + '">\n' + JSON.stringify(o, null, 2) + '\n</opinion>'),
  '</opinions>',
  '',
  'Do not read files or search; judge from what is above.',
].join('\n')

const verdict = await agent(judgePrompt, {
  label: 'Judge',
  phase: 'Judge',
  schema: VERDICT_SCHEMA,
  effort: 'high',
  ...(args.judgeModel ? { model: args.judgeModel } : {}),
})

// Deterministic check: the judge must cite real opinion IDs.
const warnings = []
const ids = new Set(opinions.map((o) => o.id))
if (!verdict) {
  warnings.push('judge returned nothing')
} else {
  const uncited = (verdict.because || []).filter((b) => !b.cites || !b.cites.some((c) => ids.has(c)))
  if (uncited.length) warnings.push(uncited.length + ' verdict point(s) cite no valid opinion ID')
  const used = new Set((verdict.because || []).flatMap((b) => b.cites || []))
  const ignored = [...ids].filter((id) => !used.has(id))
  if (ignored.length) warnings.push('judge never cited: ' + ignored.join(', '))
}
warnings.forEach((w) => log('council warning: ' + w))

return { question: args.question, opinions, verdict, warnings, agentRuns: opinions.length + (verdict ? 1 : 0) }
