# Ecological and Routing Mathematics

## Purpose

This document defines the mathematical vocabulary for Sidetrack and OVON. It separates quantities that must not be conflated:

- ecological presence;
- conditional detectability;
- encounter probability;
- model uncertainty;
- observation coverage;
- route utility;
- user preference;
- scientific information.

Early implementations may use heuristics, but the interfaces should preserve these distinctions.

---

# 1. Spatial and temporal domain

Let the environment be represented by:

- a routing graph \(G=(V,E)\);
- candidate observation locations \(C \subseteq V\);
- route segments \(e \in E\);
- taxon set \(S\);
- time \(t\);
- observer profile \(o\);
- observation duration \(\tau\).

A route is an ordered path:

\[
R = (v_0,e_1,v_1,\ldots,e_k,v_k).
\]

A loop satisfies \(v_k=v_0\).

---

# 2. Ecological state and observation process

## 2.1 Relative ecological presence

For species \(s\), location \(x\), and time \(t\):

\[
\psi_s(x,t) \in [0,1]
\]

represents ecological presence or suitability. It is not automatically occupancy in the formal repeated-detection sense.

A provisional habitat model may use:

\[
\operatorname{logit}\psi_s(x,t)
=
\alpha_s
+
f_s(h(x))
+
g_s(x)
+
q_s(t),
\]

where:

- \(h(x)\) is environmental context;
- \(g_s(x)\) is a spatial term;
- \(q_s(t)\) is seasonality.

## 2.2 Conditional detectability

Given presence:

\[
p_s^{det}(x,t,o,\tau,m)
=
P(\text{detected}\mid\text{present},x,t,o,\tau,m),
\]

where \(m\) is protocol or travel mode.

A simple duration curve:

\[
p_s^{det}(\tau)
=
1-\exp(-r_s \tau).
\]

A richer model may include observer, habitat, time of day, sound, and protocol.

## 2.3 Encounter probability

\[
p_s^{enc}(x,t,o,\tau,m)
=
\psi_s(x,t)
p_s^{det}(x,t,o,\tau,m).
\]

Do not put \(\psi\) inside the detectability function and multiply by \(\psi\) again.

## 2.4 Complete-checklist likelihood

For a complete checklist event \(j\):

\[
Y_{s,j}
\sim
\operatorname{Bernoulli}
\left(
p_s^{enc}(x_j,t_j,o_j,\tau_j,m_j)
\right).
\]

An absent species can be zero-filled only when the checklist is validated as complete.

## 2.5 Presence-only likelihood

Presence-only sources require a separate observation process. One conceptual form:

\[
\lambda_{s,p}(x,t)
=
\exp\{
\eta_s(x,t)+b_p(x,t)
\},
\]

where \(\eta_s\) is latent ecological intensity and \(b_p\) is source/platform sampling bias.

Presence-only records do not create non-detections.

---

# 3. Species opportunity along a route

## 3.1 Edge intensity

Let \(\lambda_s(x,t,o,m)\) be an incidental encounter intensity per unit travel time along a route.

For segment \(e\):

\[
\Lambda_{s,e}
=
\int_e
\lambda_s(x,t,o,m)\,d\tau.
\]

## 3.2 Stop intensity

At stop \(i\) with duration \(\tau_i\):

\[
\Lambda_{s,i}^{stop}
=
-\log\left(
1-p_s^{enc}(x_i,t_i,o,\tau_i,m_i)
\right).
\]

## 3.3 Route-level encounter

Assuming conditional independence as an approximation:

\[
P_s(R)
=
1-\exp\left[
-\sum_{e\in R}\Lambda_{s,e}
-\sum_{i\in stops(R)}\Lambda_{s,i}^{stop}
\right].
\]

A product form is equivalent:

\[
P_s(R)
=
1-
\prod_{a\in R}
(1-p_{s,a}).
\]

