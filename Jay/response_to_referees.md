# Response to Referees — Four Rounds

**Manuscript:** *Coordination Without a Coordinator: A Scientific Programme for Hormone-Inspired Residual-Demand Signalling* (title changed in Round 4; previously *…for Hormone-Inspired Distributed Systems*)
**Revised manuscript:** `paper.pdf` — 11 pages, 3 figures, 3 tables, 32 references, Appendix A. Compiled clean (0 overfull boxes, 0 undefined references).
**This letter covers:** Round 1 (both reports, on the original 5-page draft), Round 2 (both reports, on the revised 6-page manuscript), Round 3 (both reports, on the 8-page manuscript), and Round 4 (both reports, on the 9-page manuscript). Each round's responses describe the changes made in that round; the page history is 5 → 6 → 8 → 9 → 11.

**Headline changes in this revision (Round 2):**

1. **The central law is now demonstrated, not just stated.** New Fig. 3 numerically integrates the closed loop through a demand pulse: with the antagonist term β > 0 the system recovers to baseline; with β = 0 production ratchets permanently — the fibrotic failure mode, shown (§3.2).
2. **Eq. 1's causality is fixed and the loop is closed.** The signal flux is now explicitly constitutive (p₀, *not* p₀ + u); the loop closes through the responder pool; the residual's non-negativity is structural (receptor-mediated clearance proportional to responder availability), written [p₀ − c(t)]₊ (Eqs. 1–2, §3.2).
3. **The P3 novelty claim survives a harder prior-art test.** Two nearest-miss families — congestion control/back-pressure (Kelly et al. 1998) and antithetic integral feedback (Briat et al. 2016) — are now cited, tabulated and scored; the claim is restated as the *combination* (§2.6, Table 1).
4. **The cost claim is now a five-component vector** (C_agent, C_medium, S_agent, S_medium, L) rather than a dual ledger (§4.1).
5. **The programme is tightened throughout**: biologically anchored delay ranges, a derived-not-chosen Phase-II threshold, a perturbation-and-recovery battery, a pilot-scoped inverse-design search with a stated central hypothesis and an information-restriction ladder, five-tier baselines with budget parity, a substrate-fidelity audit before the pilots, phase diagrams for Phase V, and honest grading of kill-criterion strength.
6. **Medzhitov (2008) corrected** to Nature 454, 428 (the spliced Cell 140, 771 entry was indeed a different, later paper). Full citation pass run; all other spot-checked entries were verified by Referee 2 and re-verified here.

---

## ROUND 1 — Referee 1

### R1-1. "The central biological idea is promising, but currently oversimplified" — distinguish biological mechanism / idealised control law / engineering principle.

**Done in Round 1; strengthened in Round 2.** §3.2 now presents the mechanism explicitly at three labelled levels (*Mechanism / Control law / Engineering principle*), and the control law is introduced as "a deliberately reduced control motif extracted from one component of the richer regulation described above — a model of the abstraction, not of the biology" — exactly the "reduced motif vs complete mechanism" distinction. The Mechanism paragraph already flags that TPO clearance couples to platelet and megakaryocyte mass and that emergency granulopoiesis layers further regulation on G-CSF. *(Location: §3.2.)*

### R1-2. Eq. 1 without a decay term is monotone — "something rather like the fibrosis pathology"; investigate u̇ = γr − β(u − u₀).

**Done in Round 1; now demonstrated.** Eq. 1 carries the antagonist term −β(u − u₀), and the text draws the referee's own conclusion: "P3 supplies demand adaptation, P5 supplies reversibility… Return to homeostasis requires the antagonist." Round 2 goes further: **Fig. 3 integrates the closed loop and shows both regimes numerically** — recovery with β > 0, irreversible elevation with β = 0. The pathology section now cites the demonstration (§3.4: "fibrosis centrally involves missing P5 — Eq. 1 with β = 0, demonstrated in Fig. 3(b)"). *(Location: Eq. 1, §3.2, Fig. 3, §3.4.)*

### R1-3. Start smaller: P3 + P5 only, in the smallest possible model.

**Done in Round 1; made explicit in Round 2.** Phase I's stated *first deliverable* is the closed loop of Eqs. 1–2 — factory, circulating pool, workload, receptor-mediated clearance, signal-driven production, responder lifetime, delay, relaxation — analysed before the full HS formalism. The programme introduction states the loop "is simulated as soon as it is written (Fig. 3)", and Fig. 3 is precisely the referee's minimal experiment: demand pulse → residual → production → population → recovery. *(Location: §4 intro, §4.1, Fig. 3.)*

### R1-4. Phase I and II should run iteratively, not formalisation-first.

**Done in Round 1.** §4 opens: "The phases are not a waterfall: the minimal loop is simulated as soon as it is written (Fig. 3), control analysis feeds revised models, sandbox anomalies feed back into theorems…" The delay-driven overshoot/oscillation question the referee anticipated is named "the recurring scientific object" of the whole programme and is Phase I's first theorem. *(Location: §4 intro, §4.1(i).)*

### R1-5. "Existence proof… scales from pinprick to major trauma" needs weakening; where is the operating boundary?

**Done in Round 1.** Abstract now says "existence proof over a substantial operating envelope"; §1 says overwhelming injury "does break it, a boundary the programme must map rather than assume away"; Phase V is titled "Failure theory and the operating boundary" and asks the referee's question verbatim in italics. Round 2 adds the phase-diagram deliverable (see N1-11). *(Location: Abstract, §1, §4.5.)*

### R1-6. P6 is conceptually different — separate as an architectural assumption.

**Done in Round 1.** §3.3 is retitled "Five primitives and one architectural assumption"; P6 became A1 ("cheap items, elastic factories"), with the referee's own open question stated: whether P1–P5 can coordinate expensive, heterogeneous or irreplaceable responders is tested in Phases II and V, not assumed. *(Location: §3.3, Table 1 column A1.)*

### R1-7. The O(nk) claim needs C_logical and C_substrate, or the coordinator is hidden in the medium.

**Done in Round 1; upgraded in Round 2** to the five-component vector (C_agent, C_medium, S_agent, S_medium, L) requested by Round-2 Referee 1 — see N1-6 below. The accounting explicitly charges a well-mixed broadcast's n deliveries to C_medium, and retains: "A coordinator hidden inside the medium is still a coordinator." *(Location: §4.1, §5.)*

### R1-8. Expand to factorial ablations with interaction terms.

**Done in Round 1.** Phase II runs single-principle knockouts plus a factorial design over P1–P5 with the interaction terms the referee listed: P3×P5 (integration without antagonist), P2-without-P4 (false activation), P1+P2 without damping, P4 without P2 sensitivity. Round 2 adds the fractional-replicate budget (see N2, Phase II). *(Location: §4.2.)*

### R1-9. "Roughly an order of magnitude" is arbitrary — predict directionally.

**Done in Round 1.** Prediction (iii) is now directional: FPR_P4 < FPR_no-P4, with the effect size preregistered once the noise/adversarial model is fixed. Round 2 extends the same treatment to prediction (i)'s exponent (see N1-7). *(Location: §4.2, prediction 3.)*

### R1-10. Phase III inverse design: extend the genotype and ask whether evolution rediscovers the motifs.

