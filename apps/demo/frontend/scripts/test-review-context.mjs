import assert from 'node:assert/strict'
import test from 'node:test'
import { evidenceContext, humanReviewIsCurrent } from '../src/features/cpa/review-context.ts'

test('object property order does not invalidate unchanged evidence', () => {
  assert.equal(evidenceContext({ output: 'a', inputs: { cash: 14, living: 1 } }), evidenceContext({ inputs: { living: 1, cash: 14 }, output: 'a' }))
})
test('output, claim tolerance, inputs and engine results invalidate a prior verdict', () => {
  const data = { output: 'a', claim: { tolerance: 0 }, inputs: { cash: 14 }, result: 3 }
  const context = evidenceContext(data)
  const log = { verdict: 'fixed', evidenceContext: context }
  assert.equal(humanReviewIsCurrent(log, context), true)
  for (const changed of [{ ...data, output: 'b' }, { ...data, claim: { tolerance: 1 } }, { ...data, inputs: { cash: 13 } }, { ...data, result: 4 }]) {
    assert.equal(humanReviewIsCurrent(log, evidenceContext(changed)), false)
  }
})
test('legacy verdict, unset verdict and loading context cannot approve current evidence', () => {
  assert.equal(humanReviewIsCurrent({ verdict: 'fixed' }, 'x'), false)
  assert.equal(humanReviewIsCurrent({ verdict: 'unset', evidenceContext: 'x' }, 'x'), false)
  assert.equal(humanReviewIsCurrent({ verdict: 'fixed', evidenceContext: 'x' }, null), false)
})