Correlation between adjacent segments should eventually be handled through effective exposure or redundancy rather than naive independence.

---

# 4. Coverage and redundancy

## 4.1 Cyclic time distance

For annual weeks \(t,u \in \{1,\ldots,52\}\):

\[
d_T(t,u)
=
\min(|t-u|,52-|t-u|).
\]

## 4.2 Environmental kernel

With standardized environmental vectors \(z_i,z_j\):

\[
k_H(i,j)
=
\exp\left(
-\frac{
(z_i-z_j)^\top W (z_i-z_j)
}{
2\ell_H^2
}
\right).
\]

If \(W=I\), this is standardized Euclidean distance, not a full Mahalanobis distance.

## 4.3 Space-time-environment kernel

\[
k(i,j)
=
\exp\left(-\frac{d_S(i,j)^2}{2\ell_S^2}\right)
k_H(i,j)
\exp\left(-\frac{d_T(t_i,t_j)^2}{2\ell_T^2}\right).
\]

## 4.4 Species-specific complete-checklist coverage

\[
C_s(i,t)
=
1-\exp\left[
-\kappa
\sum_{j\in D_s^{complete}}
w_j k(i,j)
\right].
\]

Weights may account for:

- duration;
- protocol;
- independent observer;
- recency;
- validation.

Presence-only occurrence density should be stored separately and not automatically treated as complete-checklist coverage.

## 4.5 Route redundancy

A pairwise penalty:

\[
R(A)
=
\frac{2}{|A|(|A|-1)}
\sum_{i<j}k(i,j).
\]

A facility-location coverage objective may be more stable:

\[
F(A)
=
\sum_{g\in \mathcal G}
w_g \max_{a\in A} s(a,g),
\]

where \(\mathcal G\) is a set of spatial, habitat, temporal, or species targets.

---

# 5. Uncertainty

## 5.1 Predictive entropy

For probability \(p\):

\[
H(p)
=
-p\log p -(1-p)\log(1-p).
\]

Entropy is highest near 0.5 but does not distinguish model disagreement from irreducible uncertainty.

## 5.2 Query by committee

Given model predictions \(p_b\):

\[
QBC
=
H\left(\frac1B\sum_b p_b\right)
-
\frac1B\sum_b H(p_b).
\]

This approximates epistemic disagreement. It should be calculated from an actual ensemble or posterior draws.

## 5.3 Calibration

A probability label requires evaluation using:

- Brier score;
- log loss;
- calibration curve;
- calibration intercept/slope;
- reliability by spatial and temporal strata.

If calibration is not evaluated, display a relative score rather than a probability.

---

# 6. Route objectives

No single objective fits every product mode.

## 6.1 Likely Encounter

For target set \(S^*\):

\[
U_{likely}(R)
=
\sum_{s\in S^*}
w_s f(P_s(R))
-
\alpha T(R).
\]

## 6.2 Species diversity

A simple expected richness approximation:

\[
U_{rich}(R)
=
\sum_s P_s(R).
\]

To avoid rewarding many nearly identical common species, apply guild or phylogenetic diversity.

## 6.3 Expected but under-documented

\[
U_{gap}(R)
=
\sum_{s,a\in R}
w_s
\psi_s(a,t)
[1-C_s(a,t)].
\]

## 6.4 Scientific uncertainty

\[
U_{unc}(R)
=
\sum_{s,a\in R}
w_s
QBC_s(a,t)
[1-C_s(a,t)].
\]

More rigorous variants estimate expected reduction in held-out loss or posterior variance.

## 6.5 Hard-to-detect opportunity

\[
U_{hard}(R)
=
\sum_{s,i}
w_s
\psi_s(i,t)
\Delta p_s^{det}(\tau_i)
V_s,
\]

where \(V_s\) describes the value of resolving the target and \(\Delta p^{det}\) is the marginal detection gain from additional observation time.

## 6.6 Personal novelty