**Done in Round 1; elevated in Round 2.** The genotype extends beyond (Σ, R, θ) to medium parameters (λ, D, γ, β) and affinity/antagonist relationships; the audit asks whether search independently rediscovers co-stimulus gating, antagonist pairing and constitutive-and-consumed signalling. Round 2 makes rediscovery the programme's stated central evolutionary hypothesis with an information-restriction ladder (see N1-9). *(Location: §4.3.)*

### R1-11. Add a biology → abstraction → engineering validation table with falsification column.

**Done in Round 1.** Table 2 (tab:validation) has exactly those columns — Biology / Abstraction / Engineering / "Refuted if" — one row per primitive, with Phase-II prediction numbers in parentheses. *(Location: Table 2.)*

### R1-12. The "union covers everything except P3" claim needs external verification across named literatures.

**Done in Round 1 (hormone/endocrine line: Digital Hormone Model, artificial endocrine systems, AHS, all cited and tabulated) and substantially deepened in Round 2** with the referee-endorsed near-miss families — see N1-5 below, which quotes and answers this round's sharpened form of the same question. *(Location: §2.5, §2.6, Table 1.)*

### R1-programme-order. Minimal biological model → simulation → analysis → proofs → larger sandbox; your five phases re-ordered.

**Done in Round 1.** The referee's sequence is the paper's structure read at one level down: §3 = biological validation and minimal abstraction; Phase I now opens with the closed loop itself, simulated (Fig. 3) and then analysed; Phase II = the larger sandbox; Phases III–V unchanged in position. The non-waterfall paragraph makes the iteration explicit rather than leaving it implicit in the numbering. *(Location: §4 intro, §4.1.)*

### R1-bottom-line. State the deepest hypothesis as a single falsifiable proposition.

**Done in Round 1.** §3.2 closes the control-law discussion with it, in italics: "a distributed system can estimate unmet global demand without explicitly measuring global demand, because the residual of a consumed signal can itself encode the error." Round 2 adds its evolutionary twin in Phase III (see N1-9). *(Location: §3.2, §4.3.)*

---

## ROUND 1 — Referee 2

### R2-1. Venue mismatch (MNRAS template).

**Acknowledged; no content change.** The mnras class was a working-draft convenience inherited from this project's toolchain, not a submission choice. The submission target is a self-organising-systems venue family (SASO / ACSOS / DCOSS) or a control-/autonomic-computing journal, and the manuscript will be retempled for the chosen venue. Nothing in the content depends on the template.

### R2-2. Omitted prior art: Digital Hormone Model; artificial endocrine systems.

**Done in Round 1.** §2.5 now cites Shen et al. (2004) — "the closest precedent to our P1 and P2" — and Xu & Wang (2011) with the lattice-based AES line, plus Brinkschulte et al. (2008) for AHS. Table 1 carries all three rows, each checked specifically against P3: in these systems "the hormone is a score, computed and consumed by nodes to guide movement or assignment; no signal is constitutively produced and cleared by its own consumers, so no residual encodes unmet demand." *(Location: §2.5, Table 1 rows.)*

### R2-3. Engage Hellerstein et al. (2004) and control-theoretic autoscaling on integral control.

**Done in Round 1.** Hellerstein et al. is cited in §2.1 and, decisively, in §3.2's Engineering-principle paragraph: feedback control of computing systems already uses integral action; the distinction kept is where the error *lives* — "measured and integrated by a controller, or *being* the unconsumed remainder of a consumed signal, with the medium doing the computing." Round 2 adds the closest two descendants of that literature (back-pressure, antithetic integral feedback) as scored near-misses — see N1-5. *(Location: §2.1, §3.2, §2.6.)*

### R2-4. Receptor spoofing vs genome-fixed receptors deserves its own paragraph.

**Done in Round 1.** §3.3 devotes a paragraph ("One disanalogy must be respected from the start") to exactly this asymmetry: receptor identity is genome-fixed in biology; a software subscription set is dynamic data and can be spoofed; authentication and authorisation are load-bearing parts of the medium; P4's co-stimulus guards are the architectural mitigation; both are attacked in Phase V's spoofing chapter. *(Location: §3.3, §4.5.)*

### R2-5. Tension between the spatial PDE (Eq. 2) and the well-mixed ODE (Eq. 1).

**Done in Round 1.** Phase I distinguishes the two signal classes explicitly — local fields follow the PDE of Eq. 3; well-mixed systemic signals "serve supply loops: their medium is a circulating pool rather than a spatial field — TPO is whole-body — and their dynamics are the ODEs of Eqs. 1–2" — and notes the different physics and cost, which is also why the cost vector separates agent-side from medium-side accounting. *(Location: §4.1, first paragraph.)*

### R2-6. The Table-1 wound row is tautological — flag it.

**Done in Round 1.** The caption states: "The final row is definitional — an internal consistency check that the primitive set describes the reference system, not an empirical comparison." *(Location: Table 1 caption.)*

### R2-Phase I. Commit to a formal task class; name proof techniques.

**Done in Round 1.** Phase I commits to "deadline-constrained demand covering: a set of sites each requires r_i responders within time T of demand onset, under churn," and names the techniques: Lyapunov/contraction for stability, potential-function for the message bound, antagonist completeness for termination, an FLP-style impossibility boundary. *(Location: §4.1.)*

### R2-Phase II. Statistical methodology; name the prediction-(iv) baseline.

**Done in Round 1.** ≥ 30 seeds per cell, bootstrap 95% CIs, preregistered effect sizes; prediction (iv) names the Kubernetes-style orchestrated baseline. Round 2 adds the compute-budget/fractional-replicate statement (N2) and the perturbation battery (N1-8). *(Location: §4.2.)*

### R2-Phase III. Scope the search; make the audit concrete.

**Done in Round 1 (two target specifications; audit = automated checking against Phase-I preconditions plus inspection of which primitives evolved solutions use) and deepened in Round 2** (pilot search before the full genotype, quantified budget, audit elevated to the central hypothesis). See N1-9 and N2-Phase III. *(Location: §4.3.)*

### R2-Phase IV. Success criteria against existing practice.

**Done in Round 1 (parity with a Kubernetes horizontal autoscaler; within 10% of a centralised assigner at 10× fleet size) and strengthened in Round 2** (KEDA-style event-driven autoscaler added to the parity criterion; a pre-pilot medium audit now gates the pilots). See N2-Phase IV. *(Location: §4.4.)*

### R2-Phase V. Provisional numeric targets.

**Done in Round 1** (overshoot ≤ 50%, recovery within 10% in five production delays, zero runaway in 10⁴ node-hours) **and grounded in Round 2** against conventional autoscaling SLOs and error budgets (N2-Phase V). *(Location: §4.5.)*

### R2-cross-cutting. Kill criteria per phase; timeline/dependency structure.