\[
U_{novel}(R,u)
=
\sum_s
P_s(R)
[1-Familiarity(s,u)]
Learnability(s,u).
\]

## 6.7 Scientific contribution on an existing journey

\[
U_{science}(R)
=
\sum_{s,a\in R}
w_s I_s(a)
P(\text{valid observation}\mid a,u).
\]

This introduces completion and protocol validity rather than assuming every recommendation becomes data.

---

# 7. Comfort, accessibility, and risk

## 7.1 Environmental exposure

For heat \(H(x,t)\), noise \(N(x,t)\), and air pollution \(A(x,t)\):

\[
Exposure(R)
=
\int_R
[
\eta_H H(x,t)
+
\eta_N N(x,t)
+
\eta_A A(x,t)
]\,d\tau.
\]

Green-routing research has used environmental impedance on network edges; Sidetrack can treat ecological benefit and exposure cost symmetrically.

## 7.2 Accessibility constraints

Hard constraints may include:

- step-free;
- surface class;
- maximum grade;
- wheelchair-accessible transit;
- maximum continuous walking interval;
- verified access.

Unknown is not equivalent to accessible.

## 7.3 Robust duration

Let \(T(R,\omega)\) be uncertain route duration.

Chance constraint:

\[
P(T(R,\omega)\le B)\ge 1-\epsilon.
\]

Risk-sensitive objective:

\[
E[U(R)]
-
\rho\,CVaR_\alpha(T(R)-B).
\]

These are later research features, not MVP requirements.

---

# 8. Detour frontier

Let \(R_0\) be the fastest route and \(R_\Delta\) a route with at most \(\Delta\) additional minutes.

\[
V(\Delta)
=
\max_{R:T(R)\le T(R_0)+\Delta}
U(R).
\]

Marginal nature value:

\[
E(\Delta)
=
\frac{V(\Delta)-V(0)}{\Delta}.
\]

The product can identify the Pareto frontier and the knee point.

---

# 9. Multiobjective route menu

Objectives:

\[
\mathbf f(R)
=
[
-T(R),
U_{nature}(R),
U_{comfort}(R),
U_{science}(R),
U_{access}(R)
].
\]

Rather than collapse everything into one opaque scalar, generate Pareto-efficient routes and label representative choices.

An \(\varepsilon\)-constraint approach:

\[
\max U_{nature}(R)
\]

subject to:

\[
T(R)\le B,
\quad
Heat(R)\le h,
\quad
Access(R)=true.
\]

---

# 10. Optimization approaches

## MVP heuristic

1. generate reachable candidate set;
2. start at origin;
3. greedily add the action with greatest marginal reward per added minute;
4. evaluate both new stop and duration extension;
5. apply 2-opt or local reorder;
6. verify exact provider route;
7. generate several routes using different objective presets.

## Small exact benchmark

Use CP-SAT or MIP for small candidate sets to estimate heuristic optimality gaps.

## Orienteering

Point-to-point and loop problems are variants of orienteering with:

- set rewards;
- time budgets;
- duration decisions;
- route-edge rewards;
- return constraints;
- optional time windows.

## Rust threshold

A Rust implementation becomes justified when a benchmark demonstrates that Python optimization—not routing APIs, raster reads, or model prediction—is the dominant latency.

---

# 11. Limited adaptivity

A fully adaptive route replans after every observation. That may be disruptive.

Compare:

- zero replans;
- one midpoint replan;
- two rounds;
- full replan.

Limited-adaptivity research finds that a small number of adaptive rounds can recover much of the value of full adaptivity in informative path planning. Sidetrack should default to zero or one replan.

---

# 12. Preference learning

A user may rank route alternatives. Let latent user utility be:

\[
U_u(R)=\theta_u^\top \phi(R),
\]

where features include time, diversity, shade, novelty, difficulty, and science.

Pairwise comparison:

\[
P(R_a \succ R_b)
=
\sigma[
\theta_u^\top(\phi(R_a)-\phi(R_b))
].
\]

This is a future feature. Explicit controls remain necessary for accessibility and safety even when preferences are learned.

---

# 13. Research validation

### Historical replay

Train through time \(t\), select hidden candidate observations in \(t+1\), reveal selected outcomes, refit, and evaluate on an untouched reference set.

### Route validation

Compare predicted and actual:

- travel time;
- completion;
- species detections;
- protocol validity;
- user burden.

### Field study

Randomize route presentation or route objective only when participants understand the study and the design is ethically approved where required.

---

# 14. Mathematical guardrails

- Do not call an objective submodular without proof or explicit conditions.
- Do not call standardized Euclidean distance Mahalanobis.
- Do not display QBC as encounter probability.
- Do not treat presence-only records as non-detections.
- Do not count one shared checklist multiple times.
- Do not precompute a duration-dependent reward and then change duration without recomputing it.
- Do not multiply the same coverage or duration factor into the objective twice without a justified model.
- Do not evaluate a policy using the same objective it directly optimized and call that ecological superiority.

---

# 15. Field-pack selection is not ecological prediction

The route field pack selects a small educational subset from the route's supported taxa. It must not feed media availability back into ecological presence or encounter probabilities.

For taxon \(s\) on route \(R\), define an educational selection value:

\[
G_s(R,u)
=
\alpha_1\,\text{route relevance}
+\alpha_2\,\text{educational distinctiveness}
+\alpha_3\,\text{habitat representation}
+\alpha_4\,\text{audience suitability}
+\alpha_5\,\text{media completeness}
-\alpha_6\,\text{cognitive overlap}
-\alpha_7\,\text{sensitivity risk}.
\]

Select a small pack \(F\) subject to:

\[
|F| \le K_u,
\]

where \(K_u\) depends on observer experience. Add diversity constraints so the pack does not contain six nearly identical species/cues.

Important guardrail:

> Media completeness may affect which species the application teaches, but it must not increase the underlying predicted ecological opportunity.

A taxon lacking licensed media remains part of route ecology and receives a text-only fallback.

# 16. Duration-aware product rewards

A static site score is insufficient when the objective depends on observation duration. Define a reward protocol:

\[
r_m(i, \tau; s,t,o)
\]

for mode \(m\), site or segment \(i\), duration \(\tau\), taxon \(s\), time \(t\), and observer profile \(o\).

Examples:

### Likely encounter

\[
r_{LE}(i,\tau)=P(\text{encounter at }i\mid\tau).
\]

### Under-documented

\[
r_{UD}(i,\tau)=\psi_{s,i,t}[1-C_{s,i,t}]\,M(\tau).
\]

### Scientific uncertainty

\[
r_{U}(i,\tau)=\operatorname{QBC}_{s,i,t}\,V(\tau)[1-C_{s,i,t}].
\]

### Hard-to-detect

\[
r_{HD}(i,\tau)=\psi_{s,i,t}\,\Delta p_{detect}(\tau,\tau+\Delta)\,w_s.
\]

The optimizer evaluates the reward at each proposed duration. Do not precompute one duration-dependent score and then multiply it by a second duration curve.

---

# 17. Route-local occurrence evidence mathematics

The Sprint 13.75 Route Evidence Layer introduces non-conflated mathematical surfaces for occurrence evidence reported around a route corridor.

## 17.1 Metric point-to-route spatial distance

Given route LineString $R$ and occurrence $i$ at projected metric coordinate $x_i$:

\[
d_i = d(x_i, R) = \min_{x \in R} \| x_i - x \|.
\]

Project route $R$ and occurrence point $x_i$ into a local metric projection (e.g., AEQD or local State Plane) prior to distance calculation.

## 17.2 Positional uncertainty propagation

For occurrence $i$ with source-reported coordinate uncertainty radius $u_i$ (e.g., GBIF `coordinateUncertaintyInMeters`):