**Done in Round 1; graded honestly in Round 2.** Every phase carries a kill criterion. The dependency structure is the non-waterfall paragraph plus explicit gates (Phase III's audit is defined against Phase I's theorems; Phase IV's pilots are gated by the medium audit). A wall-clock timeline and resourcing plan are deliberately out of scope for a programme paper and belong to the funded plan; Round 2 additionally grades criterion strength (N2-cross-phase). *(Location: §4 intro, per-phase criteria.)*

### R2-minor. Fig. 3 restates Eq. 1; merge into Fig. 2.

**Done in Round 1** — the old box-and-arrow figure was deleted and its content lives in Fig. 2's systemic-escalation lane. (Round 2 then requested a *new* Fig. 3 of a different kind — the numerical simulation — which is the current Fig. 3; see N2-2.1.) The abstract's O(nk) caveat ("conditional on a medium providing broadcast, locality and decay") and the TPO wording ("secreted constitutively, chiefly by the liver") were both adopted in Round 1. *(Location: Fig. 2, Abstract, §3.2.)*

---

## ROUND 2 — Referee 1

### N1-1. "The strongest feature is the scientific plan" — preserve the five-phase structure.

**Preserved.** The five phases, their order, and every kill criterion stand. All Round-2 changes are strengthenings inside that frame. We note the referee's scoring (falsifiability 9/10, failure analysis 9/10) and accept the two 7/10s — biological grounding and current novelty evidence — as exactly what this revision targets.

### N1-2. Eq. 1 is incomplete: consumption depends on responder population, production on residual, maturation on delay — the minimal closed loop should be Phase I's first deliverable.

**Done.** The manuscript now writes the closed loop as two coupled delayed ODEs (Eqs. 1–2): the control law u̇ = γr − β(u − u₀) with r = [p₀ − c(t)]₊, and the pool dynamics Ṅ = u(t−τ) − μN − w(t)N with clearance c = κN. Consumption now depends on the responder population, production on the residual, and maturation enters through the delay τ — the referee's coupling structure. Phase I states: "The phase's first deliverable is that closed loop itself… analysed before the full HS." The referee's fuller signal-side form (Ḣ = P_H − C(H,N) − λ_H H) is the exact model when signal dynamics are not fast; Eqs. 1–2 are its quasi-steady reduction, and the ratio anchoring (τ_prod/τ_signal ≈ 10–100) is precisely the separation that licenses the reduction — deriving conditions under which the reduction is valid (and what changes near it) is part of theorem (i). *(Location: Eqs. 1–2, §3.2, §4.1.)*

### N1-3. Distinguish "complete biological mechanism" from "deliberately reduced control motif."

**Done, in the referee's own terms.** §3.2: "Eq. 1 is a deliberately reduced control motif extracted from one component of the richer regulation described above — a model of the abstraction, not of the biology." *(Location: §3.2, after Eq. 2.)*

### N1-4. Do not claim each pathology is the failure of exactly one primitive.

**Done, adopting the referee's framing.** §3.4 now reads: "Each pathology illustrates the type of failure that arises when one or more of the corresponding control functions become inadequate — a diagnostic mapping, not a claim of single causation, these diseases being multicausal," with the four pathologies re-described using dominated-by / centrally-involves language. *(Location: §3.4.)*

### N1-5. P3 novelty needs a much deeper prior-art search (chemical reaction networks, antithetic feedback, population control, homeostatic control, back-pressure, queueing, token pools, distributed load regulation, reaction–diffusion, metabolic control).

**Done for the two nearest neighbours, with the referee's question answered verbatim.** Table 1 adds and scores two families: congestion control/back-pressure (Kelly et al. 1998) — P3 ∼, since queue backlog is a genuine demand residual but *measured state reported to a computed controller*, not a constitutive blind-broadcast signal consumed by its own responders; and antithetic integral feedback (Briat et al. 2016) — P3 ∼, since the unpaired remainder of annihilating species is an error signal *inside a single well*, not a coordination medium across a fleet. §2.6 now poses the referee's exact test — "has anyone built a system in which a constitutively generated quantity is removed in proportion to available service capacity, so that its unconsumed remainder functions directly as the distributed error signal driving capacity creation?" — answers "on the evidence assembled here, no," and restates the claim as the *combination* (residual control + receiver-defined semantics + spatial decaying medium + antagonists), which is what the programme tests. The remaining families on the referee's list map onto existing rows: population-control circuits and reaction–diffusion computation onto synthetic biology, amorphous computing and field-based coordination; distributed load regulation onto orchestration/autoscaling; token pools onto the congestion row; a full chemical-reaction-network and metabolic-control sweep is registered as part of the Phase III-adjacent literature audit rather than claimed as complete here. *(Location: §2.6, Table 1 rows, bibliography.)*

### N1-6. Make the complexity claim explicitly multidimensional: (C_agent, C_medium, S_agent, S_medium, L).

**Done, in exactly that notation.** §4.1 now defines the programme's cost statement as the five-component vector (C_agent, C_medium, S_agent, S_medium, L) — per-agent and medium communication, per-agent and medium state, latency (energy folded in at Phase IV's edge hardware) — with the broadcast's n deliveries charged to C_medium, and theorem (ii) honest only if every component is bounded. §5's first clarification is updated to match. *(Location: §4.1, §5.)*

### N1-7. Prediction 1's "fitted exponent exceeding 1.2" is arbitrary; derive it.

**Done.** The number is removed from the prediction. Prediction (i) is now directional plus procedural: "The numeric exponent threshold is derived, not chosen: Phase I fixes the expected scaling regime, and the threshold is preregistered before the definitive runs." *(Location: §4.2, prediction 1.)*

### N1-8. Add a sixth experimental category: perturbation and recovery.

**Done, with the referee's full battery.** Phase II adds a dedicated perturbation-and-recovery battery — step, impulse, ramp, periodic and stochastic demand; abrupt responder depletion and restoration; signal delay and loss; heterogeneous receptor thresholds — measuring rise time, settling time, overshoot, integrated error, oscillation amplitude, resource excess, communication cost and failure probability. *(Location: §4.2.)*

### N1-9. Make rediscovery a central hypothesis.

**Done, verbatim and in italics.** Phase III now states the programme's central evolutionary hypothesis: "deprived of global state but required to solve variable-demand resource allocation robustly, optimisation independently evolves residual-demand signalling" — run on a ladder of progressively stronger global-information restrictions so emergence can be attributed to the restriction, not the fitness function; convergence across specifications is described as evidence of convergent discovery by biological evolution and computational optimisation, and the existing kill criterion covers the informative negative. *(Location: §4.3.)*

### N1-10. Baselines must be exceptionally strong; same information and resource budget.

**Done.** Phase III now names five tiers — a centralised oracle and near-oracle; a conventional distributed controller; a state-of-the-art autoscaler (Kubernetes-style); the closest field/hormone systems (gossip membership, stigmergy-style field following); and our own ablated variants — all under identical workloads, information and resource budgets, with the explicit sentence "A comparison against handicapped baselines proves nothing." *(Location: §4.3.)*

### N1-11. Add phase diagrams to Phase V.

**Done, in the referee's axes.** Phase V now "delivers the boundary as phase diagrams: τ_production/τ_signal against peak demand over baseline capacity, regions classified stable → underdamped → oscillatory → runaway → collapse." *(Location: §4.5.)*

### N1-12. Fig. 2 overstates sequentiality — overlap the phases.

**Done.** The figure's phase washes now deliberately overlap (the drawn bands bleed into their neighbours), and the caption states why: "Phase bands are drawn overlapping, as in vivo: there is no master state machine declaring a phase boundary — transitions are population-dynamic." This now visually supports the architecture's own argument, as the referee noted it would. *(Location: Fig. 2 and caption; regenerated.)*

### N1-13. Elevate the decentralised-deciding distinction early.

**Done — moved to the Introduction.** §1, paragraph 2: "what is decentralised is *decision-making and knowledge*, not necessarily physical plant — factories may be centralised and media shared; the argument is against centralised *deciding*, not against shared infrastructure." §5 retains the marrow formulation. *(Location: §1, §5.)*

### N1-centrepiece. Organise around the rediscovery experiment under progressively stronger information restrictions.

**Adopted as the organising bet of Phase III** (hypothesis, restriction ladder, kill criterion, audit as "the programme's most impressive possible result"). We have kept it as the payload of Phase III rather than re-titling the paper around it, because the referee's own assessment scores the *programme* as the strongest feature and advises against restructuring; the rediscovery experiment is now unambiguous as its centrepiece within that structure.

---

## ROUND 2 — Referee 2

### N2-2.1. The paper reports zero original results — run a toy simulation of Eq. 1 showing stability and the β = 0 fibrosis mode; label the paper as a programme.

**Done on all three counts.** (i) New Fig. 3 integrates the closed loop through a demand pulse: panel (a), β > 0 — residual rises as the pool falls, production follows with delay-induced overshoot, both return to baseline; panel (b), β = 0 — production ratchets and never relaxes, the pool settles at ≈ 4× baseline: the fibrotic shift, demonstrated rather than predicted. Parameters are given in the caption for reproducibility, and the simulation script ships with the source (`make_figures.py`). (ii) §1 now states explicitly: "This is a research-programme paper: it reports one illustrative simulation of the central control law and a falsifiable plan, not completed experiments." (iii) The Conclusions accordingly claim the simulation, not the programme's predictions, as shown. *(Location: Fig. 3, §1, §3.2, §6.)*

### N2-2.2. Eq. 1's p(t) = p₀ + u(t) has the causality backwards.

**Correct — and fixed.** In the TPO/Mpl system the hormone's production is constitutive; what changes is clearance. The manuscript previously wrote p = p₀ + u, wiring marrow output into the signal flux. Eq. 1 now has the signal flux *constitutive and constant* (p₀); the residual is r = [p₀ − c(t)]₊ with clearance c = κN proportional to responder availability; and the loop closes through the responder pool (Eq. 2): depletion → clearance falls → residual rises → production rises. The text states the causality explicitly: "the loop closes through the responder pool, not through the signal." *(Location: Eqs. 1–2, §3.2.)*

### N2-2.3. Non-negativity of r is asserted, not enforced.

**Fixed in the equation and explained structurally.** The residual is now written r(t) = [p₀ − c(t)]₊ with [x]₊ = max(x, 0) in the equation itself, and the text adds why the max is physical rather than cosmetic: clearance is receptor-mediated and proportional to responder availability, so consumption cannot exceed what is circulating — "depletion, not instruction, raises the residual." *(Location: Eq. 1, §3.2.)*

### N2-2.4. Medzhitov citation splices two different papers.

**Fixed as prescribed.** The intended reference is Medzhitov's "Origin and physiological roles of inflammation," now correctly given as Nature, 454, 428 (2008). A full pass over the remaining 28 entries was run; the entries Round 2 verified (Kaushansky 2005, Gurtner et al. 2008, Manz & Boettcher 2014, Fischer et al. 1985, Burns et al. 2016, Basu et al. 2005, You et al. 2004, Shen et al. 2004) re-checked clean, and the two new entries (Briat et al. 2016, Cell Syst. 2, 15; Kelly et al. 1998, J. Oper. Res. Soc. 49, 237) are given in full. *(Location: bibliography.)*

### N2-2.5. Related work stops at 2016 — service meshes, KEDA, chaos engineering.

**Done.** §2.1 now names the post-2016 ecosystem and states the distinction that matters to the thesis: "refines this pipeline without changing its epistemics: the error signal is still measured and reported, never physical." Phase IV's parity criterion now names an event-driven autoscaler in the KEDA style alongside the Kubernetes HPA. *(Location: §2.1, §4.4.)*

### N2-Phase I. "Realistic production delay τ" is unanchored.

**Anchored in the reference biology.** Phase I now fixes the range from the literature the referee cites: hormone half-lives of order hours against platelet lifespans of 7–10 days and multi-day granulopoiesis give τ_production/τ_signal ≈ 10–100, "and the theorems must hold across that range." The same ratio is the axis of Phase V's phase diagrams, so the anchoring does double duty. *(Location: §4.1(i), §4.5.)*

### N2-Phase II. Factorial compute budget; justify the 1.2 exponent.

**Both done.** The design is now stated as a fractional replicate of the 2⁵ factorial ranked by Phase-I sensitivity, provisionally 10⁵ simulated node-hours per scenario class; the exponent threshold is removed from the prediction and replaced by the derive-then-preregister procedure (see N1-7). *(Location: §4.2.)*

### N2-Phase III. Quantify the budget; pilot the search before the full genotype; give the audit more space.

**Done.** Budget stated (provisionally 10⁶ evaluations per specification); a pilot — fixed topology, two or three loci free at a time — validates the fitness landscape before the extended genotype is released; and the audit paragraph has grown into the statement of the programme's central hypothesis with the restriction ladder (N1-9). *(Location: §4.3.)*

### N2-Phase IV. TTL windows vs the continuous PDE needs a validation step.

**Done — added as a gate before the pilots.** "Before either pilot, a medium audit connects Eq. 3 to the discrete substrate: emulation on a grid testbed measures the approximation error of TTL aggregation against the continuous field, and the pilots proceed only if that error is bounded — Phase I's guarantees must survive the discretisation they are deployed on." *(Location: §4.4.)*

### N2-Phase V. Numeric targets read as chosen; ground them in existing SLOs.

**Done.** The targets are now flagged as "aligned with conventional autoscaling SLOs and error budgets, to be tightened after Phase II," and the boundary is delivered as the phase diagrams above. *(Location: §4.5.)*

### N2-cross-phase. Kill criteria are softer at II–V than advertised.

**Acknowledged in the text.** The programme introduction now grades them: "The criteria are not equally sharp: Phase I's is terminal, while at Phases II–V a negative result more often forces a model revision than a full stop; we say which wherever a criterion is stated." *(Location: §4 intro.)*

### N2-minor. Table 1 symbol criteria; affiliation; "thousandth node"; family-count consistency.

(i) The Table 1 caption has carried the assignment rule since Round 1: "✓ = native; ∼ = partial or incidental; — = absent," with the wound row flagged definitional. (ii) Affiliation: BIODISC is an independent research laboratory, not an academic institution; a one-line context footnote will accompany the submission version, and we take the point about plausibility signals. (iii) The Discussion's closing line is now scoped "within the mapped operating envelope." (iv) Family count: now fourteen, consistent across Abstract, §1(iii), §2.6 and the Conclusions, matching Table 1's fourteen prior-art rows (the wound row is separate and flagged definitional). *(Location: Table 1 caption, §5, throughout.)*

### N2-recommendation. Toy simulation; Eq. 1 fix; Medzhitov fix; right journal template.

All four done or addressed above: Fig. 3 (simulation), Eqs. 1–2 (causality and saturation), the corrected reference, and the venue note in R2-1.