\[
\sigma_i^2 = \sigma_0^2 + u_i^2,
\]

where $\sigma_0$ is the baseline spatial scale parameter (e.g., 250 m).

The spatial decay kernel is:

\[
K_d(i) = \exp\left( - \frac{d_i^2}{2\sigma_i^2} \right).
\]

> **Privacy Guardrail:** Do not apply uncertainty propagation to infer precision for intentionally randomized/obscured coordinates (e.g., iNaturalist 0.2° × 0.2° geoprivacy cells). Obscured records bypass spatial distance kernels and display as broad-area indicators only.

## 17.3 Temporal and seasonal kernels

### Temporal decay for recent evidence ($\Delta t_i$ days since report):

\[
K_t(i) = \exp\left( - \frac{\Delta t_i}{\tau} \right),
\]

where half-life parameter $\tau \in \{3, 7, 14, 30\}$ days.

Provisional recent evidence index:

\[
E_s^{\text{recent}}(R, t) = \sum_{i \in O_s} q_i K_d(i) K_t(i),
\]

where $q_i$ is record quality weighting.

### Seasonal historical evidence (cyclic week distance $d_T$):

\[
d_T(w_1, w_2) = \min\left( |w_1 - w_2|, 52 - |w_1 - w_2| \right).
\]

Seasonal kernel ($h \in \{1, 2, 4\}$ weeks):

\[
K_{\text{season}}(i) = \exp\left[ - \frac{d_T(w_i, w)^2}{2h^2} \right].
\]

Seasonal historical route evidence index:

\[
E_s^{\text{seasonal}}(R, w) = \sum_{i \in O_s} q_i K_d(i) K_{\text{season}}(i).
\]

## 17.4 Beta-Binomial shrinkage checklist detection rate

For qualifying complete effort checklists $N$ within corridor/season, where $D_s$ checklists detect species $s$:

\[
\tilde{r}_s = \frac{D_s + \alpha}{N + \alpha + \beta},
\]

with weak uniform prior $\alpha = \beta = 1$. This prevents 1 detection / 1 checklist from returning misleading 100% rates.

## 17.5 Observer-effort corrected relative evidence index

Target-Group Background (TGB) sampling correction:

\[
E_s^{\text{relative}}(x) = \frac{\operatorname{KDE}_s(x)}{\operatorname{KDE}_{\text{all bird records}}(x) + \epsilon}.
\]

This measures whether species $s$ is reported frequently relative to total observer effort, mitigating observer bias toward popular parks.

## 17.6 Integrated species distribution model (ISDM) dual likelihood

- **Structured effort checklists (EBD/SED):**
  \[
  Y_{s,j}^{\text{EBD}} \sim \text{Bernoulli}\left( p_{s,j}^{\text{enc}} \right)
  \]
- **Presence-only opportunistic data (GBIF / iNaturalist):**
  \[
  N_{s,p}^{\text{PO}} \sim \text{Poisson}\left( \lambda_s(x,t) \, b_p(x,t) \right),
  \]
  where $b_p(x,t)$ models platform-specific sampling bias.

## 17.7 Route corridor evidence integral

\[
A_s(R) = \frac{1}{L(R)} \int_R e_s(x) \, dl.
\]

Differentiates a route with one isolated 100 m hotspot from a route with sustained moderate evidence across a 2 km corridor.

## 17.8 Model–evidence disagreement metric

\[
D_s(x,t) = z\left( E_s^{\text{recent}} \right) - z\left( P_s^{\text{model}} \right).
\]

Quantifies spatial divergence between recent citizen-science reports and model expectation for research search modes.

## 17.9 Under-documented route gap search

\[
U_{\text{gap}}(R) = \frac{1}{L(R)} \int_R \text{Opportunity}_s(x,t) \, [1 - C(x,t)] \, dl,
\]

where $C(x,t)$ measures observation coverage.