---

## ROUND 3 — Referee 1

*The author also lifted the page constraint for this round ("do not worry about the length"), which we have used to move analysis that was previously promised as Phase-I deliverables into the paper itself.*

### R3-1(R1). P3 novelty needs a deeper search and softer phrasing — "we have not identified", not "none exists".

**Done, both halves.** (i) The sweep was extended by two scored families in Table 1 — token-bucket/credit flow control (depletion semantics, but per flow, rate-policing, no capacity-creation loop) and metabolic/homeostatic regulation (end-product pools modulate production — the nearest conceptual cousin — but intracellularly, without a broadcast medium) — with one-line dispositions in §2.6 for the further families checked in text: chemical-reaction-network control, demand-driven autoscaling, swarm resource recruitment, and availability-signal load balancing. (ii) The claim is now stated exactly as requested: "We have not identified such an architecture; the claim is stated as assembled evidence, not proven absence." (iii) A search-methodology sentence makes the coverage auditable: families were assembled from the survey literature cited in §2 and snowballed through their taxonomies, each candidate scored against the P1–P5 definitions by the criteria in the Table 1 caption. The count is sixteen everywhere (Abstract, §1(iii), §2.6, Conclusions). *(Location: Table 1, §2.6, Abstract, §1, Conclusions.)*

### R3-2(R1). The biology is presented too cleanly; the "reduced motif" caveat must be prominent; drop "evolution has already debugged".

**Done.** (i) "Already debugged" is gone: the introduction now reads "an engineering specification that evolution has stress-tested — robust across a substantial envelope, though neither optimal nor pathology-free." (ii) TPO is explicitly "not a purely passive residual detector" (hepatic output is modulated by further cues), and emergency granulopoiesis is "not merely 'G-CSF doing the same' — it layers additional regulation on the G-CSF axis." (iii) The disclaimer is now a displayed italic sentence immediately after Eqs. (1)–(2): "*We are not claiming that Eqs. (1)–(2) model wound healing.* They are a deliberately reduced control motif extracted from one component of the richer regulation described above." *(Location: §1, §3.2.)*

### R3-3(R1). Eq. (1) needs a real dynamical-systems analysis — equilibria, linearisation, delay stability, bifurcation — before Phase II; one simulation is not sufficient.

**Done — and moved into the paper rather than deferred.** A new *Stability* block in §3.2 delivers: (a) the closed-form equilibria of the full closed loop under constant demand, both branches (Eq. 3): inactive residual when κu₀/μ ≥ p₀, otherwise N\* = (γp₀ + βu₀)/(γκ + βm) with r\* > 0 and u\* = mN\*, m = μ + w — sustained demand holds the pool just below baseline with the residual permanently elevated; (b) linearisation of the active branch to the characteristic equation (λ+β)(λ+m) + γκe^(−λτ) = 0 (Eq. 4); (c) Routh–Hurwitz at τ = 0: unconditionally stable; (d) the delay result: putting λ = iω and eliminating the phase gives (γκ)² = (ω² − βm)² + (β+m)²ω², whose minimum over ω is (βm)² at ω = 0 — so a Hopf crossing exists **if and only if γκ > β(μ+w)**: below that threshold the loop is stable at *every* delay; above it a boundary τ_H appears. Oscillation is excessive loop gain relative to the antagonist, which delay exposes and antagonist size prevents; (e) the inactive branch is linear with roots {−β, −μ}; (f) Fig. 3's parameters are located on this map (just above threshold, τ below τ_H — hence the damped overshoot in panel (a)). Phase I now commits to completing this into a phase diagram over (βτ, γκ/β(μ+w)) and extending it to finite production capacity, Michaelis–Menten clearance saturation, noisy and delayed residual measurement, and heterogeneous responders — exactly the referee's list. *(Location: §3.2 Stability block, Eqs. 3–4, Phase I (i).)*

### R3-4(R1). The five-component vector should replace O(nk) as the primary claim in the abstract and introduction.

**Done.** The abstract's question now reads "…with coordination cost carried by an explicit five-component vector (agent and medium communication, agent and medium state, latency; the agent-side component O(nk)…)"; the introduction's economic-premise paragraph and contribution (i) make the vector primary with O(nk) explicitly demoted to the agent-communication component; the Discussion was already vector-first. *(Location: Abstract, §1 premise, §1 contribution (i).)*

### R3-5(R1). Phase II's decisive comparison must be broader than P3-removal: conventional measured-error feedback, queue/back-pressure, gossip load-balancing, central oracle, at equivalent information and resources.

**Done.** Phase II now runs six arms — full P1–P5; P3 removed; ordinary measured-error integral feedback granted identical information; queue/back-pressure control; decentralised gossip load-balancing; and a central oracle — "answering whether residual signalling merely works, or confers an identifiable advantage over conventional feedback at equal information and resources." *(Location: §4 Phase II.)*

### R3-phases(R1). Phase I as a standalone-theory trajectory (βτ vs γκ phase diagram); Phase III fully blinded; Phase IV resource equivalence; Phase V as an envelope function.

**All done.** Phase I: the phase diagram is committed with the referee's axes, on top of the analysis now in §3.2 (see R3-3). Phase III: "The search is also blind: the genotype carries no signal semantics, the fitness function never names primitives, and evolved architectures are classified only after the runs complete — so rediscovery is convergent evidence, not scaffolding." Phase IV: pilot (a)'s criterion now includes "under identical replica counts, network allocation and response capacity for both sides." Phase V: the deliverable is now an operating-envelope map, F(demand, τ, noise, churn, capacity, attack rate, medium availability) → {stable, underdamped, oscillatory, runaway, collapse} (Eq. 7), summarised as phase diagrams including βτ vs γκ/β(μ+w). *(Locations: Phases I, III, IV, V.)*

### R3-structure(R1). Split into three independently falsifiable hypotheses.

**Adopted verbatim.** A hypotheses block now opens §4: H1 mechanistic (residual consumption sufficient to estimate unmet demand; Phases I–II, prediction 1), H2 architectural (P1–P5 jointly produce robust coordinator-free covering no subset reproduces; Phase II factorial, predictions 1–3), H3 comparative (better cost/robustness frontier than conventional alternatives at equal budgets; Phases III–IV, prediction 4) — each prediction is tagged (H1)/(H2)/(H3) in the list. The abstract and Conclusions name the three. *(Location: §4 opening, predictions list, Abstract, Conclusions.)*

## ROUND 3 — Referee 2

### R3-1(R2). Venue/template mismatch.

**Acknowledged, unchanged in kind.** The MNRAS class remains the working draft's convenience; the venue will be chosen before submission and the paper re-templated then (the content is template-independent, as this round's changes illustrate). The intended track is now stated in the paper itself (see R3-2(R2)).

### R3-2(R2). Target a Perspective/Vision or Registered Report (Stage 1) track explicitly.

**Done.** §1 now ends its programme-paper statement with: "The predictions, effect sizes and kill criteria are written to be registrable: a Perspective or Stage-1 registered-report track is the intended submission form." *(Location: §1, contributions paragraph.)*

### R3-3(R2). No resourcing/feasibility discussion; justify the 10⁵ and 10⁶ figures.

**Done — new subsection "Feasibility and resourcing" closing §4.** A small-team, roughly three-year sizing: Phase I is analyst work plus laptop-scale numerics (~10³ core-hours). Phase II's 10⁵ node-hours are derived from the design: ≥ 30 seeds per cell resolves standardised effects d ≳ 0.7 at 95% confidence with bootstrap intervals (the standard two-sample power calculation), covering the fractional factorial, the perturbation battery and the six-arm comparison across three topologies. Phase III's 10⁶ evaluations run in weeks on a 64-core node once the pilot validates the landscape; Phase IV needs two engineers and existing clusters; Phase V is analyst and red-team time. Every budget is provisional, gated by the preceding pilot, and allocated by the computed Sobol ranking — "a funding panel can audit each number back to a design choice rather than a guess." *(Location: §4, Feasibility and resourcing.)*

### R3-4(R2). Name the closest control-theoretic relative explicitly: leaky/anti-windup integral control on a saturating non-negative error with a delayed plant.

**Done.** The Engineering-principle paragraph now opens: "In control-theoretic terms, Eq. (1) is a leaky integral controller with anti-windup, acting on a non-negative, saturating error through a delayed plant (Åström & Murray 2008) — a known object, and we claim no novelty for the law itself. The novelty is where the error physically resides." The reference is added (30 entries). *(Location: §3.2, bibliography.)*

### R3-5(R2). The medium is treated as a black box — partition, degradation, delivery semantics.

**Done — new paragraph in Phase IV.** Under partition, concentration fields decay in place and staleness is self-announcing: a decaying signal reads as *less* demand, so a partitioned region under-responds rather than mis-responds, with local baseline capability carrying the interval. Concentration semantics relax delivery requirements: aggregation is commutative and idempotent, so at-least-once delivery with per-key TTL suffices, ordering is irrelevant, and exactly-once semantics are not needed. Sustained medium loss remains fatal to escalation — hence medium availability and partition behaviour are axes of the Phase V boundary, and both pilots carry an injected 30-second medium-partition ride-through criterion (no erroneous action; graceful decay; recovery without thrash). *(Location: §4 Phase IV, pilots (a) and (b).)*

### R3-6(R2). Security is a promissory note even for a programme paper.

**Strengthened.** The spoofing paragraph in §3.3 now specifies the layered mitigation: authenticated emission and key-scoped receptors fix identity (the analogue of genotype-fixed binding); P2's saturation doubles as an innate rate limit, bounding flood effect; P4 requires a second, locally verifiable co-signal, so a spoofed systemic signal alone cannot trigger effector action; and receptor-level anomaly thresholds bound what a valid-but-malicious insider can recruit — the sepsis analogue, attacked deliberately in Phase V precisely because valid keys defeat authentication alone. *(Location: §3.3, Phase V.)*

### R3-7(R2). Soften the completeness claim or state the search methodology.

**Done — see R3-1(R1)**; the softened claim and the auditable methodology sentence were added together.

### R3-phases(R2). Quantitative "stable" (Phase I); justify 10⁵ (Phase II); operationalise the oracle and equal budgets (Phase III); partition criteria in the pilots (Phase IV); why 50% overshoot (Phase V); a cross-phase decision table.

**All done.** Phase I's kill criterion now defines stability quantitatively: asymptotic stability of Eq. (4)'s roots across the anchored delay range with overshoot ≤ 50% and settling within five production delays — the same bounds Phase V enforces ("a tolerance, not a vibe"). Phase II: the 10⁵ figure is derived in Feasibility and resourcing, and the fractional replicate's ranking procedure is now named (first-order Sobol indices from the Phase I linearisation). Phase III: the oracle is operationalised as "an implementation convenience, not an architecture — a centralised scheduler granted simulated direct access to global state at equal compute and message budget, an upper bound on what any coordinator could achieve," with the near-oracle adding measurement latency, and budgets policed explicitly. Phase IV: both pilots carry the medium-partition criterion. Phase V: the 50% bound is "matched to typical autoscaler error budgets, and revisited against Phase II data." The cross-phase decision table is new (Table 3): each phase's kill outcome mapped to its response — terminate (I), H1 fails (II), claim narrows from "inevitable" to "useful" (III), H3 fails for open fleets (IV), claims scoped to the mapped envelope (V) — "so the falsifiability claims can be audited rather than admired." *(Locations: Phases I–V, Table 3.)*

### R3-minor(R2). Affiliation context; funding/AI disclosure; citation accuracy; kerning artifacts.

(i) The Acknowledgements now carry both: "Developed within the BIODISC (Biology Discovery and Intelligence System) environment, an independent research laboratory. Analysis and drafting were assisted by AI research tooling (Claude, Anthropic); the programme, its judgements and its claims are the author's." Venue-specific disclosure forms will be completed at submission. (ii) All thirty citations were re-verified against source records this round. (iii) The apparent kerning artifacts are pdftotext ligature-extraction artifacts, not typographic defects; the compiled PDF will be proofed page-by-page at submission.

---

## Remaining limitations, stated honestly

- The paper remains a programme paper; the equilibrium/stability analysis and one illustrative simulation are now included, but every Phase II–V claim is still prospective by design.
- The prior-art sweep is deeper, and its methodology is now stated so coverage is auditable, but it is not exhaustive; the registered families (chemical-reaction-network control, demand-driven autoscaling, swarm resource recruitment, availability-signal load balancing) are disposed of in text rather than scored in Table 1.
- The stability analysis covers the active and inactive branches of the linearisation; the kink of the residual's [·]₊ at the baseline equilibrium is handled by one-sided analysis, and the full nonsmooth treatment (Filippov/monotone-system arguments) is Phase-I work.
- Resourcing figures are derived from design choices and standard power calculations but remain provisional until pilots run.
- Page count: the original draft was commissioned at five pages; Round 1 took it to six, Round 2 to eight, and Round 3 — with the author's explicit release of the page constraint — to nine. The additions are separable if a venue limit demands it.

---

# ROUND 4

**Manuscript title changed this round:** *Coordination Without a Coordinator: A Scientific Programme for Hormone-Inspired Residual-Demand Signalling* (short title unchanged). The paper now compiles at 11 pages, 32 references, with a new Appendix A; every change below is in place and the source compiles clean (0 overfull boxes, 0 undefined references).

## Referee A

### R4-A1. The inactive-branch equilibrium is wrong: under constant w it should be u₀/(μ+w), not u₀/μ; recheck the entire derivation including the Hopf threshold.

**Correct — fixed, and you were right to call it the first thing to fix.** The inactive branch under constant demand w now reads (u*, N*) = (u₀, u₀/m) with m = μ + w, active when κu₀/m ≥ p₀, with the explicit clause "at zero demand m = μ and this is the baseline u₀/μ." The old condition κu₀/μ ≥ p₀ wrongly admitted residual-active cases. We verified the correction numerically before editing: with μ = 1, w = 0.5, u₀ = 1, the system settles at N = 0.667 = u₀/m, not at 1.0 = u₀/μ. **The full derivation was then rechecked as requested:** the active-branch equilibrium (Eq. 3) was already stated in m and is unchanged; the characteristic equation (Eq. 4), the τ = 0 result, and the Hopf threshold γκ > β(μ+w) are branch-independent and unchanged — consistent with Referee B's independent re-derivation confirming Eqs. 3–4. Two further consequences of the recheck are now in the text: the inactive branch's linear roots are corrected to {−β, −m} (was {−β, −μ}), and the equilibrium is enriched with the exact bounds — N* exceeds the fixed-production ceiling u₀/m exactly when the residual is active, and undercuts the zero-demand baseline u₀/μ whenever μp₀ < κu₀ — which is precisely the divergence that powers the reworked Prediction 1 (see R4-A6). *(Location: §3.2, Stability paragraph.)*

### R4-A2. "At steady state r → 0 — supply tracks demand" contradicts r* > 0 on the active branch; reword.

**Fixed as suggested.** The control-law paragraph now reads: "At steady state the residual settles at exactly the level that sustains the production the workload requires (r* > 0 under sustained demand; r → 0 only when demand vanishes) — supply tracks demand in the sense of matching it, not of zeroing the error." *(Location: §3.2, Control law paragraph.)*

### R4-A3. The TPO material must remain an abstraction; only a minimal biological claim is needed.

**Done.** Immediately after the italic disclaimer ("a model of the abstraction, not of the biology") the paper now states the retained claim in minimal form: "The biological claim retained is deliberately minimal: responder-dependent clearance of a constitutively supplied signal can encode information about responder availability. Nothing about physiological equivalence, organ roles or set-points is claimed, and none is needed for the engineering argument." *(Location: §3.2, after the disclaimer.)*

### R4-A4. P3's novelty needs a falsification-directed search across CRN/antithetic/metabolic/queueing/back-pressure/congestion/token/homeostatic/swarm-recruitment/reaction-diffusion/AES/autoscaling threads, with the methodology documented.

**Done — new Appendix A ("Search methodology for the gap analysis").** It records: sources (Google Scholar, ACM DL, IEEE Xplore, arXiv cs.MA/cs.DC/eess.SY, PubMed); the eight query families; the dates (original survey 2026-07, currency re-sweep 2026-08-15); inclusion criteria; the per-primitive scoring rubric (P3 native only when a constitutively produced quantity is cleared in proportion to available responding capacity and its residual drives capacity creation); the per-thread dispositions for the post-2016 threads; and the statement that the P1–P5 definitions were fixed before scoring. §2.6 now points to the appendix and states the falsification-directed intent explicitly: the goal was to find an architecture that implements P3 natively and thereby falsify the gap before publication. *(Location: §2.6, Appendix A.)*

### R4-A5. Phase I is the gatekeeper; add parameter identifiability/sensitivity, and note that the strongest result is a large stable volume retained under parameter uncertainty, not fine-tuned parameters.

**Done — new paragraph in Phase I.** The deliverable is now "a volume, not a tuned point": the fraction of the anchored parameter box that is asymptotically stable under the quantitative bounds, and how much of that volume survives a simultaneous ±20% error in every parameter — with Sobol indices naming which parameters the envelope is most sensitive to and which are safe to leave unidentified. The paper states your argument nearly verbatim: "A mechanism that needs four parameters tuned to a few per cent is not a candidate for robust distributed computing, so the strongest possible Phase I result is a large stable volume — majority, not sliver — retained under parameter uncertainty." *(Location: §4 Phase I, after the theorem list.)*

### R4-A6. Don't hang H1 on a scaling exponent alone; the six-arm outcome vector should be the principal comparison.

**Done — Prediction 1 rewritten.** The prediction now leads with the preregistered outcome vector (recovery time, integrated error, overshoot, resource excess, communication cost, failure probability) across the six arms at matched information and budget, "with the scaling exponent below one derived component of it, not the whole test." The exponent itself is now derived rather than asserted: without P3 production is fixed and the pool is capped at u₀/m, so T = −(1/m)ln[(u₀/m − N_T)/(u₀/m − N₀)] grows superlinearly and diverges as the burst requirement N_T approaches that ceiling — using exactly the corrected equilibrium bounds of R4-A1 — while the full model's demand-tracking production keeps T near-linear. Phase I derives the divergence point and near-ceiling form; the threshold is preregistered before the definitive runs. The Phase II criterion is correspondingly recast: termination fires if the full model loses to conventional feedback on the preregistered vector at matched information and budget — no penalty for removing P3, no advantage to keeping it — not merely on the exponent. *(Location: §4 Phase II, prediction 1 and termination criterion.)*

### R4-A7. Phase III must be genuinely blind: freeze genotype/fitness/information/budget/P3-like criteria/classification beforehand, and classify without knowing the condition.

**Done.** The blindness is now frozen in advance and dated: "the genotype, the fitness function, the information budget, the criteria for judging a loop P3-like, and the classification procedure are all fixed and dated before the first run of the released genotype," and classification is performed on de-identified architectures "with condition labels unblinded after every solution is classified." The search-space dimensionality is also stated (order 10² dimensions: eight signal loci with emission, response and threshold genes, four medium parameters, an 8×8 affinity/antagonist matrix), which motivates the correlation-length pilot. *(Location: §4 Phase III.)*

### R4-A8. The cost vector should be even more prominent in the abstract; the hidden-coordinator criticism is answered by Phase IV being designed to decide it.

**Done.** The abstract now closes with: "The medium is not free, and whether the coordinator has merely been hidden inside it is a criterion the programme itself tests, not an assumption" — with the criteria two-tier wording (below) also added so the abstract states what kind of criterion it is. Phase IV's criterion is now labelled claim-reduction and says the renaming-of-the-coordinator outcome explicitly: "H3 fails for open fleets, and the claim is scoped to closed fleets rather than abandoned." *(Location: Abstract; §4 Phase IV.)*

### R4-A9. Phase V's envelope should be the primary deliverable, with a region-dominance conclusion: dominates in X, comparable in Y, fails in Z.

**Done.** Phase V now names the region statement as the headline deliverable: the envelope map says where the architecture *dominates* (high churn and coordinator-targeted denial — medium cost amortised, coordinator attackable), where it is merely *comparable* (benign steady loads), and where it *fails* (sustained partition and extreme latency — the medium is the bottleneck). The Conclusions echo this: "The programme's terminal output is a dominance map — where hormonal coordination wins, where it ties, and where it should not be used." *(Location: §4 Phase V; Conclusions.)*

### R4-A10. Kill-criteria terminology should distinguish termination from claim reduction; separate the scientific and architectural novelties; Phase III's binding costs are design/implementation/debugging/validation; reconsider the title; venue.

**All done.** (i) Terminology: §4's introduction now defines the two kinds — *termination criteria* (Phase I's stability gate and Phase II's prediction 1, both kill H1) and *claim-reduction criteria* (III: "inevitable" → "useful"; IV: open fleets → closed fleets; V: universal → mapped envelope) — every criterion is relabelled accordingly, Table 3's caption uses the same terms, and the abstract says "a termination criterion for the core mechanism, claim-reducing criteria elsewhere." The decision table's content was already consistent; the prose now agrees with it. (ii) Two novelties: the hypotheses block now separates the *scientific* claim (residual-demand signalling is a stable, discoverable control mechanism — H1, H2) from the *architectural* claim (competitive on real substrates — H3), stating that "H1 can succeed while H3 fails, and the result would still be interesting: a validated, biology-derived control law that conventional infrastructure happens to beat on its own turf is a finding about the biology of control, not a failure of the science"; the Conclusions carry the same separation. (iii) Feasibility now states: "The compute figures are initial budgets, and compute is not the binding constraint: Phase III's expensive parts are design, implementation, artefact recognition and validation — building the simulator, the blinding protocol and the classifier, redesigning fitness after the pilot, auditing evolved solutions for hidden global state — which are engineer-months, not core-hours." (iv) Title changed to *Coordination Without a Coordinator: A Scientific Programme for Hormone-Inspired Residual-Demand Signalling* — the mechanism the paper is about now names itself in the title; short title unchanged. (v) Venue: see the joint response to Referee B's first point below.

## Referee B

### R4-B1. Venue mismatch: MNRAS is the wrong scope; candidates include Royal Society Interface, Artificial Life, Swarm Intelligence, ACM TAAS/TOSN, IEEE TPDS, arXiv cs.MA/cs.DC.

**Accepted — a letter-level response for now, actioned at submission.** The MNRAS class file is a working-draft convenience only; nothing in the paper's content is astronomical and we will not bolt astronomy on to make it fit. The intended sequence is: arXiv cs.MA/cs.DC posting first, then J. R. Soc. Interface as the primary target (the biology-to-engineering transfer framing and the wound-healing reference system fit its scope), with Artificial Life and ACM TAAS as alternates depending on how Phase-adjacent the final framing reads. The manuscript will be re-templated to the chosen venue's class, and the AI-disclosure statement will be moved to match that venue's format. *(No change to the working draft's class file; noted here as a commitment.)*

### R4-B2. Literature currency: newest citation is 2016, most from 2000–2011; extend to the 2017–2025 threads.

**Done.** Two new post-2016 references, both load-bearing rather than decorative: Aoki et al. (2019, Nature 570, 533) — the antithetic integral feedback controller realised experimentally in living and cell-free systems, cited in §2.6 to sharpen the antithetic row's disposition ("a residue-as-error implementation that remains within a single controlled volume"); and Hunt, Jones & Hauert (2019, R. Soc. Open Sci. 6, 190225) — the limits of pheromone stigmergy tested at high swarm density, cited in §2.3 ("the limits of that repertoire are now measured directly, not merely asserted"). §2.6 additionally records the currency re-sweep over the post-2016 threads (event-driven autoscaling in the KEDA style, digital-pheromone swarm robotics, endocrine multi-robot control, the post-Briat antithetic line), and Appendix A documents the per-thread dispositions. One honest note, recorded in the appendix: the KEDA-style thread's canonical sources are project documentation and vendor literature; peer-reviewed evaluations were scarce as of the sweep — stated as a finding about the thread rather than papered over. The bibliography moves from 30 to 32 entries; the pre-2016 core is retained because those are the family-defining works the table scores. *(Location: §2.3, §2.6, Appendix A, bibliography.)*

### R4-B3. Primitive-derivation circularity: a single author defined and scored the primitives; wants a second scorer or documented pre-registration plus reproducible extraction methodology.

**Done — both.** Appendix A now records the reproducible methodology (sources, queries, dates, inclusion criteria, per-primitive scoring rubric, per-thread dispositions) and states that the P1–P5 definitions were frozen before any family was scored. The second-scorer commitment is explicit: "Before submission, an independent second scorer rescores every family against the same frozen definitions; disagreements are resolved by documented discussion, and both scorings will be published with the paper." The frozen definitions, query list and rubric are preregistered with the Phase I–II registration. §2.6 carries both the appendix pointer and the second-pass commitment inline. *(Location: §2.6, Appendix A.)*

### R4-B4. Technical checks: Eq. 3, Eq. 4, τ = 0 stability, and the Hopf threshold with its monotonicity argument all confirmed correct.

**Acknowledged with thanks.** Your independent re-derivation is what localised the remaining defect to the inactive branch (your notational point below, and Referee A's first point): the active-branch equilibrium, the characteristic equation, and the Hopf threshold were all already in m and stand unchanged. The corrected inactive branch and the corrected roots {−β, −m} are now verified both analytically and numerically in the revised text.

### R4-B5. Notational: "γκ = 1.5, βμ = 1" is ambiguous once m is defined; the inactive branch's μ should be m (or scoped to baseline).

**Fixed, both instances.** (i) The Fig. 3 threshold sentence now reads against both branches explicitly: at baseline (w = 0, m = μ) the loop sits just above threshold (γκ = 1.5 > βm = 1) at a delay below τ_H — hence panel (a)'s damped overshoot — while during the pulse (w = 2, m = 3) the inequality reverses (βm = 3 > γκ = 1.5) and the loop is below threshold at every delay; the text adds the reading: "demand raises the per-capita loss that stabilises the loop, making it hardest to destabilise exactly when it is working hardest." (ii) The inactive branch is corrected to (u₀, u₀/m) with the zero-demand clause — see R4-A1 — and its linearisation roots to {−β, −m}. *(Location: §3.2, Stability paragraph.)*

### R4-B6. Minor points: prediction-1's provisional functional form; Phase III budget dimensionality; placeholder metadata/ORCID; AI disclosure; Fig. 3 label overlap.

(i) Prediction 1 now carries the derived functional form (see R4-A6): T = −(1/m)ln[(u₀/m − N_T)/(u₀/m − N₀)], diverging as N_T → u₀/m. (ii) Phase III's search-space dimensionality is now stated: order 10² dimensions, itemised, motivating the correlation-length pilot. (iii) Author metadata and ORCID are placeholder-dependent in the working draft and will be completed at submission. (iv) The AI-disclosure acknowledgement stays and will be reformatted per venue (see R4-B1). (v) The Fig. 3 label overlap was real, not an extraction artifact: in panel (b) the dashed u curve crosses y ≈ 3.05 at t ≈ 7.4 and passes through the second line of the annotation. Both panels' notes are moved to the open region right of the pulse (x > 11), the annotation text rewrapped, and the figure regenerated; the new layout is verified collision-free against the plotted curves in both panels.

---

## Remaining limitations, stated honestly (updated for Round 4)

- The paper remains a programme paper; the equilibrium/stability analysis, one illustrative simulation, and the derived prediction-1 divergence form are included, but every Phase II–V claim is still prospective by design.
- The prior-art sweep is documented (Appendix A) and its definitions frozen before scoring, but the independent second scoring is a pre-submission commitment, not yet performed; the KEDA-style autoscaling thread lacks peer-reviewed evaluations as of the sweep, so its disposition rests on primary documentation.
- The stability analysis covers both branches of the linearisation; the kink of the residual's [·]₊ at the baseline equilibrium is handled by one-sided analysis, and the full nonsmooth treatment (Filippov/monotone-system arguments) remains Phase-I work.
- Resourcing figures are derived from design choices and standard power calculations, and the compute figures are now labelled initial budgets with the binding engineer-months costs named, but all remain provisional until pilots run.
- The venue is unresolved pending submission (MNRAS is a working-draft convenience); the title was changed this round and the short title retained.
- Page count: commissioned at five; Round 1 → six, Round 2 → eight, Round 3 (length limit lifted) → nine, Round 4 (Appendix A + robustness/blinding/region-statement paragraphs) → eleven. The additions remain separable if a venue limit demands it.
